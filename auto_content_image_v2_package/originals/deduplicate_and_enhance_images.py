#!/usr/bin/env python3
"""
智能图片去重和增强脚本
解决文章间图片重复使用问题，为缺少图片的文章添加合适图片
"""

import os
import sys
import codecs
import re
from pathlib import Path
from collections import defaultdict

# 解决Windows编码问题
if sys.platform == "win32":
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

# 添加modules路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.image_tools.product_image_mapper import ProductImageMapper

class ImageDeduplicator:
    """图片去重和增强器"""
    
    def __init__(self):
        self.mapper = ProductImageMapper()
        self.content_dir = Path("content/articles")
        
    def analyze_image_usage_across_articles(self):
        """分析所有文章的图片使用情况"""
        image_usage = defaultdict(list)  # image_path -> [article_files]
        article_images = {}  # article_file -> [image_paths]
        
        for article_file in self.content_dir.glob("*.md"):
            try:
                with open(article_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 提取所有图片
                image_pattern = r'!\[([^\]]*)\]\(([^)]+?)(?:\s+"([^"]*)")?\)'
                matches = re.findall(image_pattern, content)
                
                article_images[article_file.name] = []
                for match in matches:
                    alt_text, image_path, title = match
                    if image_path.startswith('/images/products/'):
                        image_usage[image_path].append(article_file.name)
                        article_images[article_file.name].append(image_path)
                        
            except Exception as e:
                print(f"❌ 读取文章失败 {article_file}: {e}")
        
        return dict(image_usage), article_images
    
    def find_duplicate_images(self, image_usage):
        """找出被多篇文章使用的图片"""
        return {img: articles for img, articles in image_usage.items() if len(articles) > 1}
    
    def extract_article_info(self, article_file):
        """提取文章基本信息"""
        try:
            with open(self.content_dir / article_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 提取标题
            title_match = re.search(r'title:\s*["\'](.+?)["\']', content)
            title = title_match.group(1) if title_match else ""
            
            # 提取关键词
            keywords_match = re.search(r'keywords:\s*\[(.+?)\]', content)
            if keywords_match:
                keywords_str = keywords_match.group(1)
                keywords = [kw.strip(' "\'') for kw in keywords_str.split(',')]
                primary_keyword = keywords[0] if keywords else ""
            else:
                # 从文件名提取
                base_name = article_file.replace('.md', '')
                base_name = re.sub(r'-\d{8}$', '', base_name)
                primary_keyword = base_name.replace('-', ' ')
            
            # 提取日期
            date_match = re.search(r'date:\s*(.+?)Z', content)
            date_str = date_match.group(1) if date_match else "1900-01-01T00:00:00"
            
            return {
                'title': title,
                'keyword': primary_keyword,
                'content': content,
                'date': date_str,
                'file': article_file
            }
            
        except Exception as e:
            print(f"❌ 提取文章信息失败 {article_file}: {e}")
            return None
    
    def resolve_image_conflicts(self, duplicate_images, article_images):
        """解决图片冲突，为每篇文章分配最合适的图片"""
        resolutions = {}
        
        for image_path, conflicting_articles in duplicate_images.items():
            print(f"\n🔍 解决图片冲突: {image_path}")
            print(f"   冲突文章: {', '.join(conflicting_articles)}")
            
            # 分析每篇文章对这个图片的适配度
            article_scores = []
            
            for article_file in conflicting_articles:
                article_info = self.extract_article_info(article_file)
                if not article_info:
                    continue
                
                # 计算图片匹配分数
                matches = self.mapper.analyze_keyword_match(
                    article_info['keyword'], 
                    article_info['content']
                )
                
                # 找到当前图片的分数
                image_score = 0
                for img_path, score, metadata in matches:
                    if img_path == image_path:
                        image_score = score
                        break
                
                article_scores.append({
                    'article': article_file,
                    'score': image_score,
                    'keyword': article_info['keyword'],
                    'date': article_info['date']
                })
            
            # 按分数排序，分数相同则按日期（较新的优先）
            article_scores.sort(key=lambda x: (x['score'], x['date']), reverse=True)
            
            if article_scores:
                # 最匹配的文章保留原图片
                winner = article_scores[0]
                print(f"   ✅ 最佳匹配: {winner['article']} (分数: {winner['score']:.2f})")
                
                # 其他文章需要替换图片
                for loser in article_scores[1:]:
                    article_file = loser['article']
                    article_info = self.extract_article_info(article_file)
                    
                    # 为这篇文章找到替代图片（排除当前冲突图片）
                    exclude_images = [image_path] + article_images.get(article_file, [])
                    
                    best_alternative = self.mapper.get_best_image_for_keyword(
                        article_info['keyword'],
                        article_info['content'],
                        exclude_images
                    )
                    
                    if best_alternative:
                        alt_image_path, alt_metadata = best_alternative
                        resolutions[f"{article_file}:{image_path}"] = {
                            'article': article_file,
                            'old_image': image_path,
                            'new_image': alt_image_path,
                            'new_alt': alt_metadata['alt_text'],
                            'reason': f'解决冲突，替换为更合适的图片 (分数: {alt_metadata.get("score", 0):.2f})'
                        }
                        print(f"   🔄 {article_file}: 替换为 {alt_image_path}")
                    else:
                        print(f"   ⚠️  {article_file}: 没有找到合适的替代图片")
        
        return resolutions
    
    def add_missing_images(self, article_images):
        """为缺少图片的文章添加图片"""
        additions = {}
        
        for article_file in self.content_dir.glob("*.md"):
            if article_file.name not in article_images or not article_images[article_file.name]:
                # 这篇文章缺少图片
                article_info = self.extract_article_info(article_file.name)
                if not article_info:
                    continue
                
                print(f"\n📷 为文章添加图片: {article_file.name}")
                print(f"   关键词: {article_info['keyword']}")
                
                # 找到最佳图片
                best_match = self.mapper.get_best_image_for_keyword(
                    article_info['keyword'],
                    article_info['content']
                )
                
                if best_match:
                    image_path, metadata = best_match
                    additions[article_file.name] = {
                        'article': article_file.name,
                        'image': image_path,
                        'alt_text': metadata['alt_text'],
                        'keyword': article_info['keyword'],
                        'insert_position': 'after_title'  # 在标题后插入
                    }
                    print(f"   ✅ 建议添加: {image_path}")
                else:
                    print(f"   ⚠️  没有找到合适的图片")
        
        return additions
    
    def apply_image_changes(self, resolutions, additions, auto_apply=False):
        """应用图片更改"""
        if not resolutions and not additions:
            print("✅ 没有需要修改的图片")
            return
        
        print(f"\n📝 变更摘要:")
        print(f"   - 图片替换: {len(resolutions)} 项")
        print(f"   - 图片添加: {len(additions)} 项")
        
        if not auto_apply:
            print(f"\n💡 使用 --apply 参数自动应用这些更改")
            return
        
        # 应用图片替换
        for change_id, resolution in resolutions.items():
            self.apply_image_replacement(resolution)
        
        # 应用图片添加
        for article_file, addition in additions.items():
            self.apply_image_addition(addition)
        
        print(f"\n✅ 所有图片更改已应用完成！")
    
    def apply_image_replacement(self, resolution):
        """应用单个图片替换"""
        article_file = self.content_dir / resolution['article']
        
        try:
            with open(article_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 找到并替换图片引用
            old_pattern = rf'!\[([^\]]*)\]\({re.escape(resolution["old_image"])}(?:\s+"([^"]*)")?\)'
            
            def replacement(match):
                old_alt = match.group(1)
                old_title = match.group(2) if match.group(2) else ""
                
                # 使用新的alt文本，保留原标题或使用新的
                new_title = old_title if old_title else resolution['new_alt']
                return f'![{resolution["new_alt"]}]({resolution["new_image"]} "{new_title}")'
            
            new_content = re.sub(old_pattern, replacement, content)
            
            # 写入文件
            with open(article_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"✅ 已替换图片: {resolution['article']}")
            print(f"   {resolution['old_image']} → {resolution['new_image']}")
            
        except Exception as e:
            print(f"❌ 替换图片失败 {resolution['article']}: {e}")
    
    def apply_image_addition(self, addition):
        """为文章添加图片"""
        article_file = self.content_dir / addition['article']
        
        try:
            with open(article_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 在introduction标题后插入图片
            intro_pattern = r'(## Introduction\s*\n)'
            
            image_markdown = f'\n![{addition["alt_text"]}]({addition["image"]} "{addition["alt_text"]}")\n\n*Featured: Professional review and buying guide for {addition["keyword"]}*\n'
            
            if re.search(intro_pattern, content):
                new_content = re.sub(intro_pattern, r'\1' + image_markdown, content)
            else:
                # 如果没有Introduction标题，在front matter后插入
                front_matter_end = content.find('---', 3) + 3
                if front_matter_end > 2:
                    new_content = content[:front_matter_end] + '\n' + image_markdown + content[front_matter_end:]
                else:
                    new_content = image_markdown + content
            
            # 写入文件
            with open(article_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"✅ 已添加图片: {addition['article']}")
            print(f"   图片: {addition['image']}")
            
        except Exception as e:
            print(f"❌ 添加图片失败 {addition['article']}: {e}")
    
    def run_full_deduplication(self, auto_apply=False):
        """运行完整的图片去重和增强流程"""
        print("🚀 开始图片去重和增强流程")
        print("=" * 60)
        
        # 1. 分析图片使用情况
        print("📊 分析图片使用情况...")
        image_usage, article_images = self.analyze_image_usage_across_articles()
        
        print(f"   - 发现 {len(image_usage)} 个图片被使用")
        print(f"   - 涉及 {len(article_images)} 篇文章")
        
        # 2. 找出重复图片
        duplicate_images = self.find_duplicate_images(image_usage)
        print(f"   - 发现 {len(duplicate_images)} 个重复使用的图片")
        
        # 3. 解决图片冲突
        resolutions = {}
        if duplicate_images:
            print(f"\n🔧 解决图片冲突...")
            resolutions = self.resolve_image_conflicts(duplicate_images, article_images)
        
        # 4. 为缺少图片的文章添加图片
        print(f"\n📷 检查缺少图片的文章...")
        additions = self.add_missing_images(article_images)
        
        # 5. 应用所有更改
        self.apply_image_changes(resolutions, additions, auto_apply)
        
        return len(resolutions) + len(additions)

if __name__ == "__main__":
    deduplicator = ImageDeduplicator()
    
    # 检查命令行参数
    auto_apply = '--apply' in sys.argv or '-a' in sys.argv
    
    if auto_apply:
        print("⚠️  自动应用模式 - 将直接修改文章文件")
        response = input("确认继续? (y/N): ")
        if response.lower() != 'y':
            print("操作已取消")
            sys.exit(0)
    
    changes_count = deduplicator.run_full_deduplication(auto_apply=auto_apply)
    
    if changes_count > 0 and not auto_apply:
        print(f"\n💡 发现 {changes_count} 处可以优化的地方")
        print("使用 'python scripts/deduplicate_and_enhance_images.py --apply' 自动应用修复")
    elif changes_count == 0:
        print(f"\n✅ 图片配置完美，无需修改！")
    
    print(f"\n🎉 图片去重和增强分析完成！")