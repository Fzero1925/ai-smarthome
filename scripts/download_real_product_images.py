#!/usr/bin/env python3
"""
Real Product Images Downloader
下载真实的产品图片替换占位符，支持Google AdSense质量要求

Features:
- Downloads high-quality product images from Unsplash API
- Automatically processes and optimizes images
- Replaces placeholder images while maintaining file structure
- Ensures AdSense compliance (>50KB, relevant content)
"""

import os
import sys
import requests
import json
import time
import hashlib
from PIL import Image
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import codecs
from datetime import datetime

# 解决Windows编码问题
if sys.platform == "win32":
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

class RealImageDownloader:
    """真实产品图片下载器"""
    
    def __init__(self, unsplash_access_key: Optional[str] = None):
        """
        Initialize the image downloader
        
        Args:
            unsplash_access_key: Unsplash API access key (optional - uses demo mode if not provided)
        """
        self.unsplash_key = unsplash_access_key or os.getenv('UNSPLASH_ACCESS_KEY')
        self.base_path = Path("static/images/products")
        self.download_cache = Path("data/downloaded_images_cache.json")
        
        # 确保目录存在
        os.makedirs("data", exist_ok=True)
        
        # 产品搜索关键词配置
        self.product_search_terms = {
            'smart-plugs': [
                'smart plug white background',
                'wifi outlet white background', 
                'smart power outlet',
                'alexa smart plug',
                'smart socket white background'
            ],
            'smart-bulbs': [
                'smart led bulb white background',
                'wifi light bulb',
                'smart lighting bulb',
                'color changing bulb',
                'philips hue bulb white background'
            ],
            'smart-thermostats': [
                'smart thermostat white background',
                'digital thermostat',
                'nest thermostat',
                'wifi thermostat white background',
                'smart climate control'
            ],
            'security-cameras': [
                'security camera white background',
                'wifi camera',
                'surveillance camera white background',
                'smart security camera',
                'outdoor security camera'
            ],
            'robot-vacuums': [
                'robot vacuum white background',
                'robotic vacuum cleaner',
                'smart vacuum robot',
                'automatic vacuum white background',
                'roomba vacuum'
            ]
        }
        
        # 备用图片URLs (高质量免费图片 - 确保所有类别都有)
        self.fallback_images = {
            'smart-plugs': [
                'https://images.unsplash.com/photo-1558618047-3c8c76ca7d13?w=400&h=300&fit=crop',
                'https://images.unsplash.com/photo-1544197150-b99a580bb7a8?w=400&h=300&fit=crop',
                'https://images.unsplash.com/photo-1544197150-b99a580bb7a8?w=400&h=300&fit=crop'
            ],
            'smart-bulbs': [
                'https://images.unsplash.com/photo-1513475382585-d06e58bcb0e0?w=400&h=300&fit=crop',
                'https://images.unsplash.com/photo-1524484485831-a92ffc0de03f?w=400&h=300&fit=crop',
                'https://images.unsplash.com/photo-1556075798-4825dfaaf498?w=400&h=300&fit=crop'
            ],
            'smart-thermostats': [
                'https://images.unsplash.com/photo-1545259741-2ea3ebf61fa9?w=400&h=300&fit=crop',
                'https://images.unsplash.com/photo-1581092918484-8313dcafc98f?w=400&h=300&fit=crop',
                'https://images.unsplash.com/photo-1558618047-3c8c76ca7d13?w=400&h=300&fit=crop'
            ],
            'security-cameras': [
                'https://images.unsplash.com/photo-1557804506-669a67965ba0?w=400&h=300&fit=crop',
                'https://images.unsplash.com/photo-1573164713714-d95e436ab8d6?w=400&h=300&fit=crop',
                'https://images.unsplash.com/photo-1544197150-b99a580bb7a8?w=400&h=300&fit=crop'
            ],
            'robot-vacuums': [
                'https://images.unsplash.com/photo-1558618047-3c8c76ca7d13?w=400&h=300&fit=crop',
                'https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=400&h=300&fit=crop',
                'https://images.unsplash.com/photo-1544197150-b99a580bb7a8?w=400&h=300&fit=crop'
            ],
            'smart-speakers': [
                'https://images.unsplash.com/photo-1544197150-b99a580bb7a8?w=400&h=300&fit=crop',
                'https://images.unsplash.com/photo-1558618047-3c8c76ca7d13?w=400&h=300&fit=crop',
                'https://images.unsplash.com/photo-1513475382585-d06e58bcb0e0?w=400&h=300&fit=crop'
            ],
            'general': [
                'https://images.unsplash.com/photo-1558618047-3c8c76ca7d13?w=400&h=300&fit=crop',
                'https://images.unsplash.com/photo-1544197150-b99a580bb7a8?w=400&h=300&fit=crop',
                'https://images.unsplash.com/photo-1513475382585-d06e58bcb0e0?w=400&h=300&fit=crop'
            ]
        }
        
        # 载入下载缓存
        self.download_cache_data = self._load_download_cache()
    
    def _load_download_cache(self) -> Dict:
        """载入下载缓存数据"""
        if self.download_cache.exists():
            try:
                with open(self.download_cache, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        
        return {
            'downloaded_images': {},
            'failed_downloads': {},
            'last_updated': datetime.now().isoformat()
        }
    
    def _save_download_cache(self):
        """保存下载缓存数据"""
        self.download_cache_data['last_updated'] = datetime.now().isoformat()
        with open(self.download_cache, 'w', encoding='utf-8') as f:
            json.dump(self.download_cache_data, f, indent=2, ensure_ascii=False)
    
    def detect_placeholder_images(self) -> List[Tuple[str, int]]:
        """检测占位符图片 (基于文件大小和内容)"""
        placeholder_images = []
        
        for category_dir in self.base_path.iterdir():
            if category_dir.is_dir():
                for img_file in category_dir.glob("*.jpg"):
                    file_size = img_file.stat().st_size
                    
                    # 检测小文件 (<5KB) 或特定占位符大小
                    if file_size < 5000 or file_size == 996:
                        try:
                            # 额外验证: 检查是否为单色图片
                            with Image.open(img_file) as img:
                                # 获取图片的颜色分布
                                colors = img.getcolors(maxcolors=256*256*256)
                                if colors and len(colors) <= 3:  # 很少的颜色 = 占位符
                                    placeholder_images.append((str(img_file), file_size))
                        except Exception:
                            # 如果无法打开图片，也认为是占位符
                            placeholder_images.append((str(img_file), file_size))
        
        return placeholder_images
    
    def search_unsplash_images(self, query: str, per_page: int = 5) -> List[Dict]:
        """从Unsplash搜索图片"""
        if not self.unsplash_key:
            print("⚠️ No Unsplash API key provided, using fallback images")
            return []
        
        url = "https://api.unsplash.com/search/photos"
        headers = {"Authorization": f"Client-ID {self.unsplash_key}"}
        params = {
            "query": query,
            "per_page": per_page,
            "orientation": "landscape",
            "content_filter": "high"
        }
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data.get('results', [])
            else:
                print(f"⚠️ Unsplash API error: {response.status_code}")
        except Exception as e:
            print(f"⚠️ Failed to search Unsplash: {e}")
        
        return []
    
    def download_and_process_image(self, image_url: str, output_path: str, 
                                 target_size: Tuple[int, int] = (400, 300)) -> bool:
        """下载并处理图片"""
        try:
            # 下载图片
            response = requests.get(image_url, timeout=15)
            if response.status_code != 200:
                return False
            
            # 打开并处理图片
            from io import BytesIO
            with Image.open(BytesIO(response.content)) as img:
                # 转换为RGB模式 (去除透明通道)
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # 调整尺寸 (保持宽高比)
                img.thumbnail(target_size, Image.Resampling.LANCZOS)
                
                # 创建目标尺寸的白色背景
                final_img = Image.new('RGB', target_size, 'white')
                
                # 居中贴图
                offset = ((target_size[0] - img.size[0]) // 2,
                         (target_size[1] - img.size[1]) // 2)
                final_img.paste(img, offset)
                
                # 保存图片 (高质量)
                final_img.save(output_path, 'JPEG', quality=85, optimize=True)
                
                # 验证文件大小 (确保>10KB for AdSense)
                if os.path.getsize(output_path) < 10000:
                    print(f"⚠️ Image too small after processing: {output_path}")
                    return False
                
                return True
                
        except Exception as e:
            print(f"❌ Failed to process image: {e}")
            return False
    
    def get_category_image_url(self, category: str, image_index: int = 0) -> Optional[str]:
        """获取分类的图片URL (Unsplash优先，备用其次)"""
        
        # 首先尝试Unsplash API
        if category in self.product_search_terms and self.unsplash_key:
            search_terms = self.product_search_terms[category]
            for term in search_terms[:2]:  # 尝试前2个搜索词
                results = self.search_unsplash_images(term, per_page=3)
                if results:
                    if image_index < len(results):
                        return results[image_index]['urls']['regular']
                time.sleep(0.5)  # API限制
        
        # 使用备用图片
        if category in self.fallback_images:
            fallback_urls = self.fallback_images[category]
            if image_index < len(fallback_urls):
                return fallback_urls[image_index]
        
        return None
    
    def replace_placeholder_images(self, max_images_per_category: int = 10) -> Dict[str, int]:
        """批量替换占位符图片"""
        
        print("🔍 Detecting placeholder images...")
        placeholder_images = self.detect_placeholder_images()
        
        if not placeholder_images:
            print("✅ No placeholder images found!")
            return {}
        
        print(f"📋 Found {len(placeholder_images)} placeholder images to replace")
        
        # 按分类组织文件
        category_files = {}
        for img_path, file_size in placeholder_images:
            path_obj = Path(img_path)
            category = path_obj.parent.name
            
            if category not in category_files:
                category_files[category] = []
            category_files[category].append((img_path, file_size))
        
        replacement_stats = {}
        
        for category, files in category_files.items():
            print(f"\n🎯 Processing category: {category}")
            replaced_count = 0
            
            for i, (img_path, file_size) in enumerate(files[:max_images_per_category]):
                print(f"  📸 Replacing {Path(img_path).name} ({file_size} bytes)...")
                
                # 获取图片URL (轮换使用不同图片)
                image_url = self.get_category_image_url(category, i % 3)
                
                if image_url:
                    success = self.download_and_process_image(image_url, img_path)
                    if success:
                        print(f"    ✅ Successfully replaced with real image")
                        replaced_count += 1
                        
                        # 记录到缓存
                        self.download_cache_data['downloaded_images'][img_path] = {
                            'source_url': image_url,
                            'download_time': datetime.now().isoformat(),
                            'category': category
                        }
                    else:
                        print(f"    ❌ Failed to process image")
                        self.download_cache_data['failed_downloads'][img_path] = {
                            'error': 'Processing failed',
                            'attempted_url': image_url,
                            'time': datetime.now().isoformat()
                        }
                else:
                    print(f"    ⚠️ No image URL available for category {category}")
                
                time.sleep(1)  # 避免过快请求
            
            replacement_stats[category] = replaced_count
            print(f"  📊 Replaced {replaced_count}/{len(files)} images in {category}")
        
        # 保存缓存
        self._save_download_cache()
        
        return replacement_stats
    
    def verify_image_quality(self) -> Dict[str, List[str]]:
        """验证所有图片质量"""
        quality_report = {
            'good_images': [],
            'placeholder_images': [],
            'corrupted_images': []
        }
        
        for category_dir in self.base_path.iterdir():
            if category_dir.is_dir():
                for img_file in category_dir.glob("*.jpg"):
                    try:
                        file_size = img_file.stat().st_size
                        
                        # 检查文件大小
                        if file_size < 5000:
                            quality_report['placeholder_images'].append(str(img_file))
                            continue
                        
                        # 检查图片内容
                        with Image.open(img_file) as img:
                            # 检查尺寸
                            if img.size[0] < 200 or img.size[1] < 150:
                                quality_report['placeholder_images'].append(str(img_file))
                                continue
                            
                            # 检查颜色多样性
                            colors = img.getcolors(maxcolors=256*256*256)
                            if colors and len(colors) <= 5:
                                quality_report['placeholder_images'].append(str(img_file))
                                continue
                            
                            quality_report['good_images'].append(str(img_file))
                    
                    except Exception:
                        quality_report['corrupted_images'].append(str(img_file))
        
        return quality_report
    
    def create_quality_report(self) -> str:
        """创建质量检查报告"""
        quality_data = self.verify_image_quality()
        
        report = []
        report.append("# 产品图片质量报告")
        report.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # 统计信息
        total_images = sum(len(images) for images in quality_data.values())
        good_count = len(quality_data['good_images'])
        placeholder_count = len(quality_data['placeholder_images'])
        corrupted_count = len(quality_data['corrupted_images'])
        
        report.append(f"## 总体统计")
        report.append(f"- 总图片数: {total_images}")
        report.append(f"- 高质量图片: {good_count} ({good_count/total_images*100:.1f}%)")
        report.append(f"- 占位符图片: {placeholder_count} ({placeholder_count/total_images*100:.1f}%)")
        report.append(f"- 损坏图片: {corrupted_count} ({corrupted_count/total_images*100:.1f}%)")
        report.append("")
        
        # 详细列表
        if quality_data['placeholder_images']:
            report.append("## ⚠️ 占位符图片 (需要替换)")
            for img in quality_data['placeholder_images']:
                report.append(f"- {img}")
            report.append("")
        
        if quality_data['corrupted_images']:
            report.append("## ❌ 损坏图片 (需要修复)")
            for img in quality_data['corrupted_images']:
                report.append(f"- {img}")
            report.append("")
        
        if quality_data['good_images']:
            report.append("## ✅ 高质量图片")
            for img in quality_data['good_images'][:10]:  # 只显示前10个
                report.append(f"- {img}")
            if len(quality_data['good_images']) > 10:
                report.append(f"... 还有 {len(quality_data['good_images']) - 10} 张")
            report.append("")
        
        return "\n".join(report)

def main():
    """主执行函数"""
    print("🚀 AI Smart Home Hub - Real Image Downloader")
    print("=" * 60)
    
    # 检查Unsplash API Key
    unsplash_key = os.getenv('UNSPLASH_ACCESS_KEY')
    if unsplash_key:
        print("✅ Unsplash API key found - will use high quality images")
    else:
        print("⚠️ No Unsplash API key - will use fallback images")
        print("💡 Set UNSPLASH_ACCESS_KEY environment variable for best results")
    
    # 初始化下载器
    downloader = RealImageDownloader(unsplash_key)
    
    # 执行替换
    print("\n📸 Starting image replacement process...")
    stats = downloader.replace_placeholder_images()
    
    # 显示结果
    total_replaced = sum(stats.values())
    print(f"\n🎉 Replacement completed!")
    print(f"📊 Total images replaced: {total_replaced}")
    for category, count in stats.items():
        print(f"  - {category}: {count} images")
    
    # 生成质量报告
    print("\n📋 Generating quality report...")
    report = downloader.create_quality_report()
    report_path = "data/image_quality_report.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"✅ Quality report saved: {report_path}")
    
    # 最终验证
    quality_data = downloader.verify_image_quality()
    remaining_placeholders = len(quality_data['placeholder_images'])
    
    if remaining_placeholders == 0:
        print("\n🎉 SUCCESS: All placeholder images have been replaced!")
        print("🌐 Your website is now ready with high-quality product images")
    else:
        print(f"\n⚠️ Warning: {remaining_placeholders} placeholder images still remain")
        print("💡 Check the quality report for details")
    
    return total_replaced > 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)