"""
Assign images to content using multiple providers and semantic matching
Based on ai_shh_growth_kit_v3/image_aggregator/assign_images.py
"""
import json
import yaml
from pathlib import Path
from typing import Dict, List

from .providers_openverse import search as ov_search
from .providers_commons import search as wm_search
from .semantic_rank import rank_images
from .cache import (
    dl, write_meta, load_cached_results, save_cached_results,
    filter_unique_images, is_url_used
)
from .build_info_card import make_info_card, make_category_card, make_compatibility_card


class ImageAssigner:
    """Assigns relevant images to content using semantic matching"""
    
    def __init__(self, config_path: str = "configs/image_config.yml"):
        """Initialize with configuration"""
        self.config = self._load_config(config_path)
        
    def _load_config(self, config_path: str) -> Dict:
        """Load image configuration"""
        default_config = {
            'providers': {
                'openverse': True,
                'wikimedia': True
            },
            'semantic_threshold': 0.35,  # Increased from 0.28 for better precision
            'download_dir': 'static/images',
            'formats': ['webp'],
            'min_hero_size': [1280, 720],
            'min_inline_size': [960, 540],
            'fallback_threshold': 0.25,  # Lower threshold for fallback scenarios
            'min_candidates': 3  # Minimum candidates required before fallback
        }
        
        try:
            config_file = Path(config_path)
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    user_config = yaml.safe_load(f) or {}
                # Merge with defaults
                default_config.update(user_config)
        except Exception as e:
            print(f"Config load error, using defaults: {e}")
        
        return default_config
    
    def assign(self, keyword: str, entities: Dict, slug: str) -> Dict:
        """
        Assign images for given keyword and entities
        
        Args:
            keyword: Primary search keyword
            entities: Entity metadata (category, protocol, use_case, etc.)
            slug: Content slug for file organization
            
        Returns:
            Dict with 'hero' and 'inline' image paths
        """
        # Build search query
        query = self._build_query(entities, keyword)
        
        # Check cache first
        cache_key = f"{query}_{slug}"
        cached_results = load_cached_results(cache_key)
        
        if cached_results:
            print(f"Using cached results for: {query}")
            return cached_results
        
        # Search multiple providers
        candidates = self._search_providers(query)
        
        if not candidates:
            print(f"No image candidates found for: {query}")
            return self._create_fallback_result(keyword, entities, slug)
        
        # Rank by semantic similarity with higher precision threshold
        primary_threshold = self.config.get('semantic_threshold', 0.35)
        ranked = rank_images(query, candidates, primary_threshold)

        # If not enough high-quality matches, try with fallback threshold
        if len(ranked) < self.config.get('min_candidates', 3):
            fallback_threshold = self.config.get('fallback_threshold', 0.25)
            print(f"Only {len(ranked)} images above {primary_threshold:.2f}, trying fallback threshold {fallback_threshold:.2f}")
            ranked = rank_images(query, candidates, fallback_threshold)

        if not ranked:
            print(f"No images above threshold for: {query}")
            return self._create_fallback_result(keyword, entities, slug)

        # Apply URL deduplication to ensure uniqueness across the site
        unique_ranked = filter_unique_images(ranked, max_images=10)

        if not unique_ranked:
            print(f"No unique images available for: {query}")
            return self._create_fallback_result(keyword, entities, slug)

        print(f"Using {len(unique_ranked)} unique images out of {len(ranked)} ranked candidates")

        # Download and organize images using unique candidates
        result = self._download_images(unique_ranked, keyword, entities, slug)
        
        # Cache results
        save_cached_results(cache_key, result)
        
        return result
    
    def _build_query(self, entities: Dict, keyword: str) -> str:
        """Build unique search query from entities and keyword"""
        query_parts = [keyword]

        # Add protocol information for specificity
        protocol = entities.get('protocol', '')
        if protocol and protocol.lower() not in keyword.lower():
            query_parts.append(protocol)

        # Add use case for context differentiation
        use_case = entities.get('use_case', '')
        if use_case and len(use_case) < 30:  # Avoid overly long descriptions
            # Clean and add use case
            clean_use_case = use_case.replace('_', ' ').strip()
            if clean_use_case and clean_use_case.lower() not in keyword.lower():
                query_parts.append(clean_use_case)

        # Add category only if it adds meaningful differentiation
        category = entities.get('category', '').replace('-', ' ')
        if category and category not in keyword.lower():
            # Only add category for broad keywords that need more specificity
            keyword_words = set(keyword.lower().split())
            generic_words = {'smart', 'home', 'device', 'gadget', 'product'}
            if len(keyword_words.intersection(generic_words)) > 0:
                query_parts.append(category)

        # Join parts with space, limit total length for API compatibility
        full_query = ' '.join(query_parts)

        # Limit query length to avoid API issues (max ~100 chars)
        if len(full_query) > 100:
            # Keep keyword + most important modifier
            if len(query_parts) > 2:
                full_query = f"{keyword} {query_parts[1]}"
            else:
                full_query = keyword

        return full_query.strip()
    
    def _search_providers(self, query: str) -> List[Dict]:
        """Search all enabled image providers"""
        candidates = []
        
        # Search Openverse
        if self.config['providers'].get('openverse', True):
            try:
                ov_results = ov_search(query, limit=5)
                candidates.extend(ov_results)
                print(f"Openverse: {len(ov_results)} results for '{query}'")
            except Exception as e:
                print(f"Openverse search error: {e}")
        
        # Search Wikimedia Commons
        if self.config['providers'].get('wikimedia', True):
            try:
                wm_results = wm_search(query, limit=10)
                # Filter None results
                wm_results = [r for r in wm_results if r is not None]
                candidates.extend(wm_results)
                print(f"Wikimedia: {len(wm_results)} results for '{query}'")
            except Exception as e:
                print(f"Wikimedia search error: {e}")
        
        return candidates
    
    def _download_images(self, ranked: List[Dict], keyword: str, entities: Dict, slug: str) -> Dict:
        """Download and organize selected images"""
        category = entities.get('category', 'general')
        out_dir = Path(self.config.get('download_dir', 'static/images')) / category / slug
        
        result = {
            'hero': '',
            'inline': [],
            'metadata': {
                'keyword': keyword,
                'query': self._build_query(entities, keyword),
                'total_candidates': len(ranked),
                'selected_count': 0
            }
        }
        
        # Select hero image (first/best match)
        if ranked:
            hero_meta = ranked[0]
            hero_path = dl(hero_meta['url'], out_dir, 'hero')
            if hero_path:
                result['hero'] = hero_path
                result['metadata']['hero_score'] = hero_meta.get('similarity_score', 0)
                
                # Write hero metadata
                hero_metadata = {
                    'source': hero_meta.get('source'),
                    'url': hero_meta.get('url'),
                    'license': hero_meta.get('license'),
                    'creator': hero_meta.get('creator'),
                    'title': hero_meta.get('title'),
                    'similarity_score': hero_meta.get('similarity_score'),
                    'alt_text': self._generate_alt_text(entities, hero_meta)
                }
                write_meta(hero_path, hero_metadata)
                result['metadata']['selected_count'] += 1
        
        # Select inline images (up to 3 additional)
        for i, meta in enumerate(ranked[1:4], start=1):
            inline_path = dl(meta['url'], out_dir, f'inline_{i}')
            if inline_path:
                result['inline'].append(inline_path)
                
                # Write inline metadata
                inline_metadata = {
                    'source': meta.get('source'),
                    'url': meta.get('url'),
                    'license': meta.get('license'),
                    'creator': meta.get('creator'),
                    'title': meta.get('title'),
                    'similarity_score': meta.get('similarity_score'),
                    'alt_text': self._generate_alt_text(entities, meta)
                }
                write_meta(inline_path, inline_metadata)
                result['metadata']['selected_count'] += 1
        
        return result
    
    def _generate_alt_text(self, entities: Dict, image_meta: Dict) -> str:
        """Generate SEO-friendly alt text for image"""
        parts = []
        
        # Add category
        category = entities.get('category', '').replace('-', ' ')
        if category:
            parts.append(category)
        
        # Add specific technology/protocol  
        protocol = entities.get('protocol', '')
        if protocol:
            parts.append(protocol)
        
        # Add use case context
        use_case = entities.get('use_case', '')
        if use_case:
            parts.append(use_case)
        
        # Use image title as fallback
        title = image_meta.get('title', '')
        if title and not parts:
            # Clean and limit title
            title = title.strip()[:50]
            if title:
                parts.append(title)
        
        # Ensure we have some alt text
        if not parts:
            parts.append('smart home device')
        
        alt_text = ' — '.join(parts).strip()
        
        # Ensure length is between 8-120 characters for SEO
        if len(alt_text) < 8:
            alt_text += ' for home automation'
        elif len(alt_text) > 120:
            alt_text = alt_text[:117] + '...'
        
        return alt_text
    
    def _create_fallback_result(self, keyword: str, entities: Dict, slug: str) -> Dict:
        """Create fallback result with generated info cards when no images are found"""
        category = entities.get('category', 'general')
        out_dir = Path(self.config.get('download_dir', 'static/images')) / category / slug
        
        result = {
            'hero': '',
            'inline': [],
            'metadata': {
                'keyword': keyword,
                'query': self._build_query(entities, keyword),
                'total_candidates': 0,
                'selected_count': 0,
                'fallback': True,
                'generated_cards': 0
            }
        }
        
        try:
            # Generate hero card based on category
            hero_features = self._get_category_features(entities)
            if hero_features:
                hero_path = make_category_card(
                    category=entities.get('category', keyword),
                    features=hero_features,
                    output_path=str(out_dir / 'hero_generated.webp')
                )
                if hero_path:
                    result['hero'] = hero_path
                    result['metadata']['generated_cards'] += 1
                    
                    # Write metadata for generated hero
                    hero_metadata = {
                        'source': 'generated',
                        'type': 'category_card',
                        'category': entities.get('category', 'general'),
                        'alt_text': self._generate_alt_text(entities, {'title': f'{category} overview'})
                    }
                    write_meta(hero_path, hero_metadata)
            
            # Generate compatibility card as inline image
            protocols = self._extract_protocols(entities, keyword)
            if protocols:
                compat_path = make_compatibility_card(
                    device_name=keyword.title(),
                    protocols=protocols,
                    output_path=str(out_dir / 'inline_1_generated.webp')
                )
                if compat_path:
                    result['inline'].append(compat_path)
                    result['metadata']['generated_cards'] += 1
                    
                    # Write metadata for compatibility card
                    compat_metadata = {
                        'source': 'generated',
                        'type': 'compatibility_card',
                        'protocols': protocols,
                        'alt_text': f'{keyword} compatibility guide'
                    }
                    write_meta(compat_path, compat_metadata)
            
            # Generate generic info card if we still need more images
            if len(result['inline']) < 2:
                generic_features = [
                    "Setup and configuration guide",
                    "Compatible with major smart home platforms",
                    "Energy efficient operation",
                    "Remote monitoring and control"
                ]
                
                generic_path = make_info_card(
                    title=f"{keyword.title()} Guide",
                    bullet_points=generic_features,
                    output_path=str(out_dir / 'inline_2_generated.webp')
                )
                if generic_path:
                    result['inline'].append(generic_path)
                    result['metadata']['generated_cards'] += 1
                    
                    # Write metadata
                    generic_metadata = {
                        'source': 'generated',
                        'type': 'info_card',
                        'alt_text': f'{keyword} setup and features guide'
                    }
                    write_meta(generic_path, generic_metadata)
                    
        except Exception as e:
            print(f"Fallback card generation error: {e}")
        
        # Update selected count
        result['metadata']['selected_count'] = (
            (1 if result['hero'] else 0) + len(result['inline'])
        )
        
        return result
    
    def _get_category_features(self, entities: Dict) -> List[str]:
        """Get relevant features for category card"""
        category = entities.get('category', '').lower()
        
        category_features = {
            'smart-plugs': [
                "Remote on/off control via smartphone app",
                "Energy monitoring and usage tracking", 
                "Voice control with Alexa/Google Assistant",
                "Scheduling and timer functionality",
                "Away mode for security automation"
            ],
            'smart-cameras': [
                "HD video recording and live streaming",
                "Motion detection with instant alerts",
                "Night vision for 24/7 monitoring",
                "Two-way audio communication",
                "Cloud and local storage options"
            ],
            'smart-lights': [
                "Dimming and brightness control",
                "Color temperature adjustment",
                "Voice control integration",
                "Scheduling and automation scenes",
                "Energy efficient LED technology"
            ],
            'robot-vacuums': [
                "Automated cleaning schedules",
                "Smart mapping and navigation",
                "Multi-surface cleaning capability",
                "Self-charging and resume cleaning",
                "App control and monitoring"
            ]
        }
        
        return category_features.get(category, [
            "Smart home automation features",
            "Mobile app remote control",
            "Voice assistant compatibility",
            "Energy efficient operation",
            "Easy setup and configuration"
        ])
    
    def _extract_protocols(self, entities: Dict, keyword: str) -> List[str]:
        """Extract relevant protocols from entities and keyword"""
        protocols = []
        
        # Check entities first
        if 'protocol' in entities and entities['protocol']:
            protocols.append(entities['protocol'])
        
        # Extract from keyword
        keyword_lower = keyword.lower()
        common_protocols = ['wifi', 'zigbee', 'z-wave', 'matter', 'thread', 'bluetooth']
        
        for protocol in common_protocols:
            if protocol in keyword_lower and protocol not in protocols:
                protocols.append(protocol.title())
        
        # Default protocols if none found
        if not protocols:
            protocols = ['WiFi', 'Matter']  # Most common modern protocols
            
        return protocols[:3]  # Limit to 3 protocols


# Global instance for convenience
_assigner = None


def assign(keyword: str, entities: Dict, slug: str) -> Dict:
    """
    Convenience function for assigning images
    
    Args:
        keyword: Primary keyword
        entities: Entity metadata
        slug: Content slug
        
    Returns:
        Image assignment result
    """
    global _assigner
    if _assigner is None:
        _assigner = ImageAssigner()
    
    return _assigner.assign(keyword, entities, slug)