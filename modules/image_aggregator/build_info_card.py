"""
Build informational graphics as fallback when no suitable images are found
Based on ai_shh_growth_kit_v3/image_aggregator/build_info_card.py
"""
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from typing import List


def make_info_card(title: str, bullet_points: List[str], output_path: str, 
                   size: tuple = (1280, 720), 
                   bg_color: str = '#f8f9fa',
                   text_color: str = '#212529',
                   accent_color: str = '#007bff') -> str:
    """
    Create an informational graphic card with title and bullet points
    
    Args:
        title: Main title text
        bullet_points: List of bullet point strings
        output_path: Output file path
        size: Image dimensions (width, height)
        bg_color: Background color hex
        text_color: Text color hex  
        accent_color: Accent color hex
        
    Returns:
        Output file path or empty string if failed
    """
    try:
        # Create output directory
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Create image
        img = Image.new('RGB', size, bg_color)
        draw = ImageDraw.Draw(img)
        
        # Try to load fonts, fall back to default if not available
        try:
            title_font = ImageFont.truetype('arial.ttf', 48)
            subtitle_font = ImageFont.truetype('arial.ttf', 32)
            bullet_font = ImageFont.truetype('arial.ttf', 28)
        except (OSError, IOError):
            # Fallback to default font with different sizes
            title_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()
            bullet_font = ImageFont.load_default()
        
        # Calculate positions
        width, height = size
        margin = 80
        current_y = margin
        
        # Draw title
        title_bbox = draw.textbbox((0, 0), title, font=title_font)
        title_width = title_bbox[2] - title_bbox[0]
        title_height = title_bbox[3] - title_bbox[1]
        title_x = (width - title_width) // 2
        
        draw.text((title_x, current_y), title, fill=accent_color, font=title_font)
        current_y += title_height + 60
        
        # Draw accent line under title
        line_width = min(title_width, width - 2 * margin)
        line_x = (width - line_width) // 2
        draw.rectangle([line_x, current_y, line_x + line_width, current_y + 4], 
                      fill=accent_color)
        current_y += 50
        
        # Draw bullet points
        bullet_margin = margin + 40
        for i, point in enumerate(bullet_points[:5]):  # Max 5 bullet points
            if current_y > height - 100:  # Leave space at bottom
                break
                
            # Clean and truncate text
            point = str(point).strip()
            if len(point) > 60:
                point = point[:57] + '...'
            
            # Draw bullet
            bullet_x = bullet_margin
            bullet_y = current_y + 5
            draw.ellipse([bullet_x, bullet_y, bullet_x + 12, bullet_y + 12], 
                        fill=accent_color)
            
            # Draw text
            text_x = bullet_x + 25
            draw.text((text_x, current_y), point, fill=text_color, font=bullet_font)
            
            # Calculate line height for next bullet
            text_bbox = draw.textbbox((0, 0), point, font=bullet_font)
            line_height = text_bbox[3] - text_bbox[1]
            current_y += max(line_height, 20) + 25
        
        # Add footer text
        footer_text = "AI Smart Home Hub"
        footer_bbox = draw.textbbox((0, 0), footer_text, font=subtitle_font)
        footer_width = footer_bbox[2] - footer_bbox[0]
        footer_x = (width - footer_width) // 2
        footer_y = height - margin - 20
        
        draw.text((footer_x, footer_y), footer_text, fill='#6c757d', font=subtitle_font)
        
        # Save as WebP for optimization
        if output_path.lower().endswith('.webp'):
            img.save(output_path, 'WEBP', quality=85, optimize=True)
        else:
            # Convert extension to WebP
            webp_path = str(output_file.with_suffix('.webp'))
            img.save(webp_path, 'WEBP', quality=85, optimize=True)
            output_path = webp_path
        
        # Return relative path if possible, otherwise absolute path
        try:
            return str(Path(output_path).relative_to(Path.cwd()))
        except ValueError:
            # If can't make relative, return the absolute path
            return output_path
        
    except Exception as e:
        print(f"Info card creation error: {e}")
        return ""


