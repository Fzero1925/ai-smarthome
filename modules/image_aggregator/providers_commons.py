"""
Wikimedia Commons API provider for free images  
Based on ai_shh_growth_kit_v3/image_aggregator/providers_commons.py
"""
import requests
import json
from typing import List, Dict


def search(query: str, limit: int = 20) -> List[Dict]:
    """
    Search Wikimedia Commons for free images
    
    Args:
        query: Search terms
        limit: Maximum number of results
        
    Returns:
        List of image metadata dicts
    """
    try:
        # Wikimedia Commons API endpoint
        url = "https://commons.wikimedia.org/w/api.php"
        
        params = {
            'action': 'query',
            'format': 'json',
            'list': 'search',
            'srsearch': f'filetype:bitmap {query}',
            'srnamespace': 6,  # File namespace
            'srlimit': limit,
            'srprop': 'size|wordcount|timestamp'
        }
        
        headers = {
            'User-Agent': 'AI-SmartHomeHub/1.0 (contact@ai-smarthomehub.com)'
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        results = []
        
        for item in data.get('query', {}).get('search', []):
            title = item.get('title', '')
            if not title.startswith('File:'):
                continue
                
            # Get image info
            image_info = get_image_info(title)
            if image_info:
                results.append(image_info)
        
        return results[:limit]
        
    except requests.exceptions.RequestException as e:
        print(f"Wikimedia Commons API error: {e}")
        return []
    except Exception as e:
        print(f"Commons processing error: {e}")
        return []


def get_image_info(title: str) -> Dict:
    """
    Get detailed information about a Commons image
    
    Args:
        title: File title (e.g., "File:Example.jpg")
        
    Returns:
        Image metadata dict or None
    """
    try:
        url = "https://commons.wikimedia.org/w/api.php"
        
        params = {
            'action': 'query',
            'format': 'json',
            'titles': title,
            'prop': 'imageinfo',
            'iiprop': 'url|size|metadata|extmetadata',
            'iiurlwidth': 1200
        }
        
        headers = {
            'User-Agent': 'AI-SmartHomeHub/1.0 (contact@ai-smarthomehub.com)'
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        pages = data.get('query', {}).get('pages', {})
        
        for page_id, page in pages.items():
            if page_id == '-1':  # File not found
                continue
                
            imageinfo = page.get('imageinfo', [])
            if not imageinfo:
                continue
                
            info = imageinfo[0]
            extmetadata = info.get('extmetadata', {})
            
            # Extract metadata
            image_meta = {
                'url': info.get('url'),
                'thumbnail': info.get('thumburl'),
                'title': page.get('title', '').replace('File:', ''),
                'description': extmetadata.get('ImageDescription', {}).get('value', ''),
                'width': info.get('width', 0),
                'height': info.get('height', 0),
                'license': extmetadata.get('License', {}).get('value', 'CC'),
                'license_version': '',
                'creator': extmetadata.get('Artist', {}).get('value', ''),
                'creator_url': '',
                'source': 'wikimedia_commons',
                'provider': 'wikimedia',
                'tags': []
            }
            
            # Filter by minimum dimensions
            if image_meta['width'] >= 800 and image_meta['height'] >= 450:
                return image_meta
        
        return None
        
    except requests.exceptions.RequestException as e:
        print(f"Wikimedia image info API error: {e}")
        return None
    except Exception as e:
        print(f"Commons image info processing error: {e}")
        return None