"""
Semantic ranking for image search results
Based on ai_shh_growth_kit_v3/image_aggregator/semantic_rank.py
"""
from typing import List, Dict
import re
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False


class SemanticImageRanker:
    """Ranks images based on semantic similarity to query"""
    
    def __init__(self):
        self.model = None
        self.fallback_mode = False
        
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                # Use lightweight model suitable for short texts
                self.model = SentenceTransformer('all-MiniLM-L6-v2')
                print("Semantic ranking: Using sentence-transformers model")
            except Exception as e:
                print(f"Failed to load sentence-transformers model: {e}")
                self.fallback_mode = True
        else:
            print("sentence-transformers not available, using fallback ranking")
            self.fallback_mode = True
    
    def rank_images(self, query: str, candidates: List[Dict], threshold: float = 0.28) -> List[Dict]:
        """
        Rank image candidates by semantic similarity to query
        
        Args:
            query: Search query text
            candidates: List of image metadata dicts
            threshold: Minimum similarity threshold
            
        Returns:
            Ranked list of image dicts with similarity scores
        """
        if not candidates:
            return []
        
        if self.fallback_mode or not self.model:
            return self._fallback_ranking(query, candidates)
        
        try:
            # Extract text features from images
            candidate_texts = []
            for candidate in candidates:
                text_features = self._extract_text_features(candidate)
                candidate_texts.append(text_features)
            
            # Calculate semantic similarity
            query_embedding = self.model.encode([query])
            candidate_embeddings = self.model.encode(candidate_texts)
            
            # Calculate cosine similarity
            from sklearn.metrics.pairwise import cosine_similarity
            similarities = cosine_similarity(query_embedding, candidate_embeddings)[0]
            
            # Add similarity scores and filter by threshold
            ranked_candidates = []
            for i, candidate in enumerate(candidates):
                similarity = similarities[i]
                if similarity >= threshold:
                    candidate_copy = candidate.copy()
                    candidate_copy['similarity_score'] = float(similarity)
                    ranked_candidates.append(candidate_copy)
            
            # Sort by similarity score (descending)
            ranked_candidates.sort(key=lambda x: x['similarity_score'], reverse=True)
            
            return ranked_candidates
            
        except Exception as e:
            print(f"Semantic ranking error: {e}")
            return self._fallback_ranking(query, candidates)
    
    def _extract_text_features(self, candidate: Dict) -> str:
        """Extract relevant text features from image metadata"""
        features = []
        
        # Add title
        title = candidate.get('title', '')
        if title:
            features.append(title)
        
        # Add description
        description = candidate.get('description', '')
        if description:
            # Clean HTML tags if present
            description = re.sub(r'<[^>]+>', '', description)
            # Limit description length
            if len(description) > 200:
                description = description[:200] + "..."
            features.append(description)
        
        # Add tags
        tags = candidate.get('tags', [])
        if tags:
            if isinstance(tags, list):
                features.extend([tag.get('name', '') if isinstance(tag, dict) else str(tag) for tag in tags[:5]])
            
        # Combine all features
        text = ' '.join(features).strip()
        return text if text else candidate.get('title', 'image')
    
    def _fallback_ranking(self, query: str, candidates: List[Dict]) -> List[Dict]:
        """Fallback keyword-based ranking when semantic model is unavailable"""
        query_words = set(query.lower().split())
        
        scored_candidates = []
        for candidate in candidates:
            score = self._calculate_keyword_score(query_words, candidate)
            if score > 0:  # Only include candidates with some relevance
                candidate_copy = candidate.copy()
                candidate_copy['similarity_score'] = score
                scored_candidates.append(candidate_copy)
        
        # Sort by score (descending)
        scored_candidates.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        return scored_candidates
    
    def _calculate_keyword_score(self, query_words: set, candidate: Dict) -> float:
        """Calculate keyword-based relevance score"""
        score = 0.0
        
        # Check title (weight: 3.0)
        title = candidate.get('title', '').lower()
        if title:
            title_words = set(title.split())
            common_title = query_words.intersection(title_words)
            score += len(common_title) * 3.0
        
        # Check description (weight: 2.0)
        description = candidate.get('description', '').lower()
        if description:
            description_words = set(description.split())
            common_desc = query_words.intersection(description_words)
            score += len(common_desc) * 2.0
        
        # Check tags (weight: 1.5)
        tags = candidate.get('tags', [])
        if tags:
            tag_text = ' '.join([str(tag).lower() for tag in tags])
            tag_words = set(tag_text.split())
            common_tags = query_words.intersection(tag_words)
            score += len(common_tags) * 1.5
        
        # Normalize score by query length
        max_possible_score = len(query_words) * 3.0
        return score / max_possible_score if max_possible_score > 0 else 0.0


# Global instance
_ranker = None


def rank_images(query: str, candidates: List[Dict], threshold: float = 0.28) -> List[Dict]:
    """
    Convenience function for ranking images
    
    Args:
        query: Search query
        candidates: List of image metadata dicts  
        threshold: Minimum similarity threshold
        
    Returns:
        Ranked list of images
    """
    global _ranker
    if _ranker is None:
        _ranker = SemanticImageRanker()
    
    return _ranker.rank_images(query, candidates, threshold)