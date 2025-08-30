"""
Advanced Keyword Analysis and Trend Detection Module

This module provides sophisticated keyword research capabilities using multiple data sources
to identify trending topics, assess keyword difficulty, and generate content ideas for 
smart home product reviews and guides.
"""

import os
import time
import random
import pandas as pd
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
import json
from dataclasses import dataclass, asdict

try:
    from pytrends.request import TrendReq
    PYTRENDS_AVAILABLE = True
except ImportError:
    print("Warning: pytrends not available. Install with: pip install pytrends")
    PYTRENDS_AVAILABLE = False


@dataclass
class KeywordMetrics:
    """Data class for keyword performance metrics"""
    keyword: str
    search_volume: int
    competition_score: float  # 0-1 scale
    trend_score: float       # 0-1 scale (higher = more trending)
    difficulty_score: float  # 0-1 scale (higher = more difficult)
    commercial_intent: float # 0-1 scale (higher = more commercial)
    suggested_topics: List[str]
    related_queries: List[str]
    seasonal_pattern: Dict[str, float]
    last_updated: datetime


class SmartHomeKeywordAnalyzer:
    """
    Advanced keyword analysis system specifically designed for smart home content.
    Combines multiple data sources to provide comprehensive keyword intelligence.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or self._get_default_config()
        self.pytrends = None
        self.cache_dir = "data/keyword_cache"
        self.cache_expiry = timedelta(hours=24)
        
        # Initialize Google Trends if available
        if PYTRENDS_AVAILABLE:
            self.pytrends = TrendReq(
                hl='en-US', 
                tz=360,
                timeout=(10, 25),
                proxies=[],
                retries=2,
                backoff_factor=0.1
            )
        
        # Smart home product categories and seed keywords
        self.smart_home_categories = {
            'smart_plugs': [
                'smart plug', 'wifi outlet', 'alexa plug', 'google home plug',
                'smart outlet', 'energy monitoring plug', 'outdoor smart plug'
            ],
            'smart_speakers': [
                'alexa echo', 'google home', 'smart speaker', 'voice assistant',
                'echo dot', 'google nest', 'homepod', 'smart display'
            ],
            'security_cameras': [
                'security camera', 'wifi camera', 'outdoor camera', 'doorbell camera',
                'surveillance camera', 'ip camera', 'wireless camera', 'night vision camera'
            ],
            'robot_vacuums': [
                'robot vacuum', 'robotic cleaner', 'automatic vacuum', 'smart vacuum',
                'roomba', 'mapping vacuum', 'self emptying vacuum', 'pet hair vacuum'
            ],
            'smart_thermostats': [
                'smart thermostat', 'wifi thermostat', 'programmable thermostat',
                'nest thermostat', 'ecobee', 'learning thermostat', 'energy saving thermostat'
            ],
            'smart_lighting': [
                'smart bulb', 'led smart light', 'color changing bulb', 'dimmer switch',
                'smart light strip', 'outdoor smart lights', 'motion sensor lights'
            ]
        }
        
        # Commercial intent indicators
        self.commercial_indicators = [
            'best', 'review', 'buy', 'price', 'cheap', 'deal', 'sale', 'discount',
            'compare', 'vs', 'alternative', 'recommendation', 'guide', 'how to choose'
        ]
        
        # Create cache directory
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def _get_default_config(self) -> Dict:
        """Get default configuration settings"""
        return {
            'max_keywords_per_batch': 5,  # Google Trends limit
            'request_delay': 1.0,         # Seconds between requests
            'cache_enabled': True,
            'include_seasonal_data': True,
            'min_search_volume': 100,
            'max_difficulty_score': 0.8
        }
    
    def analyze_trending_topics(self, category: str = None, geo: str = 'US') -> List[Dict]:
        """
        Analyze trending topics in smart home categories using Google Trends
        
        Args:
            category: Specific smart home category to analyze
            geo: Geographic region for trends (default: US)
            
        Returns:
            List of trending topics with metrics
        """
        if not PYTRENDS_AVAILABLE:
            return self._get_fallback_trends()
        
        trending_topics = []
        categories = [category] if category else list(self.smart_home_categories.keys())
        
        for cat in categories:
            try:
                # Get trending queries for category
                seed_keywords = self.smart_home_categories[cat][:self.config['max_keywords_per_batch']]
                
                # Build payload for Google Trends
                self.pytrends.build_payload(
                    seed_keywords,
                    cat=0,
                    timeframe='today 3-m',  # Last 3 months
                    geo=geo,
                    gprop=''
                )
                
                # Get interest over time
                interest_df = self.pytrends.interest_over_time()
                
                if not interest_df.empty:
                    # Calculate trend scores
                    for keyword in seed_keywords:
                        if keyword in interest_df.columns:
                            trend_data = interest_df[keyword]
                            trend_score = self._calculate_trend_score(trend_data)
                            
                            topic_data = {
                                'keyword': keyword,
                                'category': cat,
                                'trend_score': trend_score,
                                'avg_interest': trend_data.mean(),
                                'peak_interest': trend_data.max(),
                                'current_interest': trend_data.iloc[-1] if len(trend_data) > 0 else 0,
                                'timestamp': datetime.now()
                            }
                            trending_topics.append(topic_data)
                
                # Get related queries
                related_queries = self.pytrends.related_queries()
                self._process_related_queries(related_queries, cat, trending_topics)
                
                # Respectful delay between requests
                time.sleep(self.config['request_delay'])
                
            except Exception as e:
                print(f"Error analyzing trends for category {cat}: {str(e)}")
                continue
        
        return sorted(trending_topics, key=lambda x: x['trend_score'], reverse=True)
    
    def _calculate_trend_score(self, trend_data: pd.Series) -> float:
        """Calculate a normalized trend score based on recent growth"""
        if len(trend_data) < 2:
            return 0.0
        
        # Recent period (last 30% of data points)
        recent_size = max(1, int(len(trend_data) * 0.3))
        recent_avg = trend_data.tail(recent_size).mean()
        overall_avg = trend_data.mean()
        
        # Calculate growth rate
        if overall_avg > 0:
            growth_rate = (recent_avg - overall_avg) / overall_avg
        else:
            growth_rate = 0
        
        # Normalize to 0-1 scale
        trend_score = min(1.0, max(0.0, (growth_rate + 1) / 2))
        return round(trend_score, 3)
    
    def _process_related_queries(self, related_queries: Dict, category: str, trending_topics: List[Dict]):
        """Process related queries from Google Trends"""
        for keyword, queries in related_queries.items():
            if queries is not None:
                # Top queries
                if 'top' in queries and queries['top'] is not None:
                    for _, row in queries['top'].head(5).iterrows():
                        related_keyword = row['query']
                        if self._is_relevant_keyword(related_keyword, category):
                            trending_topics.append({
                                'keyword': related_keyword,
                                'category': category,
                                'trend_score': 0.5,  # Default score for related queries
                                'parent_keyword': keyword,
                                'query_type': 'related_top',
                                'timestamp': datetime.now()
                            })
                
                # Rising queries
                if 'rising' in queries and queries['rising'] is not None:
                    for _, row in queries['rising'].head(3).iterrows():
                        related_keyword = row['query']
                        if self._is_relevant_keyword(related_keyword, category):
                            trending_topics.append({
                                'keyword': related_keyword,
                                'category': category,
                                'trend_score': 0.8,  # Higher score for rising queries
                                'parent_keyword': keyword,
                                'query_type': 'related_rising',
                                'timestamp': datetime.now()
                            })
    
    def _is_relevant_keyword(self, keyword: str, category: str) -> bool:
        """Check if a keyword is relevant to the smart home category"""
        keyword_lower = keyword.lower()
        
        # Category-specific relevance check
        category_terms = self.smart_home_categories.get(category, [])
        for term in category_terms:
            if any(word in keyword_lower for word in term.lower().split()):
                return True
        
        # General smart home terms
        smart_home_terms = [
            'smart', 'wifi', 'bluetooth', 'alexa', 'google', 'home', 'automation',
            'iot', 'connected', 'wireless', 'app', 'control', 'remote'
        ]
        
        return any(term in keyword_lower for term in smart_home_terms)
    
    def analyze_keyword_metrics(self, keywords: List[str]) -> List[KeywordMetrics]:
        """
        Comprehensive analysis of keyword metrics including difficulty, volume, and intent
        
        Args:
            keywords: List of keywords to analyze
            
        Returns:
            List of KeywordMetrics objects
        """
        metrics_list = []
        
        for keyword in keywords:
            try:
                # Check cache first
                cached_metrics = self._get_cached_metrics(keyword)
                if cached_metrics:
                    metrics_list.append(cached_metrics)
                    continue
                
                # Calculate various metrics
                search_volume = self._estimate_search_volume(keyword)
                competition_score = self._calculate_competition_score(keyword)
                commercial_intent = self._calculate_commercial_intent(keyword)
                difficulty_score = self._calculate_difficulty_score(keyword)
                
                # Get related data
                suggested_topics = self._generate_topic_suggestions(keyword)
                related_queries = self._get_related_queries(keyword)
                seasonal_pattern = self._analyze_seasonal_pattern(keyword)
                
                # Create metrics object
                metrics = KeywordMetrics(
                    keyword=keyword,
                    search_volume=search_volume,
                    competition_score=competition_score,
                    trend_score=0.5,  # Will be updated by trend analysis
                    difficulty_score=difficulty_score,
                    commercial_intent=commercial_intent,
                    suggested_topics=suggested_topics,
                    related_queries=related_queries,
                    seasonal_pattern=seasonal_pattern,
                    last_updated=datetime.now()
                )
                
                metrics_list.append(metrics)
                
                # Cache the results
                self._cache_metrics(metrics)
                
                # Respectful delay
                time.sleep(0.5)
                
            except Exception as e:
                print(f"Error analyzing keyword '{keyword}': {str(e)}")
                continue
        
        return metrics_list
    
    def _estimate_search_volume(self, keyword: str) -> int:
        """Estimate search volume using available data sources"""
        # This is a simplified estimation - in production you'd use paid APIs
        base_volume = 1000
        
        # Adjust based on keyword characteristics
        word_count = len(keyword.split())
        if word_count == 1:
            base_volume *= 2  # Single words tend to have higher volume
        elif word_count > 3:
            base_volume *= 0.5  # Long-tail keywords have lower volume
        
        # Adjust for commercial intent
        commercial_intent = self._calculate_commercial_intent(keyword)
        base_volume = int(base_volume * (1 + commercial_intent))
        
        return max(100, base_volume)
    
    def _calculate_competition_score(self, keyword: str) -> float:
        """Calculate competition score based on keyword characteristics"""
        score = 0.5  # Base competition level
        
        # High competition indicators
        high_comp_terms = ['best', 'top', 'review', 'vs', 'comparison']
        if any(term in keyword.lower() for term in high_comp_terms):
            score += 0.2
        
        # Brand keywords typically have higher competition
        brands = ['amazon', 'google', 'apple', 'samsung', 'philips', 'nest']
        if any(brand in keyword.lower() for brand in brands):
            score += 0.1
        
        # Generic vs specific keywords
        if len(keyword.split()) == 1:
            score += 0.2  # Single words more competitive
        
        return min(1.0, max(0.0, score))
    
    def _calculate_commercial_intent(self, keyword: str) -> float:
        """Calculate commercial intent score"""
        keyword_lower = keyword.lower()
        intent_score = 0.0
        
        # Strong commercial indicators
        strong_indicators = ['buy', 'price', 'deal', 'sale', 'cheap', 'discount', 'coupon']
        for indicator in strong_indicators:
            if indicator in keyword_lower:
                intent_score += 0.2
        
        # Medium commercial indicators  
        medium_indicators = ['best', 'review', 'compare', 'vs', 'alternative', 'recommendation']
        for indicator in medium_indicators:
            if indicator in keyword_lower:
                intent_score += 0.1
        
        # Product-specific terms
        product_terms = ['smart', 'wifi', 'bluetooth', 'wireless', 'device']
        if any(term in keyword_lower for term in product_terms):
            intent_score += 0.05
        
        return min(1.0, intent_score)
    
    def _calculate_difficulty_score(self, keyword: str) -> float:
        """Calculate keyword difficulty score"""
        # Simplified difficulty calculation
        difficulty = 0.3  # Base difficulty
        
        # Length affects difficulty
        word_count = len(keyword.split())
        if word_count == 1:
            difficulty += 0.4  # Single words are harder
        elif word_count > 4:
            difficulty -= 0.2  # Long-tail easier
        
        # Commercial keywords are more difficult
        commercial_score = self._calculate_commercial_intent(keyword)
        difficulty += commercial_score * 0.3
        
        return min(1.0, max(0.0, difficulty))
    
    def _generate_topic_suggestions(self, keyword: str) -> List[str]:
        """Generate related topic suggestions for content creation"""
        suggestions = []
        keyword_words = keyword.lower().split()
        
        # Common content angles for smart home products
        content_angles = [
            f"How to choose the best {keyword}",
            f"{keyword} installation guide",
            f"{keyword} troubleshooting tips",
            f"{keyword} vs alternatives",
            f"Budget {keyword} options",
            f"{keyword} for beginners",
            f"Professional {keyword} review",
            f"{keyword} buying guide 2025"
        ]
        
        # Filter relevant suggestions
        for angle in content_angles[:5]:  # Limit to 5 suggestions
            suggestions.append(angle)
        
        return suggestions
    
    def _get_related_queries(self, keyword: str) -> List[str]:
        """Get related query suggestions"""
        related = []
        
        # Generate variations
        base_variations = [
            f"best {keyword}",
            f"{keyword} review",
            f"cheap {keyword}",
            f"{keyword} 2025",
            f"{keyword} comparison"
        ]
        
        related.extend(base_variations[:3])  # Limit to 3
        return related
    
    def _analyze_seasonal_pattern(self, keyword: str) -> Dict[str, float]:
        """Analyze seasonal trends for the keyword"""
        # This is a simplified version - real implementation would use historical data
        seasons = {
            'spring': 0.8,
            'summer': 1.0,
            'fall': 0.9,
            'winter': 1.1  # Higher in winter (indoor activities)
        }
        
        # Adjust based on keyword type
        if 'outdoor' in keyword.lower():
            seasons.update({
                'spring': 1.2,
                'summer': 1.3,
                'fall': 0.7,
                'winter': 0.3
            })
        elif 'holiday' in keyword.lower() or 'christmas' in keyword.lower():
            seasons.update({
                'spring': 0.5,
                'summer': 0.4,
                'fall': 0.8,
                'winter': 1.5
            })
        
        return seasons
    
    def _get_cached_metrics(self, keyword: str) -> Optional[KeywordMetrics]:
        """Retrieve cached keyword metrics if available and not expired"""
        if not self.config['cache_enabled']:
            return None
        
        cache_file = os.path.join(self.cache_dir, f"{keyword.replace(' ', '_')}.json")
        
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Check if cache is expired
                last_updated = datetime.fromisoformat(data['last_updated'])
                if datetime.now() - last_updated < self.cache_expiry:
                    # Convert back to KeywordMetrics object
                    data['last_updated'] = last_updated
                    return KeywordMetrics(**data)
            except Exception as e:
                print(f"Error reading cache for {keyword}: {str(e)}")
        
        return None
    
    def _cache_metrics(self, metrics: KeywordMetrics):
        """Cache keyword metrics to disk"""
        if not self.config['cache_enabled']:
            return
        
        cache_file = os.path.join(self.cache_dir, f"{metrics.keyword.replace(' ', '_')}.json")
        
        try:
            # Convert to dict and handle datetime serialization
            data = asdict(metrics)
            data['last_updated'] = data['last_updated'].isoformat()
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error caching metrics for {metrics.keyword}: {str(e)}")
    
    def _get_fallback_trends(self) -> List[Dict]:
        """Fallback trending topics when Pytrends is not available"""
        fallback_trends = [
            {'keyword': 'smart home automation', 'category': 'general', 'trend_score': 0.8},
            {'keyword': 'alexa smart plug', 'category': 'smart_plugs', 'trend_score': 0.7},
            {'keyword': 'robot vacuum pet hair', 'category': 'robot_vacuums', 'trend_score': 0.9},
            {'keyword': 'outdoor security camera', 'category': 'security_cameras', 'trend_score': 0.6},
            {'keyword': 'color changing smart bulb', 'category': 'smart_lighting', 'trend_score': 0.8}
        ]
        
        for trend in fallback_trends:
            trend['timestamp'] = datetime.now()
            trend['avg_interest'] = random.randint(20, 80)
        
        return fallback_trends
    
    def export_keyword_report(self, metrics_list: List[KeywordMetrics], 
                            output_file: str = None) -> str:
        """Export comprehensive keyword analysis report"""
        if not output_file:
            output_file = f"data/keyword_report_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
        
        # Convert to DataFrame for easy export
        report_data = []
        for metrics in metrics_list:
            row = {
                'keyword': metrics.keyword,
                'search_volume': metrics.search_volume,
                'competition_score': metrics.competition_score,
                'trend_score': metrics.trend_score,
                'difficulty_score': metrics.difficulty_score,
                'commercial_intent': metrics.commercial_intent,
                'suggested_topics': '; '.join(metrics.suggested_topics),
                'related_queries': '; '.join(metrics.related_queries),
                'last_updated': metrics.last_updated
            }
            report_data.append(row)
        
        df = pd.DataFrame(report_data)
        df.to_csv(output_file, index=False)
        
        return output_file


# Example usage and testing
if __name__ == "__main__":
    analyzer = SmartHomeKeywordAnalyzer()
    
    # Analyze trending topics
    print("Analyzing trending topics...")
    trends = analyzer.analyze_trending_topics('smart_plugs')
    
    for trend in trends[:5]:
        print(f"Keyword: {trend['keyword']}")
        print(f"Trend Score: {trend['trend_score']}")
        print(f"Category: {trend['category']}")
        print("-" * 40)
    
    # Analyze specific keywords
    test_keywords = [
        'smart plug alexa',
        'robot vacuum pet hair',
        'outdoor security camera',
        'smart thermostat energy saving'
    ]
    
    print("\nAnalyzing keyword metrics...")
    metrics = analyzer.analyze_keyword_metrics(test_keywords)
    
    for metric in metrics:
        print(f"\nKeyword: {metric.keyword}")
        print(f"Search Volume: {metric.search_volume}")
        print(f"Commercial Intent: {metric.commercial_intent:.2f}")
        print(f"Difficulty Score: {metric.difficulty_score:.2f}")
    
    # Export report
    report_file = analyzer.export_keyword_report(metrics)
    print(f"\nReport exported to: {report_file}")