#!/usr/bin/env python3
"""
Comprehensive Image Manager Module - v2 Enhanced
Integrates with external APIs, local caching, quality control, and usage tracking
"""

import os
import sys
import json
import requests
import hashlib
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import yaml

# Add project root to path for configuration access
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

class ComprehensiveImageManager:
    """
    Complete image management system with API integration, caching, and quality control
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize with configuration"""
        self.config = self._load_config(config_path)
        self.cache_dir = Path(self.config.get('cache', {}).get('cache_directory', 'data/image_cache'))
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Usage tracking
        self.usage_file = self.cache_dir / 'image_usage.json'
        self.usage_data = self._load_usage_data()
        
        # API configurations
        self.apis = self.config.get('apis', {})
        self.quality_config = self.config.get('quality', {})
        self.compliance_config = self.config.get('compliance', {})
        
        # Category mapping
        self.categories = self.config.get('categories', {})
        
        # Initialize API clients
        self._init_api_clients()
        
        print(f"✅ ImageManager initialized with {len(self.apis)} API sources")
    
    def _load_config(self, config_path: Optional[str] = None) -> Dict:
        """Load configuration from YAML file"""
        if not config_path:
            config_path = project_root / 'image_config.yml'
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                return config
        except Exception as e:
            print(f"⚠️ Failed to load config, using defaults: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """Default configuration if config file is unavailable"""
        return {
            'quality': {'min_width': 800, 'min_height': 600, 'max_usage_count': 3},
            'cache': {'cache_directory': 'data/image_cache', 'cache_duration_days': 30},
            'apis': {'unsplash': {'enabled': False}, 'pexels': {'enabled': False}},
            'categories': {'smart_plugs': 'smart-plugs', 'smart_bulbs': 'smart-bulbs'},
            'compliance': {'allowed_licenses': ['CC0', 'CC BY 4.0']}
        }
    
    def _init_api_clients(self):
        """Initialize API clients based on configuration"""
        self.api_clients = {}
        
        # Unsplash API
        if self.apis.get('unsplash', {}).get('enabled'):
            api_key = os.getenv('UNSPLASH_API_KEY')
            if api_key:
                self.api_clients['unsplash'] = {
                    'base_url': 'https://api.unsplash.com',
                    'headers': {'Authorization': f'Client-ID {api_key}'},
                    'rate_limit': self.apis['unsplash'].get('rate_limit', 50)
                }
        
        # Pexels API
        if self.apis.get('pexels', {}).get('enabled'):
            api_key = os.getenv('PEXELS_API_KEY')
            if api_key:
                self.api_clients['pexels'] = {
                    'base_url': 'https://api.pexels.com/v1',
                    'headers': {'Authorization': api_key},
                    'rate_limit': self.apis['pexels'].get('rate_limit', 200)
                }
        
        # Pixabay API
        if self.apis.get('pixabay', {}).get('enabled'):
            api_key = os.getenv('PIXABAY_API_KEY')
            if api_key:
                self.api_clients['pixabay'] = {
                    'base_url': 'https://pixabay.com/api',
                    'api_key': api_key,
                    'rate_limit': self.apis['pixabay'].get('rate_limit', 5000)
                }
        
        print(f"🔌 Initialized {len(self.api_clients)} API clients")
    
    def _load_usage_data(self) -> Dict:
        """Load image usage tracking data"""
        try:
            if self.usage_file.exists():
                with open(self.usage_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"⚠️ Failed to load usage data: {e}")
        
        return {'images': {}, 'last_updated': datetime.now().isoformat()}
    
    def _save_usage_data(self):
        """Save image usage tracking data"""
        try:
            self.usage_data['last_updated'] = datetime.now().isoformat()
            with open(self.usage_file, 'w', encoding='utf-8') as f:
                json.dump(self.usage_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️ Failed to save usage data: {e}")
    
    def search_and_assign(self, keyword: str, category: str, needs: Dict[str, int], 
                         why_selected: Dict[str, str] = None) -> Dict[str, Any]:
        """
        Main function to search and assign images intelligently
        
        Args:
            keyword: Search keyword
            category: Product category 
            needs: Dict specifying image needs (e.g., {'hero': 1, 'inline': 3})
            why_selected: Context for why these images were selected
        
        Returns:
            Dict containing success status, assigned images, and metadata
        """
        try:
            print(f"🎯 Starting intelligent image assignment for '{keyword}' (category: {category})")
            
            # Step 1: Try API-based search
            api_results = self._search_external_apis(keyword, category, needs)
            
            # Step 2: Check local cache and deduplication
            filtered_results = self._apply_quality_and_deduplication(api_results, keyword)
            
            # Step 3: Generate fallback images if needed
            final_results = self._ensure_sufficient_images(filtered_results, keyword, category, needs)
            
            # Step 4: Track usage and update metadata
            self._track_image_usage(final_results, keyword, category, why_selected)
            
            # Step 5: Format results for return
            assigned_images = self._format_assignment_results(final_results, needs)
            
            success = len(assigned_images) > 0
            
            result = {
                'success': success,
                'assigned_images': assigned_images,
                'total_images': sum(len(images) for images in assigned_images.values()),
                'sources_used': list(set(img.get('source', 'local') for images in assigned_images.values() for img in images)),
                'quality_score': self._calculate_overall_quality(assigned_images),
                'compliance_check': self._verify_compliance(assigned_images),
                'metadata': {
                    'keyword': keyword,
                    'category': category,
                    'timestamp': datetime.now().isoformat(),
                    'why_selected': why_selected or {}
                }
            }
            
            print(f"✅ Image assignment complete: {result['total_images']} images from {len(result['sources_used'])} sources")
            return result
            
        except Exception as e:
            print(f"❌ Image assignment failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'assigned_images': {},
                'fallback_reason': 'Exception during processing'
            }
    
    def _search_external_apis(self, keyword: str, category: str, needs: Dict[str, int]) -> List[Dict]:
        """Search external APIs for images"""
        all_results = []
        total_needed = sum(needs.values())
        
        for api_name, client_config in self.api_clients.items():
            try:
                print(f"🔍 Searching {api_name} for '{keyword}'...")
                
                if api_name == 'unsplash':
                    results = self._search_unsplash(keyword, total_needed, client_config)
                elif api_name == 'pexels':
                    results = self._search_pexels(keyword, total_needed, client_config)
                elif api_name == 'pixabay':
                    results = self._search_pixabay(keyword, total_needed, client_config)
                else:
                    continue
                
                all_results.extend(results)
                print(f"📸 Found {len(results)} images from {api_name}")
                
            except Exception as e:
                print(f"⚠️ {api_name} search failed: {e}")
                continue
        
        return all_results
    
    def _search_unsplash(self, keyword: str, count: int, client_config: Dict) -> List[Dict]:
        """Search Unsplash API"""
        url = f"{client_config['base_url']}/search/photos"
        params = {
            'query': f"{keyword} smart home technology",
            'per_page': min(count * 2, 30),  # Get extra for filtering
            'orientation': 'landscape'
        }
        
        response = requests.get(url, headers=client_config['headers'], params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        results = []
        
        for photo in data.get('results', []):
            results.append({
                'source': 'unsplash',
                'id': photo['id'],
                'url': photo['urls']['regular'],
                'thumbnail_url': photo['urls']['small'],
                'alt_description': photo.get('alt_description', f"{keyword} smart home device"),
                'width': photo['width'],
                'height': photo['height'],
                'author': photo['user']['name'],
                'author_url': photo['user']['links']['html'],
                'download_url': photo['links']['download'],
                'license': 'Unsplash License',
                'quality_score': self._calculate_quality_score(photo['width'], photo['height'], keyword)
            })
        
        return results
    
    def _search_pexels(self, keyword: str, count: int, client_config: Dict) -> List[Dict]:
        """Search Pexels API"""
        url = f"{client_config['base_url']}/search"
        params = {
            'query': f"{keyword} smart home",
            'per_page': min(count * 2, 80),
            'orientation': 'landscape'
        }
        
        response = requests.get(url, headers=client_config['headers'], params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        results = []
        
        for photo in data.get('photos', []):
            results.append({
                'source': 'pexels',
                'id': photo['id'],
                'url': photo['src']['large'],
                'thumbnail_url': photo['src']['medium'],
                'alt_description': f"{keyword} - {photo.get('alt', 'Smart home device')}",
                'width': photo['width'],
                'height': photo['height'],
                'author': photo['photographer'],
                'author_url': photo['photographer_url'],
                'license': 'Pexels License',
                'quality_score': self._calculate_quality_score(photo['width'], photo['height'], keyword)
            })
        
        return results
    
    def _search_pixabay(self, keyword: str, count: int, client_config: Dict) -> List[Dict]:
        """Search Pixabay API"""
        url = client_config['base_url']
        params = {
            'key': client_config['api_key'],
            'q': f"{keyword} smart home technology",
            'per_page': min(count * 2, 200),
            'orientation': 'horizontal',
            'image_type': 'photo',
            'safesearch': 'true'
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        results = []
        
        for photo in data.get('hits', []):
            results.append({
                'source': 'pixabay',
                'id': photo['id'],
                'url': photo['webformatURL'],
                'thumbnail_url': photo['previewURL'],
                'alt_description': f"{keyword} - {photo.get('tags', 'Smart home device')}",
                'width': photo['imageWidth'],
                'height': photo['imageHeight'],
                'author': photo['user'],
                'license': 'Pixabay License',
                'quality_score': self._calculate_quality_score(photo['imageWidth'], photo['imageHeight'], keyword)
            })
        
        return results
    
    def _calculate_quality_score(self, width: int, height: int, keyword: str) -> float:
        """Calculate quality score for an image"""
        score = 0.0
        
        # Dimension score (0.4 weight)
        min_width = self.quality_config.get('min_width', 800)
        min_height = self.quality_config.get('min_height', 600)
        
        if width >= min_width and height >= min_height:
            score += 0.4
        else:
            score += 0.4 * min(width/min_width, height/min_height)
        
        # Aspect ratio score (0.3 weight)
        aspect_ratio = width / height if height > 0 else 0
        ideal_ratio = 16/9  # Ideal for web content
        ratio_diff = abs(aspect_ratio - ideal_ratio) / ideal_ratio
        score += 0.3 * max(0, 1 - ratio_diff)
        
        # Resolution score (0.3 weight)
        total_pixels = width * height
        if total_pixels >= 1920 * 1080:  # Full HD+
            score += 0.3
        elif total_pixels >= 1280 * 720:  # HD
            score += 0.2
        else:
            score += 0.1
        
        return min(1.0, score)
    
    def _apply_quality_and_deduplication(self, images: List[Dict], keyword: str) -> List[Dict]:
        """Apply quality filtering and deduplication"""
        if not images:
            return images
        
        # Quality filtering
        min_quality = self.quality_config.get('quality_threshold', 0.6)
        quality_filtered = [img for img in images if img.get('quality_score', 0) >= min_quality]
        
        print(f"🎯 Quality filter: {len(quality_filtered)}/{len(images)} images passed (threshold: {min_quality})")
        
        # Deduplication by usage frequency
        max_usage = self.quality_config.get('max_usage_count', 3)
        deduplicated = []
        
        for img in quality_filtered:
            img_id = img.get('id') or img.get('url')
            usage_count = self.usage_data['images'].get(img_id, {}).get('usage_count', 0)
            
            if usage_count < max_usage:
                img['current_usage'] = usage_count
                deduplicated.append(img)
        
        print(f"🔄 Deduplication: {len(deduplicated)}/{len(quality_filtered)} images available (max usage: {max_usage})")
        
        # Sort by quality score and usage (prefer less used, higher quality)
        deduplicated.sort(key=lambda x: (x.get('quality_score', 0) - x.get('current_usage', 0) * 0.1), reverse=True)
        
        return deduplicated
    
    def _ensure_sufficient_images(self, images: List[Dict], keyword: str, category: str, needs: Dict[str, int]) -> List[Dict]:
        """Ensure sufficient images, generate fallbacks if needed"""
        total_needed = sum(needs.values())
        
        if len(images) >= total_needed:
            return images[:total_needed]
        
        # Generate fallback infographic images
        print(f"🎨 Generating {total_needed - len(images)} fallback images...")
        
        for i in range(total_needed - len(images)):
            fallback_img = self._generate_infographic(keyword, category, f"infographic_{i+1}")
            if fallback_img:
                images.append(fallback_img)
        
        return images
    
    def _generate_infographic(self, keyword: str, category: str, suffix: str = "") -> Optional[Dict]:
        """Generate fallback infographic image using PIL"""
        try:
            # Configuration from YAML
            fallback_config = self.config.get('fallback', {})
            width, height = fallback_config.get('default_size', [1280, 720])
            bg_color = tuple(fallback_config.get('background_color', [255, 255, 255]))
            text_color = tuple(fallback_config.get('text_color', [0, 0, 0]))
            
            # Create image
            img = Image.new('RGB', (width, height), bg_color)
            draw = ImageDraw.Draw(img)
            
            # Try to load font, fallback to default if unavailable
            try:
                font_large = ImageFont.truetype("arial.ttf", fallback_config.get('font_size_large', 64))
                font_medium = ImageFont.truetype("arial.ttf", fallback_config.get('font_size_medium', 48))
            except:
                font_large = ImageFont.load_default()
                font_medium = ImageFont.load_default()
            
            # Draw title
            title_text = f"{keyword.title()}"
            title_bbox = draw.textbbox((0, 0), title_text, font=font_large)
            title_width = title_bbox[2] - title_bbox[0]
            title_x = (width - title_width) // 2
            draw.text((title_x, height//3), title_text, fill=text_color, font=font_large)
            
            # Draw subtitle
            subtitle_text = "Smart Home Technology Guide"
            subtitle_bbox = draw.textbbox((0, 0), subtitle_text, font=font_medium)
            subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
            subtitle_x = (width - subtitle_width) // 2
            draw.text((subtitle_x, height//2), subtitle_text, fill=text_color, font=font_medium)
            
            # Save to cache
            filename = f"generated_{hashlib.md5(f'{keyword}_{category}_{suffix}'.encode()).hexdigest()[:8]}.png"
            filepath = self.cache_dir / filename
            img.save(filepath, 'PNG')
            
            return {
                'source': 'generated',
                'id': filename,
                'url': f'/images/cache/{filename}',
                'local_path': str(filepath),
                'alt_description': f"{keyword} guide infographic",
                'width': width,
                'height': height,
                'author': 'AI Smart Home Hub',
                'license': 'Generated Content',
                'quality_score': 0.7,  # Default quality for generated images
                'generated': True
            }
            
        except Exception as e:
            print(f"⚠️ Failed to generate infographic: {e}")
            return None
    
    def _track_image_usage(self, images: List[Dict], keyword: str, category: str, why_selected: Dict[str, str]):
        """Track image usage for deduplication"""
        for img in images:
            img_id = img.get('id') or img.get('url')
            
            if img_id not in self.usage_data['images']:
                self.usage_data['images'][img_id] = {
                    'usage_count': 0,
                    'first_used': datetime.now().isoformat(),
                    'categories_used': [],
                    'keywords_used': []
                }
            
            usage_info = self.usage_data['images'][img_id]
            usage_info['usage_count'] += 1
            usage_info['last_used'] = datetime.now().isoformat()
            
            if category not in usage_info['categories_used']:
                usage_info['categories_used'].append(category)
            
            if keyword not in usage_info['keywords_used']:
                usage_info['keywords_used'].append(keyword)
        
        self._save_usage_data()
    
    def _format_assignment_results(self, images: List[Dict], needs: Dict[str, int]) -> Dict[str, List[Dict]]:
        """Format images according to specified needs"""
        assigned = {}
        image_index = 0
        
        for need_type, count in needs.items():
            assigned[need_type] = []
            
            for _ in range(count):
                if image_index < len(images):
                    img = images[image_index]
                    
                    # Create optimized alt text based on need type
                    alt_text = self._generate_seo_alt_text(img, need_type)
                    
                    assigned[need_type].append({
                        'url': img['url'],
                        'alt': alt_text,
                        'source': img['source'],
                        'author': img.get('author', 'Unknown'),
                        'license': img.get('license', 'Unknown'),
                        'quality_score': img.get('quality_score', 0.0),
                        'width': img.get('width', 0),
                        'height': img.get('height', 0)
                    })
                    
                    image_index += 1
        
        return assigned
    
    def _generate_seo_alt_text(self, img: Dict, need_type: str) -> str:
        """Generate SEO-optimized alt text"""
        base_alt = img.get('alt_description', 'Smart home device')
        
        # Remove banned words from SEO config
        banned_words = self.config.get('seo', {}).get('banned_alt_words', [])
        for banned_word in banned_words:
            base_alt = base_alt.replace(banned_word, '')
        
        # Add context based on need type
        context_map = {
            'hero': 'overview and compatibility guide',
            'inline': 'key features and installation guide', 
            'comparison': 'comparison chart and specifications',
            'installation': 'setup and installation process'
        }
        
        context = context_map.get(need_type, 'smart home automation guide')
        
        # Ensure length constraints
        max_length = self.config.get('seo', {}).get('max_alt_length', 125)
        full_alt = f"{base_alt} {context}".strip()
        
        if len(full_alt) > max_length:
            full_alt = full_alt[:max_length-3] + "..."
        
        return full_alt
    
    def _calculate_overall_quality(self, assigned_images: Dict) -> float:
        """Calculate overall quality score for assigned images"""
        if not assigned_images:
            return 0.0
        
        total_score = 0.0
        total_images = 0
        
        for image_list in assigned_images.values():
            for img in image_list:
                total_score += img.get('quality_score', 0.0)
                total_images += 1
        
        return total_score / total_images if total_images > 0 else 0.0
    
    def _verify_compliance(self, assigned_images: Dict) -> Dict[str, Any]:
        """Verify compliance with license and quality requirements"""
        allowed_licenses = self.compliance_config.get('allowed_licenses', [])
        compliance_issues = []
        compliant_images = 0
        total_images = 0
        
        for image_list in assigned_images.values():
            for img in image_list:
                total_images += 1
                license_type = img.get('license', 'Unknown')
                
                # Check license compliance
                if license_type in allowed_licenses or 'Generated Content' in license_type:
                    compliant_images += 1
                else:
                    compliance_issues.append(f"Non-compliant license: {license_type}")
        
        return {
            'compliant_images': compliant_images,
            'total_images': total_images,
            'compliance_rate': compliant_images / total_images if total_images > 0 else 0.0,
            'issues': compliance_issues,
            'fully_compliant': len(compliance_issues) == 0
        }
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get comprehensive usage statistics"""
        stats = {
            'total_images_tracked': len(self.usage_data['images']),
            'high_usage_images': 0,
            'categories_served': set(),
            'keywords_served': set(),
            'source_breakdown': {},
            'last_updated': self.usage_data.get('last_updated', 'Unknown')
        }
        
        max_usage = self.quality_config.get('max_usage_count', 3)
        
        for img_data in self.usage_data['images'].values():
            if img_data['usage_count'] >= max_usage:
                stats['high_usage_images'] += 1
            
            stats['categories_served'].update(img_data.get('categories_used', []))
            stats['keywords_served'].update(img_data.get('keywords_used', []))
        
        # Convert sets to lists for JSON serialization
        stats['categories_served'] = list(stats['categories_served'])
        stats['keywords_served'] = list(stats['keywords_served'])
        
        return stats
    
    def cleanup_cache(self, days_old: int = 30):
        """Clean up old cached images"""
        cutoff_date = datetime.now() - timedelta(days=days_old)
        cleaned_count = 0
        
        try:
            for file_path in self.cache_dir.glob("*.png"):
                if file_path.stat().st_mtime < cutoff_date.timestamp():
                    file_path.unlink()
                    cleaned_count += 1
            
            print(f"🧹 Cache cleanup complete: removed {cleaned_count} old files")
            
        except Exception as e:
            print(f"⚠️ Cache cleanup failed: {e}")


# Convenience function for backward compatibility
def search_and_assign(keyword: str, category: str, needs: Dict[str, int], why_selected: Dict[str, str] = None) -> Dict[str, Any]:
    """
    Convenience function that creates ImageManager instance and calls search_and_assign
    This maintains compatibility with the existing smart_image_manager.py interface
    """
    try:
        manager = ComprehensiveImageManager()
        return manager.search_and_assign(keyword, category, needs, why_selected)
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'assigned_images': {},
            'fallback_reason': 'Failed to initialize ImageManager'
        }


if __name__ == "__main__":
    # Test the image manager
    manager = ComprehensiveImageManager()
    
    # Test search and assignment
    result = manager.search_and_assign(
        keyword="smart plug alexa",
        category="smart_plugs", 
        needs={'hero': 1, 'inline': 2},
        why_selected={'reason': 'High commercial intent + growing trend'}
    )
    
    print(f"\n🧪 Test Results:")
    print(f"Success: {result['success']}")
    print(f"Total Images: {result.get('total_images', 0)}")
    print(f"Sources: {result.get('sources_used', [])}")
    print(f"Quality Score: {result.get('quality_score', 0.0):.2f}")
    
    # Show usage stats
    stats = manager.get_usage_stats()
    print(f"\n📊 Usage Stats:")
    print(f"Images Tracked: {stats['total_images_tracked']}")
    print(f"Categories Served: {len(stats['categories_served'])}")