def make_category_card(category: str, features: List[str], output_path: str, keyword: str = "") -> str:
    """
    Create a category-specific information card with keyword differentiation

    Args:
        category: Product category (e.g., "Smart Plugs")
        features: List of key features
        output_path: Output file path
        keyword: Original keyword for context-specific customization

    Returns:
        Output file path or empty string if failed
    """
    # Enhanced color schemes with keyword-specific variations
    base_schemes = {
        'smart-plugs': {'bg': '#f8f9fa', 'accent': '#28a745', 'text': '#212529'},
        'smart-cameras': {'bg': '#f8f9fa', 'accent': '#dc3545', 'text': '#212529'},
        'smart-lights': {'bg': '#f8f9fa', 'accent': '#ffc107', 'text': '#212529'},
        'robot-vacuums': {'bg': '#f8f9fa', 'accent': '#17a2b8', 'text': '#212529'},
        'security-cameras': {'bg': '#f8f9fa', 'accent': '#dc3545', 'text': '#212529'},
        'default': {'bg': '#f8f9fa', 'accent': '#007bff', 'text': '#212529'}
    }

    # Get base scheme
    scheme = base_schemes.get(category.lower(), base_schemes['default'])

    # CRITICAL: Customize based on keyword to create visual differentiation
    keyword_lower = keyword.lower()

    # Black Friday / Sales context - use promotional colors
    if any(term in keyword_lower for term in ['black friday', 'sale', 'deal', 'discount', 'cyber monday']):
        scheme = {'bg': '#1a1a1a', 'accent': '#ff6b35', 'text': '#ffffff'}  # Dark with orange accent

    # Pet-related context - use warm, pet-friendly colors
    elif any(term in keyword_lower for term in ['pet', 'dog', 'cat', 'fur', 'hair']):
        scheme = {'bg': '#fff8e1', 'accent': '#8d6e63', 'text': '#3e2723'}  # Warm brown theme

    # Outdoor/Solar context - use nature-inspired colors
    elif any(term in keyword_lower for term in ['outdoor', 'solar', 'weather', 'wireless']):
        scheme = {'bg': '#e8f5e8', 'accent': '#2e7d32', 'text': '#1b5e20'}  # Green nature theme

    # Security context - use security-focused colors
    elif any(term in keyword_lower for term in ['security', 'surveillance', 'monitoring', 'camera']):
        scheme = {'bg': '#e3f2fd', 'accent': '#1565c0', 'text': '#0d47a1'}  # Professional blue

    # Budget/affordable context - use value-oriented colors
    elif any(term in keyword_lower for term in ['cheap', 'budget', 'affordable', 'under']):
        scheme = {'bg': '#f3e5f5', 'accent': '#7b1fa2', 'text': '#4a148c'}  # Purple value theme

    # Clean category name for title with keyword context
    if any(term in keyword_lower for term in ['black friday', 'sale']):
        title = f"{category.replace('-', ' ').title()} - Special Deals"
    elif 'pet' in keyword_lower:
        title = f"Pet-Friendly {category.replace('-', ' ').title()}"
    elif 'outdoor' in keyword_lower:
        title = f"Outdoor {category.replace('-', ' ').title()}"
    elif 'security' in keyword_lower:
        title = f"Security {category.replace('-', ' ').title()}"
    else:
        title = category.replace('-', ' ').title()
        if not title.endswith('s') and not title.endswith('es'):
            title += 's'  # Pluralize if needed

    return make_info_card(
        title=title,
        bullet_points=features,
        output_path=output_path,
        bg_color=scheme['bg'],
        text_color=scheme['text'],
        accent_color=scheme['accent']
    )


def make_compatibility_card(device_name: str, protocols: List[str], output_path: str) -> str:
    """
    Create a compatibility information card
    
    Args:
        device_name: Name of the device
        protocols: List of supported protocols
        output_path: Output file path
        
    Returns:
        Output file path or empty string if failed
    """
    title = f"{device_name} Compatibility"
    
    bullet_points = [
        "Check hub requirements before purchase",
        "Ensure 2.4GHz WiFi network available",
        "Verify protocol compatibility"
    ]
    
    # Add protocol-specific points
    for protocol in protocols[:2]:  # Max 2 protocols to show
        if protocol.lower() in ['matter', 'thread']:
            bullet_points.append(f"✓ {protocol} certified for interoperability")
        elif protocol.lower() in ['zigbee', 'z-wave']:
            bullet_points.append(f"✓ {protocol} - requires compatible hub")
        elif protocol.lower() == 'wifi':
            bullet_points.append("✓ WiFi - works with most smart home apps")
    
    return make_info_card(
        title=title,
        bullet_points=bullet_points,
        output_path=output_path,
        accent_color='#6f42c1'  # Purple for compatibility
    )