#!/usr/bin/env python3
"""
智能图片去重和增强脚本 v2 Enhanced
解决文章间图片重复使用问题，为缺少图片的文章添加合适图片
新增：内容哈希去重、Smart Image Manager集成、配置化管理
"""

import os
import sys
import codecs
import re
import json
import hashlib
from pathlib import Path
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any

# 解决Windows编码问题
if sys.platform == "win32":
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

# 添加modules路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from modules.image_tools.product_image_mapper import ProductImageMapper

# 尝试导入Smart Image Manager
try:
    from smart_image_manager import search_and_assign
    SMART_IMAGES_AVAILABLE = True
    print("✅ Smart Image Manager integration enabled")
except ImportError:
    SMART_IMAGES_AVAILABLE = False
    print("⚠️ Smart Image Manager not available, using fallback methods")

# 尝试导入综合ImageManager
try:
    from modules.image_tools.image_manager import ComprehensiveImageManager
    COMPREHENSIVE_MANAGER_AVAILABLE = True
except ImportError:
    COMPREHENSIVE_MANAGER_AVAILABLE = False

class ImageDeduplicator:
    """图片去重和增强器 v2 Enhanced"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.mapper = ProductImageMapper()
        self.content_dir = Path("content/articles")
        self.image_dir = Path("static/images")
        
        # 加载配置
        self.config = self._load_config(config_path)
        
        # 初始化Smart Image Manager (如果可用)
        self.smart_manager = None
        if COMPREHENSIVE_MANAGER_AVAILABLE:
            try:
                self.smart_manager = ComprehensiveImageManager(config_path)
                print("✅ Comprehensive Image Manager initialized")
            except Exception as e:
                print(f"⚠️ Comprehensive Image Manager init failed: {e}")
        
        # 内容哈希缓存
        self.hash_cache = {}
        self.hash_cache_file = Path("data/image_hash_cache.json")
        self._load_hash_cache()
        
        print(f"📁 Content directory: {self.content_dir}")
        print(f"🖼️ Image directory: {self.image_dir}")
    
    def _load_config(self, config_path: Optional[str] = None) -> Dict:
        """加载配置文件"""
        if not config_path:
            config_path = project_root / 'image_config.yml'
        
        try:
            import yaml
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                print(f"✅ Loaded config from {config_path}")
                return config
        except Exception as e:
            print(f"⚠️ Failed to load config, using defaults: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """默认配置"""
        return {
            'quality': {
                'max_usage_count': 3,
                'min_image_relevance_score': 0.6
            },
            'file_organization': {
                'use_content_hash': True,
                'hash_length': 8
            },
            'cache': {
                'cache_directory': 'data/image_cache'
            }
        }
    
    def _load_hash_cache(self):
        """加载哈希缓存"""
        try:
            if self.hash_cache_file.exists():
                with open(self.hash_cache_file, 'r', encoding='utf-8') as f:
                    self.hash_cache = json.load(f)
                print(f"📝 Loaded {len(self.hash_cache)} cached hashes")
        except Exception as e:
            print(f"⚠️ Failed to load hash cache: {e}")
            self.hash_cache = {}
    
    def _save_hash_cache(self):
        """保存哈希缓存"""
        try:
            self.hash_cache_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.hash_cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.hash_cache, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️ Failed to save hash cache: {e}")
    
    def _content_hash(self, image_path: Path) -> Optional[str]:
        """计算文件内容哈希"""
        try:
            # 检查缓存
            cache_key = f"{image_path}:{image_path.stat().st_mtime}"
            if cache_key in self.hash_cache:
                return self.hash_cache[cache_key]
            
            # 计算哈希
            hash_obj = hashlib.sha1(image_path.read_bytes())
            content_hash = hash_obj.hexdigest()
            
            # 缓存结果
            self.hash_cache[cache_key] = content_hash
            
            return content_hash
            
        except Exception as e:
            print(f"⚠️ Failed to compute hash for {image_path}: {e}")
            return None
        
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
    import argparse
    
    parser = argparse.ArgumentParser(description='Smart Image Deduplication and Enhancement v2')
    parser.add_argument('--apply', '-a', action='store_true', help='Apply changes automatically')
    parser.add_argument('--mode', choices=['usage', 'content', 'both'], default='usage', 
                        help='Deduplication mode: usage (article usage), content (hash-based), or both')
    parser.add_argument('--execute', action='store_true', help='Execute content hash deduplication plan')
    parser.add_argument('--dry-run', action='store_true', default=True, help='Show changes without applying (default)')
    parser.add_argument('--image-root', default='static/images', help='Root directory for images')
    parser.add_argument('--config', help='Path to configuration file')
    
    args = parser.parse_args()
    
    # Override dry-run if apply is specified
    if args.apply:
        args.dry_run = False
    
    total_changes = 0
    
    # Run usage-based deduplication
    if args.mode in ['usage', 'both']:
        print("🎯 Running Usage-Based Deduplication...")
        print("=" * 60)
        
        deduplicator = ImageDeduplicator(config_path=args.config)
        
        if args.apply:
            print("⚠️  自动应用模式 - 将直接修改文章文件")
            response = input("确认继续? (y/N): ")
            if response.lower() != 'y':
                print("操作已取消")
                sys.exit(0)
        
        changes_count = deduplicator.run_full_deduplication(auto_apply=args.apply)
        total_changes += changes_count
        
        if changes_count > 0 and not args.apply:
            print(f"\n💡 发现 {changes_count} 处可以优化的地方")
            print("使用 --apply 参数自动应用修复")
        elif changes_count == 0:
            print(f"\n✅ 使用情况去重完美，无需修改！")
        
        # 保存哈希缓存
        deduplicator._save_hash_cache()
    
    # Run content hash-based deduplication
    if args.mode in ['content', 'both']:
        if args.mode == 'both':
            print(f"\n" + "=" * 60)
        
        print("🔍 Running Content Hash-Based Deduplication...")
        print("=" * 60)
        
        hash_changes = run_content_hash_deduplication(
            image_root=args.image_root,
            dry_run=args.dry_run,
            execute=args.execute or args.apply
        )
        total_changes += hash_changes
    
    # Summary
    if args.mode == 'both':
        print(f"\n" + "=" * 60)
        print(f"🎉 Complete Deduplication Analysis Finished!")
        print(f"📊 Total optimization opportunities: {total_changes}")
        
        if total_changes > 0 and args.dry_run:
            print(f"\n💡 To apply all changes:")
            print(f"   - Usage-based: python {sys.argv[0]} --mode usage --apply")
            print(f"   - Content-based: python {sys.argv[0]} --mode content --execute --apply")
            print(f"   - Both: python {sys.argv[0]} --mode both --apply --execute")
    else:
        print(f"\n🎉 {args.mode.title()}-based deduplication analysis complete!")


# === v2: Enhanced Content Hash-Based Deduplication System ===

class ContentHashDeduplicator:
    """v2 内容哈希去重系统 - 检测实际相同的图片文件"""
    
    def __init__(self, image_root: str = 'static/images'):
        self.image_root = Path(image_root)
        self.hash_cache = {}
        self.supported_formats = {'.webp', '.jpg', '.jpeg', '.png', '.gif'}
        
    def _content_hash(self, file_path: Path) -> Optional[str]:
        """计算文件内容哈希"""
        try:
            return hashlib.sha1(file_path.read_bytes()).hexdigest()
        except Exception as e:
            print(f"⚠️ Failed to hash {file_path}: {e}")
            return None
    
    def find_content_duplicates(self, verbose: bool = True) -> List[Tuple[Path, Path]]:
        """查找内容完全相同的图片文件"""
        print(f"🔍 Scanning {self.image_root} for content duplicates...")
        
        seen_hashes = {}
        duplicates = []
        
        # 扫描所有支持的图片格式
        for ext in self.supported_formats:
            for file_path in self.image_root.rglob(f'*{ext}'):
                if not file_path.is_file():
                    continue
                
                content_hash = self._content_hash(file_path)
                if not content_hash:
                    continue
                
                if content_hash in seen_hashes:
                    duplicates.append((file_path, seen_hashes[content_hash]))
                    if verbose:
                        print(f"   🔄 Duplicate found: {file_path} == {seen_hashes[content_hash]}")
                else:
                    seen_hashes[content_hash] = file_path
        
        print(f"✅ Content duplicate scan complete: found {len(duplicates)} duplicate pairs")
        return duplicates
    
    def analyze_duplicate_usage(self, duplicates: List[Tuple[Path, Path]], content_dir: Path = Path("content/articles")) -> Dict:
        """分析重复图片的使用情况"""
        usage_analysis = []
        
        for dup_path, original_path in duplicates:
            # 转换为网站相对路径
            try:
                dup_web_path = '/' + str(dup_path.relative_to(Path('static')))
                original_web_path = '/' + str(original_path.relative_to(Path('static')))
            except ValueError:
                continue
            
            # 查找引用这些图片的文章
            dup_articles = self._find_articles_using_image(dup_web_path, content_dir)
            original_articles = self._find_articles_using_image(original_web_path, content_dir)
            
            if dup_articles or original_articles:
                usage_analysis.append({
                    'duplicate_file': str(dup_path),
                    'original_file': str(original_path),
                    'duplicate_web_path': dup_web_path,
                    'original_web_path': original_web_path,
                    'duplicate_used_in': dup_articles,
                    'original_used_in': original_articles,
                    'total_usage': len(dup_articles) + len(original_articles),
                    'can_consolidate': len(dup_articles) > 0  # 可以合并到原始文件
                })
        
        return {
            'analysis': usage_analysis,
            'total_duplicates': len(duplicates),
            'used_duplicates': len([a for a in usage_analysis if a['total_usage'] > 0]),
            'consolidation_candidates': len([a for a in usage_analysis if a['can_consolidate']])
        }
    
    def _find_articles_using_image(self, image_web_path: str, content_dir: Path) -> List[str]:
        """查找使用特定图片的文章"""
        articles = []
        
        for article_file in content_dir.glob("*.md"):
            try:
                with open(article_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if image_web_path in content:
                    articles.append(article_file.name)
                    
            except Exception as e:
                print(f"⚠️ Error reading {article_file}: {e}")
        
        return articles
    
    def generate_consolidation_plan(self, analysis: Dict) -> Dict:
        """生成重复图片整合计划"""
        plan = {
            'file_deletions': [],
            'content_replacements': [],
            'estimated_savings': 0
        }
        
        for item in analysis['analysis']:
            if not item['can_consolidate']:
                continue
            
            # 计划删除重复文件
            duplicate_path = Path(item['duplicate_file'])
            if duplicate_path.exists():
                plan['file_deletions'].append({
                    'file': str(duplicate_path),
                    'size_bytes': duplicate_path.stat().st_size,
                    'reason': f"Duplicate of {item['original_file']}"
                })
                plan['estimated_savings'] += duplicate_path.stat().st_size
            
            # 计划替换内容中的引用
            for article in item['duplicate_used_in']:
                plan['content_replacements'].append({
                    'article': article,
                    'old_path': item['duplicate_web_path'],
                    'new_path': item['original_web_path'],
                    'reason': 'Consolidate to original image'
                })
        
        # 转换字节到可读格式
        plan['estimated_savings_mb'] = plan['estimated_savings'] / (1024 * 1024)
        
        return plan
    
    def execute_consolidation_plan(self, plan: Dict, dry_run: bool = True, content_dir: Path = Path("content/articles")):
        """执行重复图片整合计划"""
        if dry_run:
            print("🧪 DRY RUN - No actual changes will be made")
        
        print(f"\n📋 Consolidation Plan Summary:")
        print(f"   - Files to delete: {len(plan['file_deletions'])}")
        print(f"   - Content replacements: {len(plan['content_replacements'])}")
        print(f"   - Estimated savings: {plan['estimated_savings_mb']:.2f} MB")
        
        if not dry_run:
            # 执行内容替换
            for replacement in plan['content_replacements']:
                self._replace_image_in_article(
                    article_file=content_dir / replacement['article'],
                    old_path=replacement['old_path'],
                    new_path=replacement['new_path']
                )
            
            # 删除重复文件
            for deletion in plan['file_deletions']:
                file_path = Path(deletion['file'])
                if file_path.exists():
                    file_path.unlink()
                    print(f"🗑️ Deleted: {file_path}")
        
        return len(plan['file_deletions']) + len(plan['content_replacements'])
    
    def _replace_image_in_article(self, article_file: Path, old_path: str, new_path: str):
        """在文章中替换图片路径"""
        try:
            with open(article_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 替换图片引用
            updated_content = content.replace(old_path, new_path)
            
            if updated_content != content:
                with open(article_file, 'w', encoding='utf-8') as f:
                    f.write(updated_content)
                print(f"✅ Updated {article_file.name}: {old_path} → {new_path}")
            
        except Exception as e:
            print(f"❌ Failed to update {article_file}: {e}")


def list_duplicates(image_root: str = 'static/images') -> List[Tuple[Path, Path]]:
    """v2 Helper function - 查找重复图片 (向后兼容)"""
    deduplicator = ContentHashDeduplicator(image_root)
    return deduplicator.find_content_duplicates()


def run_content_hash_deduplication(image_root: str = 'static/images', dry_run: bool = True, execute: bool = False):
    """运行完整的内容哈希去重流程"""
    print("🚀 Starting Content Hash Deduplication v2")
    print("=" * 60)
    
    # 1. 创建去重器
    deduplicator = ContentHashDeduplicator(image_root)
    
    # 2. 查找重复文件
    duplicates = deduplicator.find_content_duplicates()
    
    if not duplicates:
        print("✅ No content duplicates found!")
        return 0
    
    # 3. 分析使用情况
    print(f"\n📊 Analyzing usage patterns...")
    analysis = deduplicator.analyze_duplicate_usage(duplicates)
    
    print(f"   - Total duplicate pairs: {analysis['total_duplicates']}")
    print(f"   - Duplicates in use: {analysis['used_duplicates']}")
    print(f"   - Consolidation candidates: {analysis['consolidation_candidates']}")
    
    # 4. 生成整合计划
    plan = deduplicator.generate_consolidation_plan(analysis)
    
    # 5. 执行计划（如果请求）
    if execute:
        changes = deduplicator.execute_consolidation_plan(plan, dry_run=dry_run)
        return changes
    else:
        # 只显示计划
        deduplicator.execute_consolidation_plan(plan, dry_run=True)
        print(f"\n💡 Use --execute to apply changes")
        print(f"💡 Use --execute --apply to apply changes permanently")
        return 0