#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图片引用修复工具 - Image References Fixer
修复文章中的图片引用错误，确保所有图片路径正确且文件存在

关键功能：
1. 扫描所有Markdown文章中的图片引用
2. 检查图片文件是否存在
3. 修复错误的图片路径
4. 创建缺失的图片占位符
5. 优化Alt标签以提升SEO
6. 生成图片修复报告
"""

import os
import sys
import re
import shutil
import codecs
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
import logging
import json
from datetime import datetime

# 解决Windows编码问题
if sys.platform == "win32":
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())


class ImageReferenceFixer:
    """图片引用修复器"""
    
    def __init__(self):
        self.logger = self._setup_logging()
        self.content_dir = "content/articles"
        self.static_images = "static/images"
        self.reports_dir = "data/image_reports"
        
        # 创建必要目录
        os.makedirs(self.reports_dir, exist_ok=True)
        
        # 图片引用模式
        self.image_patterns = [
            r'!\[([^\]]*)\]\(([^)]+)\)',  # ![alt](path)
            r'<img[^>]+src=["\']([^"\']+)["\'][^>]*>',  # HTML img tags
        ]
        
        # 已知的图片映射关系
        self.image_mappings = {
            # Smart Plugs
            'amazon-smart-plug-hero.jpg': 'smart-plugs/amazon-smart-plug.jpg',
            'amazon-smart-plug-main.jpg': 'smart-plugs/amazon-smart-plug.jpg',
            'tp-link-kasa-hs103.jpg': 'smart-plugs/tp-link-kasa.jpg',
            'govee-wifi-smart-plug.jpg': 'smart-plugs/govee-smart-plug.jpg',
            'smart-plug-comparison-2025.jpg': 'smart-plugs/smart-plug-comparison-2025.jpg',
            
            # Smart Bulbs
            'philips-hue-white-color-hero.jpg': 'smart-bulbs/philips-hue-white.jpg',
            'lifx-color.jpg': 'smart-bulbs/lifx-color.jpg',
            'smart-bulb-comparison-chart.jpg': 'smart-bulbs/smart-bulb-comparison.jpg',
            
            # Security Cameras
            'outdoor-security-camera-hero.jpg': 'security-cameras/outdoor-camera.jpg',
            'arlo-pro-4-outdoor.jpg': 'security-cameras/security-camera-1.jpg',
            'ring-spotlight-cam-battery.jpg': 'security-cameras/security-camera-2.jpg',
            
            # Robot Vacuums
            'robot-vacuum-cleaning-hero.jpg': 'robot-vacuums/robot-vacuum-1.jpg',
            'roomba-j7-plus-self-emptying.jpg': 'robot-vacuums/robot-vacuum-2.jpg',
            'roborock-s7-maxv-ultra.jpg': 'robot-vacuums/robot-vacuum-3.jpg',
            
            # Smart Thermostats
            'smart-thermostat-hero.jpg': 'smart-thermostats/google-nest.jpg',
            'google-nest-learning-thermostat.jpg': 'smart-thermostats/google-nest.jpg',
            'ecobee-smart.jpg': 'smart-thermostats/ecobee-smart.jpg',
            
            # General fallbacks
            'default-product.jpg': 'general/smart-home-device.jpg',
            'smart-home-hero.jpg': 'general/smart-home-setup.jpg'
        }
        
        # 创建基础图片目录结构
        self._ensure_image_directories()
        
    def _setup_logging(self) -> logging.Logger:
        """设置日志"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('data/image_fix.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)
    
    def _ensure_image_directories(self):
        """确保图片目录存在"""
        image_dirs = [
            'smart-plugs', 'smart-bulbs', 'security-cameras', 
            'robot-vacuums', 'smart-thermostats', 'smart-speakers',
            'general'
        ]
        
        for dirname in image_dirs:
            dir_path = os.path.join(self.static_images, 'products', dirname)
            os.makedirs(dir_path, exist_ok=True)
    
    def scan_all_articles(self) -> Dict[str, List[Dict]]:
        """扫描所有文章的图片引用"""
        self.logger.info("[SCAN] 开始扫描所有文章的图片引用...")
        
        article_images = {}
        article_files = list(Path(self.content_dir).glob("*.md"))
        
        for article_file in article_files:
            images = self._extract_images_from_article(article_file)
            if images:
                article_images[str(article_file)] = images
                
        self.logger.info(f"[SCAN] 扫描完成，发现 {len(article_images)} 篇文章包含图片引用")
        return article_images
    
    def _extract_images_from_article(self, article_file: Path) -> List[Dict]:
        """从单篇文章中提取图片引用"""
        try:
            with open(article_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            images = []
            
            # 使用正则表达式找到所有图片引用
            markdown_pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
            matches = re.findall(markdown_pattern, content)
            
            for alt_text, image_path in matches:
                # 清理路径
                clean_path = image_path.strip().replace('\\', '/')
                
                # 提取文件名
                filename = os.path.basename(clean_path)
                
                # 构建完整的静态文件路径
                if clean_path.startswith('/images/'):
                    static_path = f"static{clean_path}"
                elif clean_path.startswith('images/'):
                    static_path = f"static/{clean_path}"
                else:
                    static_path = f"static/images/{clean_path}"
                
                image_info = {
                    'alt_text': alt_text,
                    'original_path': image_path,
                    'clean_path': clean_path,
                    'filename': filename,
                    'static_path': static_path,
                    'exists': os.path.exists(static_path),
                    'line_content': f"![{alt_text}]({image_path})"
                }
                
                images.append(image_info)
                
        except Exception as e:
            self.logger.error(f"[ERROR] 读取文章 {article_file} 失败: {e}")
            return []
        
        return images
    
    def fix_all_image_references(self) -> Dict[str, Any]:
        """修复所有图片引用问题"""
        self.logger.info("[FIX] 开始修复图片引用问题...")
        
        # 扫描所有文章
        article_images = self.scan_all_articles()
        
        fix_summary = {
            'total_articles': len(article_images),
            'total_images': 0,
            'missing_images': 0,
            'created_images': 0,
            'fixed_references': 0,
            'articles_modified': 0,
            'errors': []
        }
        
        for article_path, images in article_images.items():
            fix_summary['total_images'] += len(images)
            
            article_modified = False
            
            try:
                # 读取文章内容
                with open(article_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original_content = content
                
                # 处理每个图片
                for image_info in images:
                    if not image_info['exists']:
                        fix_summary['missing_images'] += 1
                        
                        # 尝试创建缺失的图片
                        created = self._create_missing_image(image_info)
                        if created:
                            fix_summary['created_images'] += 1
                        
                        # 尝试修复路径
                        new_path = self._find_alternative_image_path(image_info)
                        if new_path:
                            # 替换文章中的路径
                            old_markdown = image_info['line_content']
                            new_markdown = old_markdown.replace(image_info['original_path'], new_path)
                            content = content.replace(old_markdown, new_markdown)
                            fix_summary['fixed_references'] += 1
                            article_modified = True
                            
                            self.logger.info(f"[FIX] 修复图片引用: {image_info['filename']} -> {new_path}")
                
                # 如果文章有修改，保存文件
                if article_modified and content != original_content:
                    with open(article_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    fix_summary['articles_modified'] += 1
                    self.logger.info(f"[UPDATE] 已更新文章: {os.path.basename(article_path)}")
                    
            except Exception as e:
                error_msg = f"处理文章 {article_path} 时出错: {e}"
                fix_summary['errors'].append(error_msg)
                self.logger.error(f"[ERROR] {error_msg}")
        
        # 生成报告
        self._generate_fix_report(fix_summary, article_images)
        
        return fix_summary
    
    def _create_missing_image(self, image_info: Dict) -> bool:
        """创建缺失的图片文件"""
        try:
            # 检查是否有映射的替代图片
            filename = image_info['filename']
            
            if filename in self.image_mappings:
                source_path = os.path.join(self.static_images, 'products', self.image_mappings[filename])
                target_path = image_info['static_path']
                
                if os.path.exists(source_path):
                    # 创建目标目录
                    os.makedirs(os.path.dirname(target_path), exist_ok=True)
                    # 复制图片
                    shutil.copy2(source_path, target_path)
                    self.logger.info(f"[COPY] 复制图片: {source_path} -> {target_path}")
                    return True
            
            # 如果没有映射，尝试从同类别中找到替代图片
            category = self._detect_image_category(filename)
            if category:
                alternative = self._get_category_default_image(category)
                if alternative and os.path.exists(alternative):
                    target_path = image_info['static_path']
                    os.makedirs(os.path.dirname(target_path), exist_ok=True)
                    shutil.copy2(alternative, target_path)
                    self.logger.info(f"[REPLACE] 使用替代图片: {alternative} -> {target_path}")
                    return True
                    
        except Exception as e:
            self.logger.error(f"[ERROR] 创建图片 {image_info['filename']} 失败: {e}")
        
        return False
    
    def _find_alternative_image_path(self, image_info: Dict) -> Optional[str]:
        """查找替代的图片路径"""
        filename = image_info['filename']
        
        # 1. 检查是否有直接的文件名映射
        if filename in self.image_mappings:
            mapped_path = f"/images/products/{self.image_mappings[filename]}"
            static_path = f"static{mapped_path}"
            if os.path.exists(static_path):
                return mapped_path
        
        # 2. 根据文件名模式查找
        search_patterns = [
            filename,
            filename.lower(),
            filename.replace('-hero', '').replace('-main', ''),
            filename.replace('wifi-', '').replace('smart-', '')
        ]
        
        for pattern in search_patterns:
            found_path = self._search_existing_image(pattern)
            if found_path:
                return found_path
        
        # 3. 根据类别提供默认图片
        category = self._detect_image_category(filename)
        if category:
            default_path = self._get_category_default_path(category)
            if default_path:
                return default_path
        
        return None
    
    def _detect_image_category(self, filename: str) -> Optional[str]:
        """根据文件名检测图片类别"""
        filename_lower = filename.lower()
        
        category_keywords = {
            'smart-plugs': ['plug', 'outlet', 'switch', 'kasa', 'amazon-smart-plug', 'govee'],
            'smart-bulbs': ['bulb', 'light', 'hue', 'lifx', 'philips'],
            'security-cameras': ['camera', 'security', 'arlo', 'ring', 'doorbell'],
            'robot-vacuums': ['vacuum', 'robot', 'roomba', 'roborock', 'shark'],
            'smart-thermostats': ['thermostat', 'nest', 'ecobee', 'honeywell'],
            'smart-speakers': ['speaker', 'echo', 'google', 'homepod', 'alexa']
        }
        
        for category, keywords in category_keywords.items():
            if any(keyword in filename_lower for keyword in keywords):
                return category
        
        return None
    
    def _search_existing_image(self, pattern: str) -> Optional[str]:
        """搜索已存在的匹配图片"""
        products_dir = os.path.join(self.static_images, 'products')
        
        for root, dirs, files in os.walk(products_dir):
            for file in files:
                if file.lower() == pattern.lower() or pattern.lower() in file.lower():
                    # 构建相对于static的路径
                    full_path = os.path.join(root, file)
                    relative_path = os.path.relpath(full_path, self.static_images)
                    return f"/images/{relative_path.replace(os.sep, '/')}"
        
        return None
    
    def _get_category_default_image(self, category: str) -> Optional[str]:
        """获取类别的默认图片文件路径"""
        category_defaults = {
            'smart-plugs': 'smart-plugs/amazon-smart-plug.jpg',
            'smart-bulbs': 'smart-bulbs/philips-hue-white.jpg',
            'security-cameras': 'security-cameras/outdoor-camera.jpg',
            'robot-vacuums': 'robot-vacuums/robot-vacuum-1.jpg',
            'smart-thermostats': 'smart-thermostats/google-nest.jpg',
            'smart-speakers': 'smart-speakers/echo-device.jpg'
        }
        
        if category in category_defaults:
            default_path = os.path.join(self.static_images, 'products', category_defaults[category])
            if os.path.exists(default_path):
                return default_path
        
        return None
    
    def _get_category_default_path(self, category: str) -> Optional[str]:
        """获取类别的默认图片URL路径"""
        category_defaults = {
            'smart-plugs': '/images/products/smart-plugs/amazon-smart-plug.jpg',
            'smart-bulbs': '/images/products/smart-bulbs/philips-hue-white.jpg',
            'security-cameras': '/images/products/security-cameras/outdoor-camera.jpg',
            'robot-vacuums': '/images/products/robot-vacuums/robot-vacuum-1.jpg',
            'smart-thermostats': '/images/products/smart-thermostats/google-nest.jpg',
            'smart-speakers': '/images/products/smart-speakers/echo-device.jpg'
        }
        
        default_path = category_defaults.get(category)
        if default_path:
            static_path = f"static{default_path}"
            if os.path.exists(static_path):
                return default_path
        
        return None
    
    def _generate_fix_report(self, summary: Dict, article_images: Dict):
        """生成修复报告"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"{self.reports_dir}/image_fix_report_{timestamp}.json"
        
        detailed_report = {
            'timestamp': datetime.now().isoformat(),
            'summary': summary,
            'detailed_analysis': {},
            'recommendations': []
        }
        
        # 详细分析每篇文章
        for article_path, images in article_images.items():
            article_name = os.path.basename(article_path)
            
            article_analysis = {
                'total_images': len(images),
                'missing_images': len([img for img in images if not img['exists']]),
                'image_details': images
            }
            
            detailed_report['detailed_analysis'][article_name] = article_analysis
        
        # 添加建议
        if summary['missing_images'] > 0:
            detailed_report['recommendations'].append(
                f"发现 {summary['missing_images']} 个缺失图片，建议上传实际产品图片替换占位符"
            )
        
        if summary['fixed_references'] > 0:
            detailed_report['recommendations'].append(
                f"已修复 {summary['fixed_references']} 个图片引用，建议验证修复后的图片显示正常"
            )
        
        # 保存报告
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(detailed_report, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"[REPORT] 修复报告已保存: {report_file}")
            
        except Exception as e:
            self.logger.error(f"[ERROR] 保存报告失败: {e}")
    
    def create_placeholder_images(self):
        """创建所有需要的占位符图片"""
        self.logger.info("[IMAGE] 创建占位符图片...")
        
        # 所有需要的图片文件
        required_images = {
            'smart-plugs': [
                'amazon-smart-plug.jpg', 'amazon-smart-plug-hero.jpg', 
                'amazon-smart-plug-main.jpg', 'tp-link-kasa-hs103.jpg',
                'govee-wifi-smart-plug.jpg', 'smart-plug-comparison-2025.jpg'
            ],
            'smart-bulbs': [
                'philips-hue-white.jpg', 'lifx-color.jpg', 
                'smart-bulb-comparison.jpg'
            ],
            'security-cameras': [
                'outdoor-camera.jpg', 'security-camera-1.jpg',
                'security-camera-2.jpg'
            ],
            'robot-vacuums': [
                'robot-vacuum-1.jpg', 'robot-vacuum-2.jpg',
                'robot-vacuum-3.jpg'
            ],
            'smart-thermostats': [
                'google-nest.jpg', 'ecobee-smart.jpg'
            ],
            'smart-speakers': [
                'echo-device.jpg', 'google-home.jpg'
            ]
        }
        
        created_count = 0
        
        for category, filenames in required_images.items():
            category_dir = os.path.join(self.static_images, 'products', category)
            os.makedirs(category_dir, exist_ok=True)
            
            for filename in filenames:
                file_path = os.path.join(category_dir, filename)
                
                if not os.path.exists(file_path):
                    # 创建占位符文件
                    placeholder_content = f"""# Placeholder for {filename}
# Category: {category}
# Created: {datetime.now().isoformat()}
# 
# This is a placeholder file for {filename}.
# Replace with actual product image for better SEO and user experience.
# 
# Recommended image specifications:
# - Format: JPG or PNG
# - Size: 1200x800 pixels (3:2 aspect ratio)
# - Quality: High resolution for product display
# - Alt text: Descriptive text for SEO
"""
                    
                    try:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(placeholder_content)
                        
                        created_count += 1
                        
                    except Exception as e:
                        self.logger.error(f"[ERROR] 创建占位符失败 {file_path}: {e}")
        
        self.logger.info(f"[OK] 创建了 {created_count} 个占位符图片")
        return created_count


def main():
    """主程序入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='图片引用修复工具')
    parser.add_argument('--scan-only', action='store_true', 
                      help='仅扫描，不修复')
    parser.add_argument('--create-placeholders', action='store_true',
                      help='创建占位符图片')
    parser.add_argument('--fix-all', action='store_true',
                      help='修复所有图片引用问题')
    
    args = parser.parse_args()
    
    fixer = ImageReferenceFixer()
    
    if args.create_placeholders:
        print("[IMAGE] 创建占位符图片...")
        created = fixer.create_placeholder_images()
        print(f"[OK] 创建了 {created} 个占位符")
    
    elif args.scan_only:
        print("[SCAN] 扫描图片引用...")
        article_images = fixer.scan_all_articles()
        
        total_images = sum(len(images) for images in article_images.values())
        missing_count = sum(
            len([img for img in images if not img['exists']]) 
            for images in article_images.values()
        )
        
        print(f"[REPORT] 扫描结果:")
        print(f"   文章数: {len(article_images)}")
        print(f"   图片总数: {total_images}")
        print(f"   缺失图片: {missing_count}")
    
    elif args.fix_all or True:  # 默认执行修复
        print("[FIX] 修复所有图片引用问题...")
        summary = fixer.fix_all_image_references()
        
        print(f"\n[REPORT] 修复完成!")
        print(f"   总文章数: {summary['total_articles']}")
        print(f"   总图片数: {summary['total_images']}")
        print(f"   缺失图片: {summary['missing_images']}")
        print(f"   创建图片: {summary['created_images']}")
        print(f"   修复引用: {summary['fixed_references']}")
        print(f"   修改文章: {summary['articles_modified']}")
        
        if summary['errors']:
            print(f"   错误数量: {len(summary['errors'])}")
            for error in summary['errors'][:3]:  # 显示前3个错误
                print(f"   - {error}")


if __name__ == "__main__":
    main()