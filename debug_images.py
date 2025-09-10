#!/usr/bin/env python3
"""Debug script for image assignment"""

import sys
from pathlib import Path
sys.path.append('.')

def debug_image_search():
    """Debug the image search process"""
    from smart_image_manager import _token_set, _calculate_semantic_score, _normalize_category
    
    keyword = 'smart plug alexa'
    category = 'smart-plugs'
    
    # 1. Test token generation
    tokens = _token_set(keyword, category, '', 'high demand')
    print(f"1. Tokens: {tokens}")
    
    # 2. Test category normalization
    category_normalized = _normalize_category(category)
    print(f"2. Normalized category: {category_normalized}")
    
    # 3. Test path existence
    STATIC_DIR = Path('.') / 'static' / 'images' / 'products'
    category_folder = STATIC_DIR / category_normalized
    print(f"3. Category folder: {category_folder}")
    print(f"   Exists: {category_folder.exists()}")
    
    # 4. Test file discovery
    if category_folder.exists():
        jpgs = list(category_folder.glob('*.jpg'))
        webps = list(category_folder.glob('*.webp'))
        pngs = list(category_folder.glob('*.png'))
        print(f"4. Found files:")
        print(f"   JPGs: {len(jpgs)}")
        print(f"   WEBPs: {len(webps)}")
        print(f"   PNGs: {len(pngs)}")
        
        # 5. Test candidate generation
        candidates = []
        for image_path in jpgs + webps + pngs:
            url = f"/images/products/{category_normalized}/{image_path.name}"
            
            # Create meta like in the real function
            meta = {
                "url": url,
                "tags": list(tokens),  # Use actual tokens
                "scene": "compatibility",
                "used": 0,
                "quality_score": 0.8
            }
            
            # Calculate score
            meta["score"] = _calculate_semantic_score(tokens, meta)
            candidates.append(meta)
        
        print(f"5. Generated {len(candidates)} candidates")
        
        # Sort by score
        candidates.sort(key=lambda x: (-x.get("score", 0), x.get("used", 0)))
        
        print(f"6. Top 5 candidates:")
        for i, candidate in enumerate(candidates[:5]):
            print(f"   {i+1}. {candidate['url']} (score: {candidate['score']:.2f})")
        
        return candidates
    else:
        print("Category folder doesn't exist!")
        return []

if __name__ == "__main__":
    debug_image_search()