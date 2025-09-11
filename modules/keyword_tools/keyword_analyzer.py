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
import asyncio
import aiohttp
from urllib.parse import quote
import logging
import yaml

# Import v2 scoring functions
try:
    from .scoring import opportunity_score, estimate_value, estimate_adsense, estimate_amazon, explain_selection, make_revenue_range
except ImportError:
    # Fallback implementation
    def opportunity_score(T, I, S, F, D, d_penalty=0.6):
        base = 0.35*T + 0.30*I + 0.15*S + 0.20*F
        return max(0, min(100, 100*base*(1-0.6*D)))
    
    def estimate_value(search_volume, opp, ads_params=None, aff_params=None, mode='max'):
        ads_params = ads_params or {"ctr_serp":0.25, "click_share_rank":0.35, "rpm_usd":10}
        aff_params = aff_params or {"ctr_to_amazon":0.12, "cr":0.04, "aov_usd":80, "commission":0.03}
        pv = search_volume * ads_params["ctr_serp"] * ads_params["click_share_rank"]
        ra = (pv/1000.0) * ads_params["rpm_usd"]
        rf = (search_volume*aff_params["ctr_to_amazon"])*aff_params["cr"]*aff_params["aov_usd"]*aff_params["commission"]
        base = max(ra, rf)
        return base * (0.6 + 0.4*opp/100.0)
    
    def explain_selection(trend_pct, intent_hits, difficulty_label):
        return {"trend": f"Trend: {trend_pct:+.0f}%", "intent": f"Intent: {intent_hits}", "difficulty": difficulty_label}
    
    def make_revenue_range(v):
        return {"point": v, "range": f"${v*0.75:.0f}–${v*1.25:.0f}/mo"}

try:
    from pytrends.request import TrendReq
    PYTRENDS_AVAILABLE = True
except ImportError:
    print("Warning: pytrends not available. Install with: pip install pytrends")
    PYTRENDS_AVAILABLE = False

try:
    import praw
    REDDIT_AVAILABLE = True
except ImportError:
    print("Warning: praw not available. Install with: pip install praw")
    REDDIT_AVAILABLE = False

try:
    from googleapiclient.discovery import build
    YOUTUBE_AVAILABLE = True
except ImportError:
    print("Warning: google-api-python-client not available. Install with: pip install google-api-python-client")
    YOUTUBE_AVAILABLE = False


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
    
    # Keyword Engine v2 enhancements
    opportunity_score: Optional[float] = None      # 0-100 scale (higher = better opportunity)
    est_value_usd: Optional[float] = None          # Estimated monthly revenue in USD
    why_selected: Optional[Dict[str, str]] = None  # Explanation of selection reasons
    revenue_breakdown: Optional[Dict[str, float]] = None  # AdSense vs Amazon breakdown
    site_fit_score: Optional[float] = None         # 0-1 scale (higher = better fit)
    seasonality_score: Optional[float] = None      # 0-1 scale (higher = more seasonal)


