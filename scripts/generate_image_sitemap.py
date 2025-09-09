#!/usr/bin/env python3
"""
Enhanced Image Sitemap Generator v2 
Automatically generates comprehensive image sitemaps for SEO optimization
Integrated with configuration system, quality filtering, and robots.txt management
"""

import os
import sys
import codecs
import yaml
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
import xml.etree.ElementTree as ET

# 解决Windows编码问题
if sys.platform == "win32":
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class EnhancedImageSitemapGenerator:
    """v2 Enhanced Image Sitemap Generator with configuration and quality filtering"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize with configuration"""
        self.config = self._load_config(config_path)
        self.sitemap_config = self.config.get('sitemap', {})
        self.quality_config = self.config.get('quality', {})
        
        # Base URL configuration
        self.base_urls = self.config.get('base_urls', {})
        self.environment = self.config.get('environment', 'production')
        self.base_url = self.base_urls.get(self.environment, "https://www.ai-smarthomehub.com")
        
        print(f"✅ Image sitemap generator initialized")
        print(f"🌐 Environment: {self.environment}")
        print(f"🔗 Base URL: {self.base_url}")
    
    def _load_config(self, config_path: Optional[str] = None) -> Dict:
        """Load configuration from YAML file"""
        if not config_path:
            config_path = project_root / 'image_config.yml'
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                print(f"✅ Loaded config from {config_path}")
                return config
        except Exception as e:
            print(f"⚠️ Failed to load config, using defaults: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """Default configuration"""
        return {
            'environment': 'production',
            'base_urls': {
                'production': 'https://www.ai-smarthomehub.com',
                'development': 'http://localhost:1313'
            },
            'sitemap': {
                'generate_image_sitemap': True,
                'sitemap_file': 'static/sitemap-images.xml',
                'include_in_robots': True,
                'min_quality_for_sitemap': 0.6,
                'exclude_infographics': False,
                'update_main_sitemap': True
            },
            'quality': {
                'min_width': 800,
                'min_height': 600,
                'max_usage_count': 3
            }
        }
    
    def normalize_base_url(self, url: str) -> str:
        """v2 Normalize base URL to ensure proper format"""
        if url.startswith('http'):
            return url
        return self.base_url.rstrip('/') + '/' + url.lstrip('/')
    
    def generate_image_sitemap(self) -> Tuple[str, int]:
        """Generate comprehensive image sitemap with v2 enhancements"""
        
        if not self.sitemap_config.get('generate_image_sitemap', True):
            print("🚫 Image sitemap generation is disabled in configuration")
            return "", 0
        
        print("🚀 Starting enhanced image sitemap generation...")
        
        # Get quality threshold
        min_quality = self.sitemap_config.get('min_quality_for_sitemap', 0.6)
        exclude_infographics = self.sitemap_config.get('exclude_infographics', False)
        
        # Define image directories to scan
        image_dirs = [
            "static/images/products/smart-plugs",
            "static/images/products/smart-bulbs", 
            "static/images/products/smart-thermostats",
            "static/images/products/security-cameras",
            "static/images/products/robot-vacuums",
            "static/images/products/smart-speakers",
            "static/images/general",
            "static/images"  # General images
        ]
        
        # Supported image formats
        image_extensions = {'.jpg', '.jpeg', '.png', '.webp', '.gif'}
        
        # Create root element
        urlset = ET.Element('urlset')
        urlset.set('xmlns', 'http://www.sitemaps.org/schemas/sitemap/0.9')
        urlset.set('xmlns:image', 'http://www.google.com/schemas/sitemap-image/1.1')
        
        current_time = datetime.now().isoformat()
        processed_images = 0
        quality_filtered = 0
        
        # Process each image directory
        for image_dir in image_dirs:
            if not os.path.exists(image_dir):
                continue
                
            print(f"📁 Scanning {image_dir}...")
            
            for root, dirs, files in os.walk(image_dir):
                for file in files:
                    if Path(file).suffix.lower() in image_extensions:
                        file_path = Path(root) / file
                        
                        # Quality filtering
                        quality_score = self._calculate_image_quality_score(file_path)
                        
                        if quality_score < min_quality:
                            quality_filtered += 1
                            continue
                        
                        # Infographic filtering
                        if exclude_infographics and self._is_infographic(file_path):
                            continue
                        
                        # Create URL element
                        url = ET.SubElement(urlset, 'url')
                        
                        # Calculate relative path and URL
                        rel_path = os.path.relpath(file_path, 'static')
                        image_url = self.normalize_base_url(rel_path.replace(os.sep, '/'))
                        
                        # Add location
                        loc = ET.SubElement(url, 'loc')
                        loc.text = image_url
                        
                        # Add image-specific data
                        image = ET.SubElement(url, 'image:image')
                        image_loc = ET.SubElement(image, 'image:loc')
                        image_loc.text = image_url
                        
                        # Generate descriptive caption based on filename and path
                        caption = self._generate_enhanced_caption(file, root)
                        if caption:
                            image_caption = ET.SubElement(image, 'image:caption')
                            image_caption.text = caption
                        
                        # Add title
                        title = self._generate_enhanced_title(file, root)
                        if title:
                            image_title = ET.SubElement(image, 'image:title')
                            image_title.text = title
                        
                        # Add last modification date
                        lastmod = ET.SubElement(url, 'lastmod')
                        try:
                            mod_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                            lastmod.text = mod_time.isoformat()
                        except:
                            lastmod.text = current_time
                        
                        # Set change frequency and priority
                        changefreq = ET.SubElement(url, 'changefreq')
                        changefreq.text = 'weekly'
                        
                        priority = ET.SubElement(url, 'priority')
                        priority.text = self._calculate_enhanced_priority(root, file, quality_score)
                        
                        processed_images += 1
        
        # Write XML to file with proper formatting
        tree = ET.ElementTree(urlset)
        ET.indent(tree, space="  ", level=0)  # Pretty formatting
        
        output_file = self.sitemap_config.get('sitemap_file', 'static/sitemap-images.xml')
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        tree.write(output_path, encoding='utf-8', xml_declaration=True)
        
        # Count images in sitemap
        image_count = len(urlset.findall('url'))
        
        print(f"✅ Generated image sitemap with {image_count} high-quality images")
        print(f"📊 Quality filtered: {quality_filtered} images below threshold ({min_quality})")
        print(f"📁 Output: {output_file}")
        
        # Update robots.txt if configured
        if self.sitemap_config.get('include_in_robots', True):
            self._update_robots_txt(output_file)
        
        # Update main sitemap if configured
        if self.sitemap_config.get('update_main_sitemap', True):
            self._update_main_sitemap(output_file)
        
        return str(output_path), image_count
    
    def _calculate_image_quality_score(self, file_path: Path) -> float:
        """Calculate quality score for image based on multiple factors"""
        try:
            # File size check
            file_size = file_path.stat().st_size
            min_size = self.quality_config.get('min_file_size', 50000)  # 50KB
            max_size = self.quality_config.get('max_file_size', 2000000)  # 2MB
            
            size_score = 1.0
            if file_size < min_size:
                size_score = 0.3  # Too small
            elif file_size > max_size:
                size_score = 0.7  # Too large
            
            # Filename quality (descriptive vs generic)
            filename = file_path.name.lower()
            filename_score = 1.0
            
            generic_patterns = ['image', 'img', 'photo', 'pic', 'temp', 'test', 'untitled']
            if any(pattern in filename for pattern in generic_patterns):
                filename_score = 0.4
            
            # Category relevance
            category_score = 1.0
            if 'smart' in filename or any(cat in str(file_path) for cat in ['smart-plugs', 'smart-bulbs']):
                category_score = 1.0
            else:
                category_score = 0.6
            
            # Combined score
            overall_score = (size_score * 0.4 + filename_score * 0.3 + category_score * 0.3)
            return min(1.0, overall_score)
            
        except Exception:
            return 0.5  # Default score
    
    def _is_infographic(self, file_path: Path) -> bool:
        """Check if image is a generated infographic"""
        filename = file_path.name.lower()
        return any(pattern in filename for pattern in ['generated_', 'infographic', 'chart', 'graph'])
    
    def _generate_enhanced_caption(self, filename: str, directory: str) -> str:
        """Generate enhanced SEO-optimized caption for images"""
        # Extract product category from directory path
        category_map = {
            'smart-plugs': 'smart plug',
            'smart-bulbs': 'smart bulb',
            'smart-thermostats': 'smart thermostat',
            'security-cameras': 'security camera',
            'robot-vacuums': 'robot vacuum',
            'smart-speakers': 'smart speaker'
        }
        
        category = 'smart home device'
        for key, value in category_map.items():
            if key in directory:
                category = value
                break
        
        # Extract product name from filename
        name = filename.replace('-', ' ').replace('_', ' ')
        name = os.path.splitext(name)[0].title()
        
        # Enhanced caption generation with more patterns
        filename_lower = filename.lower()
        
        if 'amazon' in filename_lower:
            return f"Amazon {name} - Professional {category} review and buying guide for smart home automation"
        elif 'philips' in filename_lower:
            return f"Philips {name} - Premium {category} with advanced features and smart home integration"
        elif 'google' in filename_lower:
            return f"Google {name} - AI-powered {category} with voice control and smart home compatibility"
        elif 'tp-link' in filename_lower:
            return f"TP-Link {name} - Reliable {category} with Wi-Fi connectivity and app control"
        elif 'comparison' in filename_lower:
            return f"{category.title()} comparison guide - Compare top models, features, and prices for smart home setup"
        elif 'installation' in filename_lower:
            return f"{category.title()} installation guide - Step-by-step setup instructions for smart home integration"
        elif 'setup' in filename_lower:
            return f"{category.title()} setup tutorial - Easy configuration guide for smart home automation"
        elif 'hero' in filename_lower or 'main' in filename_lower:
            return f"{name} - Complete {category} overview with specifications and smart home compatibility"
        else:
            return f"{name} - {category.title()} review with detailed specifications and smart home integration guide"
    
    def _generate_enhanced_title(self, filename: str, directory: str) -> str:
        """Generate enhanced SEO-optimized title for images"""
        # Extract base name
        base_name = os.path.splitext(filename)[0]
        title = base_name.replace('-', ' ').replace('_', ' ').title()
        
        # Enhanced category context
        if 'smart-plugs' in directory:
            return f"{title} - Smart Plug for Home Automation"
        elif 'smart-bulbs' in directory:
            return f"{title} - Smart LED Bulb with App Control"
        elif 'smart-thermostats' in directory:
            return f"{title} - Smart Thermostat for Energy Savings"
        elif 'security-cameras' in directory:
            return f"{title} - Smart Security Camera System"
        elif 'robot-vacuums' in directory:
            return f"{title} - Robot Vacuum for Smart Cleaning"
        elif 'smart-speakers' in directory:
            return f"{title} - Smart Speaker with Voice Assistant"
        else:
            return f"{title} - Smart Home Device Review"
    
    def _calculate_enhanced_priority(self, directory: str, filename: str, quality_score: float) -> str:
        """Calculate enhanced SEO priority for images based on multiple factors"""
        base_priority = 0.5
        
        # Category-based priority
        high_value_categories = ['smart-plugs', 'smart-bulbs', 'smart-thermostats']
        if any(cat in directory for cat in high_value_categories):
            base_priority = 0.7
        
        # Content type bonuses
        filename_lower = filename.lower()
        if 'comparison' in filename_lower:
            base_priority += 0.2  # Comparison content is high value
        elif 'hero' in filename_lower or 'main' in filename_lower:
            base_priority += 0.15  # Hero images are important
        elif any(brand in filename_lower for brand in ['amazon', 'philips', 'google', 'tp-link']):
            base_priority += 0.1  # Brand products are important
        
        # Quality score influence
        base_priority = base_priority * quality_score
        
        # Cap at 1.0 and format
        final_priority = min(1.0, base_priority)
        return f"{final_priority:.1f}"
    
    def _update_robots_txt(self, sitemap_file: str):
        """Update robots.txt with image sitemap reference"""
        try:
            robots_file = Path("static/robots.txt")
            sitemap_url = self.normalize_base_url(sitemap_file.replace('static/', ''))
            sitemap_line = f"Sitemap: {sitemap_url}\n"
            
            # Read existing robots.txt
            existing_content = ""
            if robots_file.exists():
                with open(robots_file, 'r', encoding='utf-8') as f:
                    existing_content = f.read()
            
            # Check if sitemap already exists
            if sitemap_url not in existing_content:
                # Append sitemap reference
                with open(robots_file, 'a', encoding='utf-8') as f:
                    if existing_content and not existing_content.endswith('\n'):
                        f.write('\n')
                    f.write(sitemap_line)
                
                print(f"🤖 Updated robots.txt with image sitemap reference")
            else:
                print(f"🤖 Robots.txt already contains image sitemap reference")
                
        except Exception as e:
            print(f"⚠️ Failed to update robots.txt: {e}")
    
    def _update_main_sitemap(self, sitemap_file: str):
        """Update main sitemap index with image sitemap reference"""
        try:
            main_sitemap = Path("static/sitemap.xml")
            if not main_sitemap.exists():
                print(f"⚠️ Main sitemap not found, skipping sitemap index update")
                return
            
            # Parse existing sitemap
            tree = ET.parse(main_sitemap)
            root = tree.getroot()
            
            # Check if image sitemap already exists
            sitemap_url = self.normalize_base_url(sitemap_file.replace('static/', ''))
            
            # Find sitemapindex or urlset
            if root.tag.endswith('sitemapindex'):
                # Sitemap index format
                for sitemap in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}sitemap'):
                    loc = sitemap.find('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
                    if loc is not None and sitemap_url in loc.text:
                        print(f"🗺️ Image sitemap already in main sitemap index")
                        return
                
                # Add new sitemap entry
                sitemap_elem = ET.SubElement(root, '{http://www.sitemaps.org/schemas/sitemap/0.9}sitemap')
                loc_elem = ET.SubElement(sitemap_elem, '{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
                loc_elem.text = sitemap_url
                lastmod_elem = ET.SubElement(sitemap_elem, '{http://www.sitemaps.org/schemas/sitemap/0.9}lastmod')
                lastmod_elem.text = datetime.now().isoformat()
                
                tree.write(main_sitemap, encoding='utf-8', xml_declaration=True)
                print(f"🗺️ Added image sitemap to main sitemap index")
            
        except Exception as e:
            print(f"⚠️ Failed to update main sitemap: {e}")


def generate_image_sitemap():
    """Legacy compatibility function"""
    generator = EnhancedImageSitemapGenerator()
    return generator.generate_image_sitemap()

def generate_image_caption(filename, directory):
    """Legacy compatibility function - Generate SEO-optimized caption for images"""
    generator = EnhancedImageSitemapGenerator()
    return generator._generate_enhanced_caption(filename, directory)

def generate_image_title(filename, directory):
    """Legacy compatibility function - Generate SEO-optimized title for images"""
    generator = EnhancedImageSitemapGenerator()
    return generator._generate_enhanced_title(filename, directory)

def calculate_image_priority(directory, filename):
    """Legacy compatibility function - Calculate SEO priority for images"""
    generator = EnhancedImageSitemapGenerator()
    quality_score = 0.8  # Default quality score for legacy calls
    return generator._calculate_enhanced_priority(directory, filename, quality_score)


# === v2: Enhanced Utility Functions & CLI Interface ===

def normalize_base_url(url: str) -> str:
    """v2 Helper function - Normalize base URL (backward compatibility)"""
    generator = EnhancedImageSitemapGenerator()
    return generator.normalize_base_url(url)

def batch_generate_sitemaps(config_dir: str = ".", environments: List[str] = None) -> Dict[str, Tuple[str, int]]:
    """v2 Batch generate image sitemaps for multiple environments"""
    if not environments:
        environments = ['production', 'development']
    
    results = {}
    
    for env in environments:
        print(f"\n🌐 Generating sitemap for {env} environment...")
        
        # Create temporary config for this environment
        config_path = Path(config_dir) / 'image_config.yml'
        
        try:
            generator = EnhancedImageSitemapGenerator(str(config_path))
            
            # Override environment
            generator.environment = env
            generator.base_url = generator.base_urls.get(env, f"https://{env}.ai-smarthomehub.com")
            
            output_file, count = generator.generate_image_sitemap()
            results[env] = (output_file, count)
            
        except Exception as e:
            print(f"❌ Failed to generate sitemap for {env}: {e}")
            results[env] = ("", 0)
    
    return results

def validate_sitemap(sitemap_file: str) -> Dict[str, Any]:
    """v2 Validate generated image sitemap"""
    validation_result = {
        'valid': False,
        'total_images': 0,
        'errors': [],
        'warnings': [],
        'quality_metrics': {}
    }
    
    try:
        if not os.path.exists(sitemap_file):
            validation_result['errors'].append(f"Sitemap file not found: {sitemap_file}")
            return validation_result
        
        # Parse XML
        tree = ET.parse(sitemap_file)
        root = tree.getroot()
        
        # Check XML structure
        if not root.tag.endswith('urlset'):
            validation_result['errors'].append("Invalid XML structure - missing urlset root element")
            return validation_result
        
        # Count URLs and images
        urls = root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}url')
        images = root.findall('.//{http://www.google.com/schemas/sitemap-image/1.1}image')
        
        validation_result['total_images'] = len(images)
        validation_result['total_urls'] = len(urls)
        
        # Quality checks
        if len(images) == 0:
            validation_result['warnings'].append("No images found in sitemap")
        elif len(images) < 5:
            validation_result['warnings'].append(f"Very few images in sitemap: {len(images)}")
        
        # Check for required elements
        missing_captions = 0
        missing_titles = 0
        
        for image in images:
            if not image.find('.//{http://www.google.com/schemas/sitemap-image/1.1}caption'):
                missing_captions += 1
            if not image.find('.//{http://www.google.com/schemas/sitemap-image/1.1}title'):
                missing_titles += 1
        
        if missing_captions > 0:
            validation_result['warnings'].append(f"{missing_captions} images missing captions")
        if missing_titles > 0:
            validation_result['warnings'].append(f"{missing_titles} images missing titles")
        
        validation_result['quality_metrics'] = {
            'caption_coverage': (len(images) - missing_captions) / len(images) if len(images) > 0 else 0,
            'title_coverage': (len(images) - missing_titles) / len(images) if len(images) > 0 else 0
        }
        
        validation_result['valid'] = len(validation_result['errors']) == 0
        
    except ET.ParseError as e:
        validation_result['errors'].append(f"XML parsing error: {e}")
    except Exception as e:
        validation_result['errors'].append(f"Validation error: {e}")
    
    return validation_result

def generate_sitemap_report(sitemap_file: str, output_file: str = None) -> str:
    """v2 Generate comprehensive sitemap report"""
    validation = validate_sitemap(sitemap_file)
    
    if not output_file:
        output_file = sitemap_file.replace('.xml', '_report.html')
    
    # Generate HTML report
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Image Sitemap Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background: #f5f5f5; padding: 15px; border-radius: 5px; }}
        .valid {{ color: green; }}
        .invalid {{ color: red; }}
        .warning {{ color: orange; }}
        .metrics {{ background: #fff; border: 1px solid #ddd; padding: 10px; margin: 10px 0; }}
        .metric {{ display: inline-block; margin: 10px; text-align: center; }}
        .metric-value {{ font-size: 24px; font-weight: bold; }}
        .metric-label {{ font-size: 12px; color: #666; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Image Sitemap Report</h1>
        <p><strong>File:</strong> {sitemap_file}</p>
        <p><strong>Generated:</strong> {datetime.now().isoformat()}</p>
        <p><strong>Status:</strong> <span class="{'valid' if validation['valid'] else 'invalid'}">
            {'✅ Valid' if validation['valid'] else '❌ Invalid'}
        </span></p>
    </div>
    
    <div class="metrics">
        <div class="metric">
            <div class="metric-value">{validation['total_images']}</div>
            <div class="metric-label">Total Images</div>
        </div>
        <div class="metric">
            <div class="metric-value">{validation.get('total_urls', 0)}</div>
            <div class="metric-label">Total URLs</div>
        </div>
        <div class="metric">
            <div class="metric-value">{validation.get('quality_metrics', {}).get('caption_coverage', 0):.1%}</div>
            <div class="metric-label">Caption Coverage</div>
        </div>
        <div class="metric">
            <div class="metric-value">{validation.get('quality_metrics', {}).get('title_coverage', 0):.1%}</div>
            <div class="metric-label">Title Coverage</div>
        </div>
    </div>
    
    {'<h2>Errors</h2><ul>' + ''.join([f'<li class="invalid">{error}</li>' for error in validation['errors']]) + '</ul>' if validation['errors'] else ''}
    {'<h2>Warnings</h2><ul>' + ''.join([f'<li class="warning">{warning}</li>' for warning in validation['warnings']]) + '</ul>' if validation['warnings'] else ''}
    
</body>
</html>
    """
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"📄 Sitemap report generated: {output_file}")
    return output_file


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Enhanced Image Sitemap Generator v2')
    parser.add_argument('--config', help='Path to configuration file')
    parser.add_argument('--environment', choices=['production', 'development', 'staging'], 
                        help='Environment to generate for')
    parser.add_argument('--validate', help='Validate existing sitemap file')
    parser.add_argument('--report', help='Generate sitemap report for file')
    parser.add_argument('--batch', action='store_true', help='Generate for all environments')
    parser.add_argument('--output', help='Output file path')
    
    args = parser.parse_args()
    
    if args.validate:
        print(f"🔍 Validating sitemap: {args.validate}")
        validation = validate_sitemap(args.validate)
        
        print(f"📊 Validation Results:")
        print(f"  Status: {'✅ Valid' if validation['valid'] else '❌ Invalid'}")
        print(f"  Images: {validation['total_images']}")
        print(f"  URLs: {validation.get('total_urls', 0)}")
        
        if validation['errors']:
            print(f"  ❌ Errors: {len(validation['errors'])}")
            for error in validation['errors']:
                print(f"    • {error}")
        
        if validation['warnings']:
            print(f"  ⚠️ Warnings: {len(validation['warnings'])}")
            for warning in validation['warnings']:
                print(f"    • {warning}")
        
        sys.exit(0 if validation['valid'] else 1)
    
    elif args.report:
        print(f"📄 Generating report for: {args.report}")
        report_file = generate_sitemap_report(args.report, args.output)
        print(f"✅ Report generated: {report_file}")
        sys.exit(0)
    
    elif args.batch:
        print("🔄 Batch generating sitemaps for all environments...")
        results = batch_generate_sitemaps(config_dir=".")
        
        print(f"\n📊 Batch Results:")
        total_images = 0
        for env, (output_file, count) in results.items():
            if count > 0:
                print(f"  ✅ {env}: {count} images in {output_file}")
                total_images += count
            else:
                print(f"  ❌ {env}: Failed to generate")
        
        print(f"📈 Total: {total_images} images across all environments")
        sys.exit(0)
    
    else:
        # Standard sitemap generation
        try:
            generator = EnhancedImageSitemapGenerator(config_path=args.config)
            
            # Override environment if specified
            if args.environment:
                generator.environment = args.environment
                generator.base_url = generator.base_urls.get(args.environment, 
                                                           f"https://{args.environment}.ai-smarthomehub.com")
            
            output_file, count = generator.generate_image_sitemap()
            
            print(f"\n🎉 Success!")
            print(f"📁 Generated: {output_file}")
            print(f"🖼️ Images: {count}")
            print(f"🌐 Base URL: {generator.base_url}")
            
        except Exception as e:
            print(f"❌ Error generating image sitemap: {e}")
            sys.exit(1)