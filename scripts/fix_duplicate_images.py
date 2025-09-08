#!/usr/bin/env python3
"""
Fix Duplicate Image Usage Script
自动修复文章中的图片重复使用问题，为每篇文章分配最合适的图片
"""

import os
import sys
import codecs
import re
from pathlib import Path

# 解决Windows编码问题
if sys.platform == "win32":
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

# 添加modules路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.image_tools.product_image_mapper import ProductImageMapper

class ArticleImageFixer:
    """文章图片修复器"""
    
    def __init__(self):
        self.mapper = ProductImageMapper()
        self.content_dir = Path("content/articles")
        
    def extract_keyword_from_filename(self, filename: str) -> str:
        """从文件名提取关键词"""
        # 移除日期后缀和扩展名
        base_name = filename.replace('.md', '')
        base_name = re.sub(r'-\d{8}$', '', base_name)  # 移除日期
        
        # 转换为可读关键词
        return base_name.replace('-', ' ')
    
    def read_article(self, article_path: Path) -> tuple:
        """读取文章内容，返回(标题, 关键词, 完整内容)"""
        try:
            with open(article_path, 'r', encoding='utf-8') as f:
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
                primary_keyword = self.extract_keyword_from_filename(article_path.name)
            
            return title, primary_keyword, content
            
        except Exception as e:
            print(f"读取文章失败 {article_path}: {e}")
            return "", "", ""
    
    def find_images_in_article(self, content: str) -> list:
        """查找文章中的所有图片"""
        # 匹配Markdown图片格式: ![alt text](image_path "title")
        pattern = r'!\[([^\]]*)\]\(([^)]+?)(?:\s+"([^"]*)")?\)'
        matches = re.findall(pattern, content)
        
        images = []
        for match in matches:
            alt_text, image_path, title = match
            images.append({
                'alt_text': alt_text,
                'path': image_path,
                'title': title,
                'full_match': f'![{alt_text}]({image_path}' + (f' "{title}")' if title else ')')
            })
        
        return images
    
    def suggest_better_images(self, keyword: str, content: str, used_images: list) -> list:
        """为文章建议更好的图片"""
        # 获取当前已使用的图片路径
        exclude_images = [img['path'] for img in used_images]
        
        # 分析最佳匹配
        matches = self.mapper.analyze_keyword_match(keyword, content)
        
        suggestions = []
        for image_path, score, metadata in matches:
            if image_path not in exclude_images:
                suggestions.append({
                    'path': image_path,
                    'score': score,
                    'alt_text': metadata['alt_text'],
                    'description': metadata['description'],
                    'usage_count': metadata['usage_count']
                })
        
        return suggestions[:3]  # 返回前3个建议
    
    def update_article_images(self, article_path: Path, image_updates: list):
        """更新文章中的图片"""
        try:
            with open(article_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 应用所有图片更新
            for update in image_updates:
                old_markdown = update['old_markdown']
                new_markdown = update['new_markdown']
                content = content.replace(old_markdown, new_markdown)
            
            # 写入更新后的内容
            with open(article_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ 已更新文章: {article_path.name}")
            return True
            
        except Exception as e:
            print(f"❌ 更新文章失败 {article_path}: {e}")
            return False
    
    def process_article(self, article_path: Path) -> dict:
        """处理单篇文章的图片优化"""
        print(f"\n🔍 分析文章: {article_path.name}")
        
        title, keyword, content = self.read_article(article_path)
        if not content:
            return {'status': 'error', 'message': '无法读取文章'}
        
        print(f"   标题: {title}")
        print(f"   关键词: {keyword}")
        
        # 查找当前图片
        current_images = self.find_images_in_article(content)
        print(f"   当前图片数量: {len(current_images)}")
        
        if not current_images:
            # 没有图片，建议添加
            suggestions = self.suggest_better_images(keyword, content, [])
            return {
                'status': 'no_images',
                'suggestions': suggestions,
                'article_path': article_path
            }
        
        # 分析图片质量和重复性
        image_updates = []
        for i, img in enumerate(current_images):
            print(f"   图片 {i+1}: {img['path']}")
            
            # 获取图片建议
            used_images = [current_images[j] for j in range(len(current_images)) if j != i]
            suggestions = self.suggest_better_images(keyword, content, used_images)
            
            if suggestions and suggestions[0]['score'] > 0.7:
                # 有更好的图片建议
                best_suggestion = suggestions[0]
                
                # 生成新的Alt文本
                new_alt = self.mapper.generate_optimized_alt_text(
                    best_suggestion['path'], keyword, content
                )
                
                new_markdown = f'![{new_alt}]({best_suggestion["path"]} "{new_alt}")'
                
                image_updates.append({
                    'old_markdown': img['full_match'],
                    'new_markdown': new_markdown,
                    'reason': f'更好匹配 (分数: {best_suggestion["score"]:.2f})',
                    'old_path': img['path'],
                    'new_path': best_suggestion['path']
                })
                
                print(f"     → 建议替换为: {best_suggestion['path']} (分数: {best_suggestion['score']:.2f})")
            else:
                print(f"     → 当前图片合适")
        
        return {
            'status': 'analyzed',
            'updates': image_updates,
            'article_path': article_path,
            'keyword': keyword
        }
    
    def fix_all_articles(self, auto_apply: bool = False):
        """修复所有文章的图片问题"""
        print("🚀 开始修复所有文章的图片问题")
        print("=" * 60)
        
        article_files = list(self.content_dir.glob("*.md"))
        print(f"找到 {len(article_files)} 篇文章")
        
        results = []
        
        for article_path in article_files:
            result = self.process_article(article_path)
            results.append(result)
            
            if result['status'] == 'analyzed' and result['updates']:
                if auto_apply:
                    self.update_article_images(article_path, result['updates'])
                    # 更新使用跟踪
                    for update in result['updates']:
                        self.mapper.update_image_usage(str(article_path), update['new_path'])
                else:
                    print("   📝 发现可优化的图片，使用 --apply 参数自动应用")
        
        # 生成总结报告
        self.generate_summary_report(results)
        
        return results
    
    def generate_summary_report(self, results: list):
        """生成修复总结报告"""
        print("\n" + "=" * 60)
        print("📊 图片修复总结报告")
        print("=" * 60)
        
        total_articles = len(results)
        articles_with_updates = len([r for r in results if r['status'] == 'analyzed' and r.get('updates')])
        articles_no_images = len([r for r in results if r['status'] == 'no_images'])
        articles_good = total_articles - articles_with_updates - articles_no_images
        
        print(f"📈 总体统计:")
        print(f"   - 总文章数: {total_articles}")
        print(f"   - 需要优化图片的文章: {articles_with_updates}")
        print(f"   - 缺少图片的文章: {articles_no_images}")
        print(f"   - 图片配置良好的文章: {articles_good}")
        
        if articles_with_updates > 0:
            print(f"\n🔧 需要优化的文章:")
            for result in results:
                if result['status'] == 'analyzed' and result.get('updates'):
                    article_name = result['article_path'].name
                    update_count = len(result['updates'])
                    print(f"   - {article_name}: {update_count} 个图片需要优化")
        
        if articles_no_images > 0:
            print(f"\n📷 缺少图片的文章:")
            for result in results:
                if result['status'] == 'no_images':
                    article_name = result['article_path'].name
                    print(f"   - {article_name}: 建议添加产品图片")

if __name__ == "__main__":
    fixer = ArticleImageFixer()
    
    # 检查命令行参数
    auto_apply = '--apply' in sys.argv or '-a' in sys.argv
    
    if auto_apply:
        print("⚠️  自动应用模式 - 将直接修改文章文件")
        response = input("确认继续? (y/N): ")
        if response.lower() != 'y':
            print("操作已取消")
            sys.exit(0)
    
    results = fixer.fix_all_articles(auto_apply=auto_apply)
    
    if not auto_apply and any(r.get('updates') for r in results):
        print(f"\n💡 使用 'python scripts/fix_duplicate_images.py --apply' 自动应用修复")
    
    print("\n✅ 图片修复分析完成！")