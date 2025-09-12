"""
Image caching and download utilities
Based on ai_shh_growth_kit_v3/image_aggregator/cache.py
"""
import os
import json
import hashlib
import requests
from pathlib import Path
from typing import Dict, Optional
from PIL import Image


def dl(url: str, out_dir: Path, filename: str) -> str:
    """
    Download image from URL and save locally
    
    Args:
        url: Image URL
        out_dir: Output directory  
        filename: Output filename (without extension)
        
    Returns:
        Local file path or empty string if failed
    """
    try:
        if not url:
            return ""
            
        # Create output directory
        out_dir = Path(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        
        # Download image
        headers = {
            'User-Agent': 'AI-SmartHomeHub/1.0 (contact@ai-smarthomehub.com)'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Determine file extension from content type
        content_type = response.headers.get('content-type', '')
        if 'jpeg' in content_type or 'jpg' in content_type:
            ext = '.jpg'
        elif 'png' in content_type:
            ext = '.png'
        elif 'webp' in content_type:
            ext = '.webp'
        else:
            # Try to get extension from URL
            url_ext = Path(url).suffix.lower()
            ext = url_ext if url_ext in ['.jpg', '.jpeg', '.png', '.webp'] else '.jpg'
        
        # Save original image
        original_path = out_dir / f"{filename}_original{ext}"
        with open(original_path, 'wb') as f:
            f.write(response.content)
        
        # Convert to WebP for optimization
        webp_path = out_dir / f"{filename}.webp"
        
        with Image.open(original_path) as img:
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            # Optimize size while maintaining quality
            img.save(webp_path, 'WEBP', quality=85, optimize=True)
        
        # Remove original if conversion successful
        if webp_path.exists():
            original_path.unlink()
            return str(webp_path.relative_to(Path.cwd()))
        else:
            return str(original_path.relative_to(Path.cwd()))
            
    except requests.exceptions.RequestException as e:
        print(f"Download error for {url}: {e}")
        return ""
    except Exception as e:
        print(f"Image processing error for {url}: {e}")
        return ""


def write_meta(image_path: str, metadata: Dict) -> None:
    """
    Write image metadata to JSON file
    
    Args:
        image_path: Path to image file
        metadata: Image metadata dict
    """
    try:
        if not image_path:
            return
            
        meta_path = Path(image_path).with_suffix('.json')
        
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
            
    except Exception as e:
        print(f"Metadata write error for {image_path}: {e}")


def get_cache_key(query: str) -> str:
    """
    Generate cache key for query
    
    Args:
        query: Search query
        
    Returns:
        Cache key string
    """
    return hashlib.md5(query.encode('utf-8')).hexdigest()


def load_cached_results(query: str, cache_dir: str = "data/image_cache") -> Optional[list]:
    """
    Load cached search results
    
    Args:
        query: Search query
        cache_dir: Cache directory
        
    Returns:
        Cached results or None
    """
    try:
        cache_path = Path(cache_dir) / f"{get_cache_key(query)}.json"
        
        if cache_path.exists():
            with open(cache_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return None
        
    except Exception as e:
        print(f"Cache load error: {e}")
        return None


def save_cached_results(query: str, results: list, cache_dir: str = "data/image_cache") -> None:
    """
    Save search results to cache
    
    Args:
        query: Search query
        results: Search results
        cache_dir: Cache directory
    """
    try:
        cache_dir = Path(cache_dir)
        cache_dir.mkdir(parents=True, exist_ok=True)
        
        cache_path = cache_dir / f"{get_cache_key(query)}.json"
        
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
            
    except Exception as e:
        print(f"Cache save error: {e}")