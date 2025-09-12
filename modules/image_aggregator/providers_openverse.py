"""
Openverse API provider for free images
Based on ai_shh_growth_kit_v3/image_aggregator/providers_openverse.py
"""
import requests
import json
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
        # Openverse API endpoint
        url = "https://api.openverse.engineering/v1/images/"
        
        params = {
            'q': query,
            'page_size': limit,
            'license_type': 'commercial',  # Commercial use allowed
            'mature': 'false',
            'format': 'json'
        }
        
        headers = {
            'User-Agent': 'AI-SmartHomeHub/1.0 (contact@ai-smarthomehub.com)'
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        
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
        url = f"https://api.openverse.engineering/v1/images/{image_id}/"
        
        headers = {
            'User-Agent': 'AI-SmartHomeHub/1.0 (contact@ai-smarthomehub.com)'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        return response.json()
        
    except requests.exceptions.RequestException as e:
        print(f"Openverse details API error: {e}")
        return {}