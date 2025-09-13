"""
Openverse API provider for free images
Based on ai_shh_growth_kit_v3/image_aggregator/providers_openverse.py
"""
import requests
import json
import time
import re
from typing import List, Dict


def search(query: str, limit: int = 10) -> List[Dict]:
    """
    Search Openverse for CC-licensed images

    Args:
        query: Search terms
        limit: Maximum number of results

    Returns:
        List of image metadata dicts
    """
    try:
        # Simplify query to avoid Cloudflare bot detection
        simplified_query = _simplify_query(query)

        # Openverse API endpoint
        url = "https://api.openverse.org/v1/images/"

        params = {
            'q': simplified_query,
            'page_size': min(limit, 10),  # Limit to avoid large requests
            'license_type': 'commercial',  # Commercial use allowed
            'mature': 'false',
            'format': 'json'
        }

        # Use more realistic browser headers to avoid bot detection
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://openverse.org/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site'
        }
        
        # Add delay to avoid rate limiting
        time.sleep(0.5)

        # Add SSL error handling with fallback
        try:
            response = requests.get(url, params=params, headers=headers, timeout=15, verify=True)
            response.raise_for_status()

            # Check if Cloudflare blocked the request
            if 'cloudflare' in response.text.lower() and 'just a moment' in response.text.lower():
                print(f"Cloudflare bot protection detected for query: {simplified_query}")
                return []  # Gracefully fail, let fallback system handle it

        except requests.exceptions.SSLError as ssl_error:
            print(f"SSL verification failed for Openverse API: {ssl_error}")
            print("Trying with SSL verification disabled...")
            try:
                response = requests.get(url, params=params, headers=headers, timeout=15, verify=False)
                response.raise_for_status()
            except Exception as fallback_error:
                raise Exception(f"Both SSL and non-SSL requests failed: {fallback_error}")
        except requests.exceptions.HTTPError as http_error:
            if response.status_code == 403:
                print(f"Openverse API access denied (403) for query: {simplified_query}")
                return []  # Gracefully fail for 403 errors
            else:
                raise http_error
        except Exception as e:
            raise e
        
        data = response.json()
        results = []
        
        for item in data.get('results', []):
            # Extract metadata
            image_meta = {
                'url': item.get('url'),
                'thumbnail': item.get('thumbnail'),
                'title': item.get('title', ''),
                'description': item.get('description', ''),
                'width': item.get('width', 0),
                'height': item.get('height', 0),
                'license': item.get('license'),
                'license_version': item.get('license_version'),
                'creator': item.get('creator'),
                'creator_url': item.get('creator_url'),
                'source': 'openverse',
                'provider': item.get('provider'),
                'tags': item.get('tags', [])
            }
            
            # Filter by minimum dimensions
            if image_meta['width'] >= 800 and image_meta['height'] >= 450:
                results.append(image_meta)
        
        return results[:limit]
        
    except requests.exceptions.RequestException as e:
        print(f"Openverse API error: {e}")
        return []
    except Exception as e:
        print(f"Openverse processing error: {e}")
        return []


def get_image_details(image_id: str) -> Dict:
    """
    Get detailed information about a specific image
    
    Args:
        image_id: Openverse image ID
        
    Returns:
        Detailed image metadata dict
    """
    try:
        url = f"https://api.openverse.org/v1/images/{image_id}/"
        
        headers = {
            'User-Agent': 'AI-SmartHomeHub/1.0 (contact@ai-smarthomehub.com)'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        return response.json()
        
    except requests.exceptions.RequestException as e:
        print(f"Openverse details API error: {e}")
        return {}


def _simplify_query(query: str) -> str:
    """
    Simplify query to avoid Cloudflare bot detection

    Args:
        query: Original search query

    Returns:
        Simplified query string
    """
    # Remove duplicate words
    words = query.lower().split()
    unique_words = []
    seen = set()

    for word in words:
        if word not in seen:
            unique_words.append(word)
            seen.add(word)

    # Keep only the most important 3-4 words to avoid complex queries
    important_words = []

    # Prioritize certain key terms
    priority_terms = ['smart', 'home', 'plug', 'camera', 'light', 'vacuum', 'wifi', 'alexa', 'google']

    # Add priority terms first
    for word in unique_words:
        if word in priority_terms and len(important_words) < 4:
            important_words.append(word)

    # Add remaining words up to limit
    for word in unique_words:
        if word not in important_words and len(important_words) < 3:
            important_words.append(word)

    simplified = ' '.join(important_words)

    # Remove special characters that might trigger bot detection
    simplified = re.sub(r'[^\w\s-]', '', simplified)
    simplified = re.sub(r'\s+', ' ', simplified).strip()

    # If query is still too long, take first 50 characters
    if len(simplified) > 50:
        simplified = simplified[:47] + '...'

    return simplified or 'smart home'  # Fallback if everything gets filtered out