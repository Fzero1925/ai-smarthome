"""
Image caching and download utilities
Based on ai_shh_growth_kit_v3/image_aggregator/cache.py
"""
import os
import json
import hashlib
import requests
from pathlib import Path
from typing import Dict, Optional, Set
from PIL import Image
import time


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
            # Mark URL as used to prevent duplication
            mark_url_as_used(url)
            # Return path relative to project root, using forward slashes for web compatibility
            try:
                rel_path = webp_path.relative_to(Path.cwd())
                return str(rel_path).replace('\\', '/')
            except ValueError:
                # Fallback to absolute path if relative path calculation fails
                return str(webp_path).replace('\\', '/')
        else:
            # Mark URL as used even if WebP conversion failed
            mark_url_as_used(url)
            try:
                rel_path = original_path.relative_to(Path.cwd())
                return str(rel_path).replace('\\', '/')
            except ValueError:
                return str(original_path).replace('\\', '/')
            
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


def get_cache_key(cache_key: str) -> str:
    """
    Generate MD5 hash for cache key

    Args:
        cache_key: Complete cache key (e.g., "query_slug")

    Returns:
        MD5 hash string
    """
    return hashlib.md5(cache_key.encode('utf-8')).hexdigest()


def load_cached_results(cache_key: str, cache_dir: str = "data/image_cache") -> Optional[Dict]:
    """
    Load cached search results

    Args:
        cache_key: Complete cache key (e.g., "query_slug")
        cache_dir: Cache directory

    Returns:
        Cached results dict or None
    """
    try:
        # Use the full cache_key instead of just query
        cache_path = Path(cache_dir) / f"{get_cache_key(cache_key)}.json"

        if cache_path.exists():
            with open(cache_path, 'r', encoding='utf-8') as f:
                cached_data = json.load(f)
                print(f"Cache hit for: {cache_key}")
                return cached_data

        print(f"Cache miss for: {cache_key}")
        return None

    except Exception as e:
        print(f"Cache load error: {e}")
        return None


def save_cached_results(cache_key: str, results: Dict, cache_dir: str = "data/image_cache") -> None:
    """
    Save search results to cache

    Args:
        cache_key: Complete cache key (e.g., "query_slug")
        results: Search results dict
        cache_dir: Cache directory
    """
    try:
        cache_dir = Path(cache_dir)
        cache_dir.mkdir(parents=True, exist_ok=True)

        # Use the full cache_key instead of just query
        cache_path = cache_dir / f"{get_cache_key(cache_key)}.json"

        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(f"Cache saved for: {cache_key}")

    except Exception as e:
        print(f"Cache save error: {e}")


# URL Deduplication System
def load_used_urls(tracking_file: str = "data/image_cache/used_urls.json") -> Set[str]:
    """
    Load set of already used image URLs

    Args:
        tracking_file: Path to URL tracking file

    Returns:
        Set of used URLs
    """
    try:
        tracking_path = Path(tracking_file)
        if tracking_path.exists():
            with open(tracking_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return set(data.get('used_urls', []))
        return set()
    except Exception as e:
        print(f"Error loading used URLs: {e}")
        return set()


def save_used_urls(used_urls: Set[str], tracking_file: str = "data/image_cache/used_urls.json") -> None:
    """
    Save set of used image URLs

    Args:
        used_urls: Set of used URLs
        tracking_file: Path to URL tracking file
    """
    try:
        tracking_path = Path(tracking_file)
        tracking_path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            'used_urls': list(used_urls),
            'last_updated': time.time(),
            'total_count': len(used_urls)
        }

        with open(tracking_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    except Exception as e:
        print(f"Error saving used URLs: {e}")


def mark_url_as_used(url: str, tracking_file: str = "data/image_cache/used_urls.json") -> None:
    """
    Mark a URL as used to prevent duplication

    Args:
        url: Image URL to mark as used
        tracking_file: Path to URL tracking file
    """
    try:
        used_urls = load_used_urls(tracking_file)
        used_urls.add(url)
        save_used_urls(used_urls, tracking_file)
        print(f"Marked URL as used: {url}")
    except Exception as e:
        print(f"Error marking URL as used: {e}")


def is_url_used(url: str, tracking_file: str = "data/image_cache/used_urls.json") -> bool:
    """
    Check if a URL has already been used

    Args:
        url: Image URL to check
        tracking_file: Path to URL tracking file

    Returns:
        True if URL is already used, False otherwise
    """
    try:
        used_urls = load_used_urls(tracking_file)
        return url in used_urls
    except Exception as e:
        print(f"Error checking URL usage: {e}")
        return False


def filter_unique_images(candidates: list, max_images: int = 10) -> list:
    """
    Filter image candidates to ensure uniqueness across the site

    Args:
        candidates: List of image metadata dicts
        max_images: Maximum number of unique images to return

    Returns:
        List of unique image candidates
    """
    try:
        used_urls = load_used_urls()
        unique_candidates = []

        for candidate in candidates:
            url = candidate.get('url', '')
            if url and url not in used_urls:
                unique_candidates.append(candidate)
                if len(unique_candidates) >= max_images:
                    break

        print(f"Filtered {len(candidates)} candidates to {len(unique_candidates)} unique images")
        return unique_candidates

    except Exception as e:
        print(f"Error filtering unique images: {e}")
        return candidates[:max_images]  # Fallback to original list