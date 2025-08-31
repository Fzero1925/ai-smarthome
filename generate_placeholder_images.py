#!/usr/bin/env python3
"""
Generate placeholder images for smart home products
Creates simple colored rectangles with product names as temporary images
"""

from PIL import Image, ImageDraw, ImageFont
import os

# Product images needed
PRODUCTS = {
    "philips-hue-a19.jpg": {"color": "#4285F4", "text": "Philips Hue\nA19 Bulb"},
    "lifx-a19.jpg": {"color": "#34A853", "text": "LIFX A19\nSmart Bulb"},
    "govee-rgb.jpg": {"color": "#EA4335", "text": "Govee RGB\nSmart Bulb"},
    "amazon-smart-plug.jpg": {"color": "#FF9900", "text": "Amazon\nSmart Plug"},
    "kasa-hs103p4.jpg": {"color": "#00A8E6", "text": "Kasa Smart\nPlug 4-Pack"},
    "govee-smart-plug.jpg": {"color": "#9C27B0", "text": "Govee Smart\nPlug"},
    "smart-light-bulbs-hero.jpg": {"color": "#607D8B", "text": "Smart Light\nBulbs 2025"},
    "smart-plugs-alexa-hero.jpg": {"color": "#795548", "text": "Smart Plugs\nfor Alexa"}
}

def create_placeholder_image(filename, color, text, size=(400, 300)):
    """Create a placeholder image with colored background and text"""
    
    # Create image
    img = Image.new('RGB', size, color=color)
    draw = ImageDraw.Draw(img)
    
    try:
        # Try to use a system font
        font_size = 24
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        try:
            # Fallback to default font
            font = ImageFont.load_default()
        except:
            font = None
    
    if font:
        # Get text bounding box
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Center text
        x = (size[0] - text_width) // 2
        y = (size[1] - text_height) // 2
        
        # Draw white text with black outline for visibility
        outline_color = "black" if color != "#000000" else "white"
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                draw.text((x + dx, y + dy), text, font=font, fill=outline_color)
        
        draw.text((x, y), text, font=font, fill="white")
    
    return img

def main():
    """Generate all placeholder images"""
    
    output_dir = "static/images/products"
    os.makedirs(output_dir, exist_ok=True)
    
    # Also create hero images in main images directory
    hero_dir = "static/images"
    os.makedirs(hero_dir, exist_ok=True)
    
    print("🖼️ Generating placeholder product images...")
    
    for filename, config in PRODUCTS.items():
        # Determine output directory
        if "hero" in filename:
            output_path = os.path.join(hero_dir, filename)
        else:
            output_path = os.path.join(output_dir, filename)
        
        # Create and save image
        img = create_placeholder_image(filename, config["color"], config["text"])
        img.save(output_path, "JPEG", quality=90, optimize=True)
        
        print(f"  ✅ Created: {output_path}")
    
    print(f"\n🎉 Successfully generated {len(PRODUCTS)} placeholder images!")
    print("💡 These are temporary placeholders. Replace with real product images when available.")

if __name__ == "__main__":
    main()