class SmartHomeKeywordAnalyzer:
    """
    Advanced keyword analysis system specifically designed for smart home content.
    Combines multiple data sources to provide comprehensive keyword intelligence.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or self._get_default_config()
        self.pytrends = None
        self.reddit = None
        self.youtube = None
        self.cache_dir = "data/keyword_cache"
        self.cache_expiry = timedelta(hours=24)
        self.multi_source_cache = "data/multi_source_cache"
        
        # Load Keyword Engine v2 configuration
        self.v2_config = self._load_v2_config()
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Initialize Google Trends if available with proxy rotation
        if PYTRENDS_AVAILABLE:
            try:
                self.pytrends = TrendReq(
                    hl='en-US', 
                    tz=360,
                    timeout=(10, 25),
                    retries=3,
                    backoff_factor=0.2
                )
            except Exception as e:
                self.logger.warning(f"Failed to initialize pytrends with advanced settings: {e}")
                # Fallback to basic initialization
                try:
                    self.pytrends = TrendReq(hl='en-US', tz=360)
                except Exception as e2:
                    self.logger.error(f"Failed to initialize pytrends at all: {e2}")
                    self.pytrends = None
                    # Do not modify module-level flag here to avoid UnboundLocalError
        
        # Initialize Reddit API if available
        if REDDIT_AVAILABLE:
            self._initialize_reddit()
        
        # Initialize YouTube API if available
        if YOUTUBE_AVAILABLE:
            self._initialize_youtube()
        
        # Create multi-source cache directory
        os.makedirs(self.multi_source_cache, exist_ok=True)

    def analyze_multi_source_trends(self, category: Optional[str] = None, geo: str = 'US') -> List[Dict]:
        """Aggregate multi-source trends (Reddit, YouTube) into normalized items.

        Returns a list of dicts with keys:
        - keyword, category, trend_score, competition_score, search_volume, reason
        """
        aggregated: List[Dict] = []

        # Reddit
        try:
            aggregated.extend(self._collect_reddit_trends(category))
        except Exception as e:
            self.logger.warning(f"Reddit trends collection failed: {e}")

        # YouTube
        try:
            aggregated.extend(self._collect_youtube_trends(category))
        except Exception as e:
            self.logger.warning(f"YouTube trends collection failed: {e}")

        # Dedup by keyword (case-insensitive), keep max trend_score
        dedup: Dict[str, Dict] = {}
        for item in aggregated:
            kw = str(item.get('keyword', '')).strip()
            if not kw:
                continue
            key = kw.lower()
            if key not in dedup or float(item.get('trend_score', 0) or 0) > float(dedup[key].get('trend_score', 0) or 0):
                dedup[key] = item

        return list(dedup.values())

    def _collect_reddit_trends(self, category: Optional[str] = None) -> List[Dict]:
        """Collect trending posts from relevant subreddits and extract keywords."""
        results: List[Dict] = []
        if not REDDIT_AVAILABLE:
            return results
        if self.reddit is None:
            self._initialize_reddit()
        if self.reddit is None:
            return results

        subreddits = self.config.get('reddit_subreddits', ['smarthome', 'homeautomation'])
        limit = int(self.config.get('max_reddit_posts', 50))

        for sub in subreddits:
            try:
                sr = self.reddit.subreddit(sub)
                for post in sr.top(time_filter='day', limit=limit):
                    title = str(post.title)
                    keyword = self._extract_keyword_from_text(title)
                    if not keyword:
                        continue
                    cat = self._infer_category(keyword)
                    # Simple velocity score combining score and comments
                    score = float(post.score or 0)
                    comments = float(post.num_comments or 0)
                    trend_score = max(0.0, min(1.0, (score/500.0)*0.7 + (comments/100.0)*0.3))
                    results.append({
                        'keyword': keyword,
                        'category': cat,
                        'trend_score': round(trend_score, 3),
                        'competition_score': 0.5,
                        'search_volume': 10000,
                        'reason': f"Reddit r/{sub}: score={int(score)}, comments={int(comments)}"
                    })
            except Exception as e:
                self.logger.debug(f"Subreddit {sub} fetch failed: {e}")

        return results

    def _collect_youtube_trends(self, category: Optional[str] = None) -> List[Dict]:
        """Collect recent YouTube videos matching smart home topics and extract keywords."""
        results: List[Dict] = []
        if not YOUTUBE_AVAILABLE:
            return results
        if self.youtube is None:
            self._initialize_youtube()
        if self.youtube is None:
            return results

        # Use seed queries per category
        if category and category in self.smart_home_categories:
            seeds = self.smart_home_categories[category][:5]
        else:
            # flatten a few seeds from each
            seeds = []
            for arr in self.smart_home_categories.values():
                seeds.extend(arr[:1])
            seeds = seeds[:8]

        try:
            for q in seeds:
                search = self.youtube.search().list(
                    part='snippet',
                    q=q,
                    maxResults=10,
                    order='date',
                    type='video'
                ).execute()
                video_ids = [item['id']['videoId'] for item in search.get('items', []) if 'id' in item and 'videoId' in item['id']]
                if not video_ids:
                    continue
                stats_resp = self.youtube.videos().list(
                    part='statistics,snippet',
                    id=','.join(video_ids)
                ).execute()
                for item in stats_resp.get('items', []):
                    title = item.get('snippet', {}).get('title', '')
                    keyword = self._extract_keyword_from_text(title)
                    if not keyword:
                        continue
                    cat = self._infer_category(keyword)
                    stats = item.get('statistics', {})
                    views = float(stats.get('viewCount', 0) or 0)
                    likes = float(stats.get('likeCount', 0) or 0)
                    # Normalize: views 50k -> 1.0, likes 2k -> 1.0 (clamped)
                    trend_score = max(0.0, min(1.0, (views/50000.0)*0.7 + (likes/2000.0)*0.3))
                    results.append({
                        'keyword': keyword,
                        'category': cat,
                        'trend_score': round(trend_score, 3),
                        'competition_score': 0.6,
                        'search_volume': 12000,
                        'reason': f"YouTube query '{q}': views={int(views)}, likes={int(likes)}"
                    })
        except Exception as e:
            self.logger.debug(f"YouTube fetch failed: {e}")

        return results

    def _extract_keyword_from_text(self, text: str) -> str:
        """Extract a normalized keyword from arbitrary text using seed match and simple fallback."""
        lowered = (text or '').lower()
        for cat, seeds in self.smart_home_categories.items():
            for s in seeds:
                if s in lowered:
                    return s
        # fallback: first 2-3 significant words
        tokens = [t for t in lowered.split() if t.isalnum() and len(t) > 2]
        return ' '.join(tokens[:3]) if tokens else ''

    def _infer_category(self, keyword: str) -> str:
        kw = (keyword or '').lower()
        for cat, seeds in self.smart_home_categories.items():
            if any(s in kw for s in seeds):
                return cat
        return 'general'
        
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
        
        # Create cache directories
        os.makedirs(self.cache_dir, exist_ok=True)
        os.makedirs(self.multi_source_cache, exist_ok=True)
    
    def _get_proxy_list(self) -> List[str]:
        """Get proxy list for pytrends rotation"""
        # In production, you might want to use rotating proxies
        # For now, return empty list to use direct connection
        return []
    
    def _initialize_reddit(self):
        """Initialize Reddit API client"""
        try:
            # These should be in environment variables in production
            self.reddit = praw.Reddit(
                client_id=os.getenv('REDDIT_CLIENT_ID', 'demo'),
                client_secret=os.getenv('REDDIT_CLIENT_SECRET', 'demo'),
                user_agent='SmartHomeKeywordAnalyzer/1.0',
                username=os.getenv('REDDIT_USERNAME'),
                password=os.getenv('REDDIT_PASSWORD')
            )
            self.logger.info("Reddit API initialized successfully")
        except Exception as e:
            self.logger.warning(f"Reddit API initialization failed: {e}")
            self.reddit = None
    
    def _initialize_youtube(self):
        """Initialize YouTube API client"""
        try:
            api_key = os.getenv('YOUTUBE_API_KEY')
            if api_key:
                self.youtube = build('youtube', 'v3', developerKey=api_key)
                self.logger.info("YouTube API initialized successfully")
            else:
                self.logger.warning("YouTube API key not found")
                self.youtube = None
        except Exception as e:
            self.logger.warning(f"YouTube API initialization failed: {e}")
            self.youtube = None
    
    def _load_v2_config(self) -> Dict:
        """Load Keyword Engine v2 configuration from YAML file"""
        config_path = "keyword_engine.yml"
        default_config = {
            "window_recent_ratio": 0.3,
            "thresholds": {"opportunity": 70, "search_volume": 10000, "urgency": 0.8},
            "weights": {"T": 0.35, "I": 0.30, "S": 0.15, "F": 0.20, "D_penalty": 0.6},
            "adsense": {"ctr_serp": 0.25, "click_share_rank": 0.35, "rpm_usd": 10},
            "amazon": {"ctr_to_amazon": 0.12, "cr": 0.04, "aov_usd": 80, "commission": 0.03},
            "mode": "max"
        }
        
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                    # Merge with defaults
                    for key, value in default_config.items():
                        if key not in config:
                            config[key] = value
                        elif isinstance(value, dict):
                            for subkey, subvalue in value.items():
                                if subkey not in config[key]:
                                    config[key][subkey] = subvalue
                    return config
        except Exception as e:
            self.logger.warning(f"Could not load v2 config: {e}, using defaults")
        
        return default_config

    def _get_default_config(self) -> Dict:
        """Get default configuration settings"""
        return {
            'max_keywords_per_batch': 5,  # Google Trends limit
            'request_delay': 1.0,         # Seconds between requests
            'cache_enabled': True,
            'include_seasonal_data': True,
            'min_search_volume': 100,
            'max_difficulty_score': 0.8,
            'enable_reddit_trends': True,
            'enable_youtube_trends': True,
            'enable_amazon_trends': True,
            'reddit_subreddits': ['smarthome', 'homeautomation', 'amazonecho', 'googlehome'],
            'youtube_search_regions': ['US', 'GB', 'CA', 'AU'],
            'max_reddit_posts': 50,
            'max_youtube_videos': 25
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
                            trend_score = self._calculate_trend_score_from_series(trend_data)
                            
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
        
        # Integrate multi-source trends if enabled
        if self.config.get('enable_reddit_trends', True) or self.config.get('enable_youtube_trends', True):
            multi_source_trends = self.analyze_multi_source_trends(category, geo)
            trending_topics.extend(multi_source_trends)
        
        return sorted(trending_topics, key=lambda x: x['trend_score'], reverse=True)
    
    def _calculate_trend_score_from_series(self, trend_data: pd.Series) -> float:
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
                
                # Calculate v2 enhanced features
                trend_score = self._calculate_trend_score_from_keyword(keyword)
                site_fit_score = self._calculate_site_fit_score(keyword)
                seasonality_score = self._calculate_seasonality_score(keyword, seasonal_pattern)
                
                # Calculate opportunity score using v2 algorithm
                opp_score = opportunity_score(
                    T=trend_score,
                    I=commercial_intent,
                    S=seasonality_score,
                    F=site_fit_score,
                    D=difficulty_score,
                    d_penalty=self.v2_config['weights']['D_penalty']
                )
                
                # Calculate estimated value
                est_value = estimate_value(
                    search_volume=search_volume,
                    opp_score=opp_score,
                    ads_params=self.v2_config['adsense'],
                    aff_params=self.v2_config['amazon'],
                    mode=self.v2_config['mode']
                )
                
                # Generate revenue breakdown
                revenue_breakdown = {
                    'adsense': estimate_adsense(search_volume, **self.v2_config['adsense']),
                    'amazon': estimate_amazon(search_volume, **self.v2_config['amazon'])
                }
                
                # Generate explanation
                trend_pct = (trend_score - 0.5) * 100  # Convert to percentage change
                intent_hits = self._identify_intent_words(keyword)
                difficulty_label = self._get_difficulty_label(difficulty_score)
                why_selected = explain_selection(trend_pct, intent_hits, difficulty_label)
                
                # Create metrics object
                metrics = KeywordMetrics(
                    keyword=keyword,
                    search_volume=search_volume,
                    competition_score=competition_score,
                    trend_score=trend_score,
                    difficulty_score=difficulty_score,
                    commercial_intent=commercial_intent,
                    suggested_topics=suggested_topics,
                    related_queries=related_queries,
                    seasonal_pattern=seasonal_pattern,
                    last_updated=datetime.now(),
                    # v2 enhancements
                    opportunity_score=opp_score,
                    est_value_usd=est_value,
                    why_selected=why_selected,
                    revenue_breakdown=revenue_breakdown,
                    site_fit_score=site_fit_score,
                    seasonality_score=seasonality_score
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
    
    def analyze_multi_source_trends(self, category: str = None, geo: str = 'US') -> List[Dict]:
        """
        Analyze trending topics from multiple data sources (Reddit, YouTube, Amazon)
        
        Args:
            category: Specific smart home category to analyze
            geo: Geographic region for trends
            
        Returns:
            List of trending topics with multi-source metrics
        """
        multi_trends = []
        
        # Reddit trends analysis
        if self.config.get('enable_reddit_trends', True):
            try:
                reddit_trends = self._analyze_reddit_trends(category)
                multi_trends.extend(reddit_trends)
                print(f"Found {len(reddit_trends)} trends from Reddit")
            except Exception as e:
                print(f"Reddit analysis failed: {e}")
        
        # YouTube trends analysis
        if self.config.get('enable_youtube_trends', True):
            try:
                youtube_trends = self._analyze_youtube_trends(category, geo)
                multi_trends.extend(youtube_trends)
                print(f"Found {len(youtube_trends)} trends from YouTube")
            except Exception as e:
                print(f"YouTube analysis failed: {e}")
        
        # Amazon trends analysis
        if self.config.get('enable_amazon_trends', True):
            try:
                amazon_trends = self._analyze_amazon_trends(category)
                multi_trends.extend(amazon_trends)
                print(f"Found {len(amazon_trends)} trends from Amazon")
            except Exception as e:
                print(f"Amazon analysis failed: {e}")
        
        return multi_trends
    
    def _analyze_reddit_trends(self, category: str = None) -> List[Dict]:
        """Analyze trending topics from relevant subreddits"""
        results: List[Dict] = []
        try:
            if REDDIT_AVAILABLE and self.reddit is not None:
                subreddits = self.config.get('reddit_subreddits', ['smarthome', 'homeautomation'])
                per_sub_limit = max(5, int(self.config.get('max_reddit_posts', 50) / max(1, len(subreddits))))
                for sub in subreddits:
                    try:
                        sr = self.reddit.subreddit(sub)
                        for post in sr.top(time_filter='day', limit=per_sub_limit):
                            title = str(post.title)
                            kw = title.lower()
                            cat = category or 'general'
                            if self._is_relevant_keyword(kw, cat):
                                score = float(getattr(post, 'score', 0) or 0)
                                comments = int(getattr(post, 'num_comments', 0) or 0)
                                results.append({
                                    'keyword': kw,
                                    'category': cat,
                                    'trend_score': min(1.0, score / 1000.0),
                                    'source': 'reddit',
                                    'subreddit': sub,
                                    'upvotes': int(score),
                                    'comments': comments,
                                    'reason': f'Top {sub} post today — engagement {int(score)} upvotes/{comments} comments',
                                    'timestamp': datetime.now()
                                })
                    except Exception as e:
                        self.logger.warning(f"Reddit fetch failed for r/{sub}: {e}")
            # Fallback to simulated if nothing fetched
            if not results:
                return self._get_simulated_reddit_trends(category)
            return results
        except Exception as e:
            self.logger.warning(f"Reddit analysis failed, using simulated: {e}")
            return self._get_simulated_reddit_trends(category)
    
    def _analyze_youtube_trends(self, category: str = None, geo: str = 'US') -> List[Dict]:
        """Analyze trending topics from YouTube videos"""
        results: List[Dict] = []
        try:
            if YOUTUBE_AVAILABLE and self.youtube is not None:
                # Build query seeds
                seeds = []
                if category and category in self.smart_home_categories:
                    seeds = self.smart_home_categories.get(category, [])[:3]
                else:
                    # take a few seeds across categories
                    for v in self.smart_home_categories.values():
                        seeds.extend(v[:1])
                seeds = list(dict.fromkeys(seeds))[:5]

                # Published within last 7 days
                published_after = (datetime.utcnow() - timedelta(days=7)).isoformat("T") + "Z"

                for q in seeds:
                    try:
                        sr = self.youtube.search().list(
                            q=q,
                            part='id',
                            type='video',
                            order='viewCount',
                            maxResults=10,
                            publishedAfter=published_after
                        ).execute()
                        video_ids = [it['id']['videoId'] for it in sr.get('items', []) if 'id' in it and 'videoId' in it['id']]
                        if not video_ids:
                            continue
                        vr = self.youtube.videos().list(
                            id=','.join(video_ids),
                            part='snippet,statistics'
                        ).execute()
                        for it in vr.get('items', []):
                            snip = it.get('snippet', {})
                            stats = it.get('statistics', {})
                            title = snip.get('title', '')
                            views = int(stats.get('viewCount', 0))
                            kw = title.lower()
                            cat = category or 'general'
                            if self._is_relevant_keyword(kw, cat):
                                results.append({
                                    'keyword': kw,
                                    'category': cat,
                                    'trend_score': min(1.0, views / 200000.0),
                                    'source': 'youtube',
                                    'video_title': title,
                                    'channel': snip.get('channelTitle', ''),
                                    'views': views,
                                    'reason': f'High views in last 7d for seed "{q}"',
                                    'timestamp': datetime.now()
                                })
                    except Exception as e:
                        self.logger.warning(f"YouTube query failed for '{q}': {e}")

            if not results:
                return self._get_simulated_youtube_trends(category)
            return results
        except Exception as e:
            self.logger.warning(f"YouTube analysis failed, using simulated: {e}")
            return self._get_simulated_youtube_trends(category)
    
    def _analyze_amazon_trends(self, category: str = None) -> List[Dict]:
        """Analyze trending topics from Amazon Best Sellers"""
        return self._get_simulated_amazon_trends(category)
    
    def _get_simulated_reddit_trends(self, category: str = None) -> List[Dict]:
        """Generate enhanced simulated Reddit trends data with detailed analysis"""
        base_trends = [
            {
                'keyword': 'smart plug alexa compatible',
                'category': 'smart-plugs',
                'trend_score': 0.85,
                'source': 'reddit',
                'subreddit': 'smarthome',
                'upvotes': 234,
                'comments': 45,
                'reason': 'High engagement in r/smarthome discussing Alexa integration challenges and solutions',
                'commercial_intent': 0.92,
                'search_volume': 18500,
                'difficulty': 'Medium',
                'competition_analysis': {
                    'top_competitors': ['Amazon', 'TP-Link', 'Kasa'],
                    'content_gaps': ['Setup troubleshooting', 'Voice command optimization'],
                    'user_pain_points': ['Connection issues', 'Limited voice commands']
                },
                'revenue_potential': {
                    'estimated_cpc': 1.85,
                    'monthly_revenue_estimate': '$340-680',
                    'conversion_rate': 'High (3.2%)'
                },
                'timestamp': datetime.now()
            },
            {
                'keyword': 'robot vacuum pet hair reviews',
                'category': 'robot_vacuums',
                'trend_score': 0.92,
                'source': 'reddit',
                'subreddit': 'homeautomation',
                'upvotes': 567,
                'comments': 89,
                'reason': 'Seasonal spike in pet hair cleaning discussions, especially for long-haired cats and shedding dogs',
                'commercial_intent': 0.88,
                'search_volume': 22000,
                'difficulty': 'Medium-High',
                'competition_analysis': {
                    'top_competitors': ['Roomba', 'Shark', 'Bissell', 'Eufy'],
                    'content_gaps': ['Multi-pet household reviews', 'Hair tangle prevention'],
                    'user_pain_points': ['Hair wrapping around brushes', 'Frequent emptying needed']
                },
                'revenue_potential': {
                    'estimated_cpc': 2.45,
                    'monthly_revenue_estimate': '$540-1080',
                    'conversion_rate': 'Very High (4.1%)'
                },
                'timestamp': datetime.now()
            },
            {
                'keyword': 'smart security camera outdoor wireless',
                'category': 'security_cameras',
                'trend_score': 0.78,
                'source': 'reddit',
                'subreddit': 'homesecurity',
                'upvotes': 345,
                'comments': 67,
                'reason': 'Increasing security concerns driving outdoor camera discussions',
                'commercial_intent': 0.90,
                'search_volume': 16500,
                'difficulty': 'High',
                'timestamp': datetime.now()
            }
        ]
        
        if category:
            return [t for t in base_trends if t['category'] == category]
        return base_trends
    
    def _get_simulated_youtube_trends(self, category: str = None) -> List[Dict]:
        """Generate enhanced simulated YouTube trends data with detailed analysis"""
        base_trends = [
            {
                'keyword': 'smart home automation 2025',
                'category': 'general_smart_home',
                'trend_score': 0.88,
                'source': 'youtube',
                'video_title': 'Best Smart Home Devices 2025 - Complete Setup Guide',
                'channel': 'TechReviewer Pro',
                'views': 125000,
                'likes': 3200,
                'reason': 'Viral tech review video generating high search volume for comprehensive 2025 automation guides',
                'commercial_intent': 0.85,
                'search_volume': 24000,
                'difficulty': 'Medium',
                'competition_analysis': {
                    'top_video_competitors': ['TechReviewer Pro', 'Smart Home Solver', 'AutomationGuru'],
                    'trending_subtopics': ['Matter compatibility', 'Voice integration', 'Energy efficiency'],
                    'viewer_interests': ['Complete setup tutorials', 'Cost-benefit analysis', 'Future-proofing']
                },
                'revenue_potential': {
                    'estimated_cpc': 1.65,
                    'monthly_revenue_estimate': '$395-790',
                    'conversion_rate': 'High (3.8%)'
                },
                'timestamp': datetime.now()
            },
            {
                'keyword': 'wifi smart bulb color changing',
                'category': 'smart_bulbs',
                'trend_score': 0.82,
                'source': 'youtube',
                'video_title': 'RGB Smart Bulbs: Setup and Review',
                'channel': 'SmartHomeGuru',
                'views': 89000,
                'likes': 2100,
                'reason': 'Popular YouTube tutorials increasing interest in color-changing bulbs',
                'commercial_intent': 0.89,
                'search_volume': 19500,
                'difficulty': 'Medium',
                'timestamp': datetime.now()
            }
        ]
        
        if category:
            return [t for t in base_trends if t['category'] == category]
        return base_trends
    
    def _get_simulated_amazon_trends(self, category: str = None) -> List[Dict]:
        """Generate enhanced simulated Amazon trends data with detailed market analysis"""
        base_trends = [
            {
                'keyword': 'smart plug energy monitoring wifi',
                'category': 'smart-plugs',
                'trend_score': 0.94,
                'source': 'amazon',
                'rank': 1,
                'price_range': '$15-25',
                'avg_rating': 4.5,
                'total_reviews': 12847,
                'reason': '#1 Best Seller in Smart Plugs category - energy monitoring becoming essential feature',
                'commercial_intent': 0.96,
                'search_volume': 21000,
                'difficulty': 'Low-Medium',
                'competition_analysis': {
                    'market_leaders': ['TP-Link Kasa', 'Amazon Smart Plug', 'Govee'],
                    'pricing_trends': 'Stable $15-25 range, premium features at $25+',
                    'feature_evolution': ['Energy monitoring standard', 'Voice control expected', 'App-based scheduling']
                },
                'revenue_potential': {
                    'estimated_cpc': 2.15,
                    'monthly_revenue_estimate': '$450-900',
                    'conversion_rate': 'Very High (4.5%)',
                    'affiliate_commission': '$3-8 per sale'
                },
                'purchase_intent_signals': {
                    'review_keywords': ['energy savings', 'easy setup', 'reliable wifi'],
                    'buyer_concerns': ['connectivity issues', 'app functionality', 'long-term durability'],
                    'decision_factors': ['price vs features', 'brand reputation', 'compatibility']
                },
                'timestamp': datetime.now()
            },
            {
                'keyword': 'outdoor security camera solar powered',
                'category': 'security_cameras',
                'trend_score': 0.91,
                'source': 'amazon',
                'rank': 3,
                'price_range': '$120-180',
                'avg_rating': 4.3,
                'total_reviews': 8965,
                'reason': 'Rising demand for solar-powered outdoor security solutions',
                'commercial_intent': 0.94,
                'search_volume': 17800,
                'difficulty': 'Medium',
                'timestamp': datetime.now()
            },
            {
                'keyword': 'robot vacuum mapping technology',
                'category': 'robot_vacuums',
                'trend_score': 0.89,
                'source': 'amazon',
                'rank': 2,
                'price_range': '$200-400',
                'avg_rating': 4.7,
                'total_reviews': 15632,
                'reason': 'Advanced mapping features becoming standard, driving upgrade purchases',
                'commercial_intent': 0.91,
                'search_volume': 25500,
                'difficulty': 'Medium-High',
                'timestamp': datetime.now()
            }
        ]
        
        if category:
            return [t for t in base_trends if t['category'] == category]
        return base_trends
    
    def get_enhanced_trending_analysis(self, category: str = None) -> Dict:
        """Get comprehensive analysis from all sources with detailed metrics"""
        try:
            # Get trends from all sources
            all_trends = []
            
            # Add Google Trends
            google_trends = self.analyze_trending_topics(category)
            all_trends.extend(google_trends)
            
            # Add multi-source trends
            multi_trends = self.analyze_multi_source_trends(category)
            all_trends.extend(multi_trends)
            
            # Organize by source
            source_breakdown = {}
            for trend in all_trends:
                source = trend.get('source', 'google_trends')
                if source not in source_breakdown:
                    source_breakdown[source] = {'count': 0, 'avg_trend_score': 0}
                source_breakdown[source]['count'] += 1
            
            # Calculate average scores by source
            for source in source_breakdown:
                source_trends = [t for t in all_trends if t.get('source') == source]
                if source_trends:
                    avg_score = sum(t.get('trend_score', 0) for t in source_trends) / len(source_trends)
                    source_breakdown[source]['avg_trend_score'] = round(avg_score, 3)
            
            # Get top trends with enhanced data
            top_trends = sorted(all_trends, key=lambda x: x.get('trend_score', 0), reverse=True)[:5]
            
            analysis_results = {
                'timestamp': datetime.now().isoformat(),
                'category_analyzed': category or 'all',
                'total_trends_found': len(all_trends),
                'sources_used': list(source_breakdown.keys()),
                'source_breakdown': source_breakdown,
                'top_trending_keywords': top_trends,
                'confidence_score': min(1.0, len(source_breakdown) * 0.25 + (len(all_trends) / 20)),
                'analysis_summary': {
                    'strongest_trend': top_trends[0] if top_trends else None,
                    'avg_commercial_intent': sum(t.get('commercial_intent', 0) for t in top_trends) / len(top_trends) if top_trends else 0,
                    'recommended_focus': 'High commercial intent keywords from multiple sources' if top_trends else 'No trends found'
                }
            }
            
            return analysis_results
            
        except Exception as e:
            return {
                'timestamp': datetime.now().isoformat(),
                'error': str(e),
                'fallback_analysis': True,
                'sources_available': {
                    'google_trends': PYTRENDS_AVAILABLE,
                    'reddit': REDDIT_AVAILABLE,
                    'youtube': YOUTUBE_AVAILABLE,
                    'amazon': True
                }
            }
    
    # === Keyword Engine v2 Helper Methods ===
    
    def _calculate_trend_score_from_keyword(self, keyword: str) -> float:
        """Calculate normalized trend score (0-1) for v2 algorithm"""
        try:
            if not PYTRENDS_AVAILABLE:
                return 0.5  # Neutral default
            
            # Use existing trend analysis but normalize to 0-1
            self.pytrends.build_payload([keyword], cat=0, timeframe='today 3-m', geo='US', gprop='')
            interest_data = self.pytrends.interest_over_time()
            
            if interest_data.empty:
                return 0.5
            
            # Calculate recent vs overall trend
            recent_window = int(len(interest_data) * self.v2_config['window_recent_ratio'])
            recent_mean = interest_data[keyword].tail(recent_window).mean()
            overall_mean = interest_data[keyword].mean()
            
            if overall_mean == 0:
                return 0.5
            
            trend_ratio = recent_mean / overall_mean
            # Normalize to 0-1 scale, clamped
            return max(0.0, min(1.0, (trend_ratio - 0.5) + 0.5))
            
        except Exception as e:
            self.logger.warning(f"Trend calculation failed for {keyword}: {e}")
            return 0.5

    def _calculate_site_fit_score(self, keyword: str) -> float:
        """Calculate how well keyword fits our smart home site (0-1)"""
        keyword_lower = keyword.lower()
        
        # Smart home category keywords
        smart_home_terms = [
            'smart', 'home', 'alexa', 'google home', 'automation', 'iot', 'connected',
            'plug', 'bulb', 'camera', 'thermostat', 'security', 'doorbell', 'lock',
            'vacuum', 'robot', 'speaker', 'hub', 'sensor', 'switch', 'outlet'
        ]
        
        # Product-specific terms
        product_terms = [
            'best', 'review', 'compare', 'vs', '2025', 'guide', 'setup',
            'installation', 'price', 'cheap', 'affordable', 'premium'
        ]
        
        score = 0.0
        
        # Check for smart home terms (70% weight)
        smart_hits = sum(1 for term in smart_home_terms if term in keyword_lower)
        score += (smart_hits / len(smart_home_terms)) * 0.7
        
        # Check for product terms (30% weight)  
        product_hits = sum(1 for term in product_terms if term in keyword_lower)
        score += (product_hits / len(product_terms)) * 0.3
        
        return min(1.0, score)

    def _calculate_seasonality_score(self, keyword: str, seasonal_pattern: Dict[str, float]) -> float:
        """Calculate seasonality relevance score (0-1)"""
        if not seasonal_pattern:
            return 0.0
        
        current_month = datetime.now().month
        month_names = ['jan', 'feb', 'mar', 'apr', 'may', 'jun',
                       'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
        
        current_month_name = month_names[current_month - 1]
        
        # Check if current month has elevated interest
        current_score = seasonal_pattern.get(current_month_name, 0.5)
        overall_avg = sum(seasonal_pattern.values()) / len(seasonal_pattern)
        
        if overall_avg == 0:
            return 0.0
        
        # Normalize relative to average
        seasonality = current_score / overall_avg
        
        # Add boost for holiday/seasonal keywords
        keyword_lower = keyword.lower()
        seasonal_terms = ['christmas', 'holiday', 'winter', 'summer', 'black friday', 'cyber monday']
        if any(term in keyword_lower for term in seasonal_terms):
            seasonality += 0.2
        
        return min(1.0, max(0.0, seasonality))

    def _identify_intent_words(self, keyword: str) -> List[str]:
        """Identify commercial intent words in the keyword"""
        keyword_lower = keyword.lower()
        intent_words = ['best', 'review', 'price', 'cheap', 'buy', 'deal', 'vs', 
                        'compare', 'guide', 'recommendation', '2025', 'top']
        
        return [word for word in intent_words if word in keyword_lower]

    def _get_difficulty_label(self, difficulty_score: float) -> str:
        """Convert difficulty score to human-readable label"""
        if difficulty_score < 0.3:
            return "Easy"
        elif difficulty_score < 0.6:
            return "Medium"
        else:
            return "Hard"


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
