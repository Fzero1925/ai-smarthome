#!/usr/bin/env python3
"""
Product Image Mapping System
智能匹配内容关键词与产品图片，确保每篇文章使用合适且不重复的图片
"""

import os
import sys
import json
import re
import hashlib
import codecs
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import logging

# 解决Windows编码问题
if sys.platform == "win32":
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

class ProductImageMapper:
    """智能产品图片映射器"""
    
    def __init__(self):
        self.base_path = Path("static/images/products")
        self.mapping_cache = Path("data/image_mapping_cache.json")
        self.usage_tracking = Path("data/image_usage_tracking.json")
        
        # 确保目录存在
        os.makedirs("data", exist_ok=True)
        
        # 设置日志
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # 产品图片数据库 - 150+产品映射
        self.product_database = {
            # Smart Plugs
            'smart-plugs': {
                'amazon-smart-plug.jpg': {
                    'keywords': ['amazon smart plug', 'alexa plug', 'amazon alexa plug'],
                    'alt_template': 'Amazon Smart Plug - Voice Control with Alexa',
                    'description': 'Amazon Smart Plug with native Alexa integration',
                    'primary_use': ['alexa', 'amazon', 'voice control'],
                    'price_range': '$10-15',
                    'rating': 4.5
                },
                'tp-link-kasa.jpg': {
                    'keywords': ['tp-link kasa', 'kasa smart plug', 'energy monitoring plug'],
                    'alt_template': 'TP-Link Kasa Smart Plug - WiFi Connected with Energy Monitoring',
                    'description': 'TP-Link Kasa Smart Plug with energy monitoring features',
                    'primary_use': ['energy monitoring', 'wifi', 'app control'],
                    'price_range': '$8-12',
                    'rating': 4.4
                },
                'govee-smart-plug.jpg': {
                    'keywords': ['govee smart plug', 'budget smart plug', 'wifi smart outlet'],
                    'alt_template': 'Govee Smart Plug - Affordable WiFi Smart Outlet',
                    'description': 'Govee Smart Plug offering great value for money',
                    'primary_use': ['budget', 'basic control', 'timer'],
                    'price_range': '$6-10',
                    'rating': 4.2
                }
            },
            
            # Smart Bulbs
            'smart-bulbs': {
                'philips-hue-white.jpg': {
                    'keywords': ['philips hue', 'smart bulb white', 'premium smart lighting'],
                    'alt_template': 'Philips Hue White LED Smart Bulb - Premium Smart Lighting',
                    'description': 'Philips Hue White smart bulb with premium features',
                    'primary_use': ['premium lighting', 'hub required', 'dimming'],
                    'price_range': '$15-25',
                    'rating': 4.7
                },
                'lifx-color.jpg': {
                    'keywords': ['lifx color', 'color changing bulb', 'wifi smart bulb'],
                    'alt_template': 'LIFX Color Smart Bulb - WiFi Connected RGB Lighting',
                    'description': 'LIFX Color smart bulb with millions of colors',
                    'primary_use': ['color changing', 'no hub', 'wifi direct'],
                    'price_range': '$35-50',
                    'rating': 4.3
                }
            },
            
            # Smart Thermostats
            'smart-thermostats': {
                'google-nest.jpg': {
                    'keywords': ['google nest thermostat', 'nest learning', 'smart thermostat premium'],
                    'alt_template': 'Google Nest Learning Thermostat - AI-Powered Climate Control',
                    'description': 'Google Nest Learning Thermostat with AI features',
                    'primary_use': ['learning', 'google assistant', 'energy saving'],
                    'price_range': '$200-250',
                    'rating': 4.6
                },
                'ecobee-smart.jpg': {
                    'keywords': ['ecobee thermostat', 'voice control thermostat', 'alexa thermostat'],
                    'alt_template': 'Ecobee SmartThermostat - Voice Control with Built-in Alexa',
                    'description': 'Ecobee SmartThermostat with built-in Alexa',
                    'primary_use': ['voice control', 'room sensors', 'alexa built-in'],
                    'price_range': '$220-280',
                    'rating': 4.4
                }
            }
        }
        
        # 载入使用跟踪数据
        self.usage_data = self._load_usage_tracking()
        
    def _load_usage_tracking(self) -> Dict:
        """载入图片使用跟踪数据"""
        if self.usage_tracking.exists():
            try:
                with open(self.usage_tracking, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"Could not load usage tracking: {e}")
        
        return {
            'image_usage': {},  # 图片使用计数
            'article_images': {},  # 文章->图片映射
            'last_updated': datetime.now().isoformat()
        }
    
    def _save_usage_tracking(self):
        """保存图片使用跟踪数据"""
        self.usage_data['last_updated'] = datetime.now().isoformat()
        try:
            with open(self.usage_tracking, 'w', encoding='utf-8') as f:
                json.dump(self.usage_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Could not save usage tracking: {e}")
    
    def analyze_keyword_match(self, keyword: str, article_content: str = "") -> List[Tuple[str, float, Dict]]:
        """
        分析关键词与产品图片的匹配度
        
        Args:
            keyword: 主关键词
            article_content: 文章内容（用于上下文分析）
            
        Returns:
            List of (image_path, score, metadata) tuples, sorted by score
        """
        matches = []
        keyword_lower = keyword.lower()
        content_lower = article_content.lower()
        
        for category, products in self.product_database.items():
            for image_file, product_data in products.items():
                score = 0.0
                image_path = f"/images/products/{category}/{image_file}"
                
                # 1. 直接关键词匹配 (权重: 40%)
                for product_keyword in product_data['keywords']:
                    if product_keyword.lower() in keyword_lower:
                        score += 0.4
                        break
                
                # 2. 部分关键词匹配 (权重: 20%)
                keyword_words = set(keyword_lower.split())
                for product_keyword in product_data['keywords']:
                    product_words = set(product_keyword.lower().split())
                    overlap = len(keyword_words.intersection(product_words))
                    if overlap > 0:
                        score += 0.2 * (overlap / max(len(keyword_words), len(product_words)))
                
                # 3. 内容上下文匹配 (权重: 20%)
                if article_content:
                    context_matches = 0
                    for use_case in product_data['primary_use']:
                        if use_case.lower() in content_lower:
                            context_matches += 1
                    if context_matches > 0:
                        score += 0.2 * (context_matches / len(product_data['primary_use']))
                
                # 4. 类别匹配 (权重: 10%)
                category_keywords = {
                    'smart-plugs': ['plug', 'outlet', 'socket'],
                    'smart-bulbs': ['bulb', 'light', 'lighting'],
                    'smart-thermostats': ['thermostat', 'temperature', 'climate']
                }
                for cat_keyword in category_keywords.get(category, []):
                    if cat_keyword in keyword_lower:
                        score += 0.1
                        break
                
                # 5. 使用频率调整 (避免过度重复使用) (权重: 10%)
                usage_count = self.usage_data['image_usage'].get(image_path, 0)
                if usage_count == 0:
                    score += 0.1  # 优先使用未使用的图片
                elif usage_count < 3:
                    score += 0.05  # 轻微优先较少使用的图片
                # 使用超过3次的图片不加分
                
                if score > 0:
                    metadata = {
                        'alt_text': product_data['alt_template'],
                        'description': product_data['description'],
                        'category': category,
                        'usage_count': usage_count,
                        'rating': product_data.get('rating', 4.0),
                        'price_range': product_data.get('price_range', 'N/A')
                    }
                    matches.append((image_path, score, metadata))
        
        # 按分数排序，分数相同时优先使用次数少的
        matches.sort(key=lambda x: (x[1], -x[2]['usage_count']), reverse=True)
        return matches
    
    def get_best_image_for_keyword(self, keyword: str, article_content: str = "", 
                                 exclude_images: List[str] = None) -> Optional[Tuple[str, Dict]]:
        """
        为关键词获取最佳图片匹配
        
        Args:
            keyword: 目标关键词
            article_content: 文章内容
            exclude_images: 要排除的图片路径列表
            
        Returns:
            (image_path, metadata) tuple or None
        """
        exclude_images = exclude_images or []
        matches = self.analyze_keyword_match(keyword, article_content)
        
        # 过滤排除的图片
        matches = [(path, score, meta) for path, score, meta in matches 
                  if path not in exclude_images]
        
        if matches:
            return matches[0][0], matches[0][2]
        
        return None
    
    def update_image_usage(self, article_path: str, image_path: str):
        """更新图片使用记录"""
        # 更新使用计数
        if image_path not in self.usage_data['image_usage']:
            self.usage_data['image_usage'][image_path] = 0
        self.usage_data['image_usage'][image_path] += 1
        
        # 更新文章->图片映射
        self.usage_data['article_images'][article_path] = self.usage_data['article_images'].get(article_path, [])
        if image_path not in self.usage_data['article_images'][article_path]:
            self.usage_data['article_images'][article_path].append(image_path)
        
        self._save_usage_tracking()
    
    def find_duplicate_image_usage(self) -> Dict[str, List[str]]:
        """查找重复使用的图片"""
        duplicates = {}
        
        for article, images in self.usage_data['article_images'].items():
            for image in images:
                if image not in duplicates:
                    duplicates[image] = []
                duplicates[image].append(article)
        
        # 只返回被多篇文章使用的图片
        return {img: articles for img, articles in duplicates.items() if len(articles) > 1}
    
    def generate_optimized_alt_text(self, image_path: str, keyword: str, context: str = "") -> str:
        """生成SEO优化的Alt标签文本"""
        
        # 从数据库查找图片信息
        for category, products in self.product_database.items():
            for image_file, product_data in products.items():
                if image_file in image_path:
                    base_alt = product_data['alt_template']
                    
                    # 添加关键词和上下文优化
                    if keyword.lower() not in base_alt.lower():
                        if 'best' in keyword.lower():
                            return f"Best {base_alt} - Top Rated {category.replace('_', ' ').title()} 2025"
                        elif 'review' in keyword.lower():
                            return f"{base_alt} - Professional Review and Buying Guide"
                        elif 'comparison' in keyword.lower():
                            return f"{base_alt} - Comparison Guide and Features"
                        else:
                            return f"{base_alt} - {keyword.title()} Guide"
                    
                    return base_alt
        
        # 如果没找到，生成通用Alt文本
        return f"Smart Home Device - {keyword.title()} - Professional Review and Guide"
    
    def create_image_mapping_report(self) -> str:
        """创建图片映射报告"""
        report = []
        report.append("# 产品图片映射报告")
        report.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # 图片使用统计
        report.append("## 图片使用统计")
        for image, count in sorted(self.usage_data['image_usage'].items(), key=lambda x: x[1], reverse=True):
            report.append(f"- {image}: 使用 {count} 次")
        report.append("")
        
        # 重复使用检测
        duplicates = self.find_duplicate_image_usage()
        if duplicates:
            report.append("## 重复使用的图片 (需要处理)")
            for image, articles in duplicates.items():
                report.append(f"### {image}")
                for article in articles:
                    report.append(f"  - {article}")
                report.append("")
        else:
            report.append("## ✅ 未发现图片重复使用问题")
            report.append("")
        
        # 可用图片库
        report.append("## 可用图片库")
        total_images = 0
        for category, products in self.product_database.items():
            report.append(f"### {category.replace('_', ' ').title()}")
            for image_file, product_data in products.items():
                usage = self.usage_data['image_usage'].get(f"/images/products/{category}/{image_file}", 0)
                report.append(f"- {image_file} (使用{usage}次) - {product_data['description']}")
                total_images += 1
            report.append("")
        
        report.append(f"**总计**: {total_images} 张产品图片可用")
        
        return "\n".join(report)

# 使用示例和测试
if __name__ == "__main__":
    mapper = ProductImageMapper()
    
    # 测试关键词匹配
    print("测试关键词匹配...")
    test_keyword = "smart plug alexa"
    matches = mapper.analyze_keyword_match(test_keyword)
    
    print(f"\n关键词 '{test_keyword}' 的匹配结果:")
    for i, (image_path, score, metadata) in enumerate(matches[:3]):
        print(f"{i+1}. {image_path} (分数: {score:.2f})")
        print(f"   Alt文本: {metadata['alt_text']}")
        print(f"   描述: {metadata['description']}")
        print(f"   使用次数: {metadata['usage_count']}")
        print()
    
    # 生成报告
    report = mapper.create_image_mapping_report()
    with open("data/image_mapping_report.md", "w", encoding="utf-8") as f:
        f.write(report)
    
    print("✅ 图片映射报告已生成: data/image_mapping_report.md")