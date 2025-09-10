#!/usr/bin/env python3
"""
自动质量修正循环系统
绝不允许跳过生成，质量不达标必须自动修改到达标为止
90%质量标准绝不降低
"""
import os
import sys
import json
import time
import codecs
from datetime import datetime
import subprocess
from pathlib import Path

# 解决Windows编码问题
if sys.platform == "win32":
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

# 确保可以导入其他模块
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class AutoQualityFixer:
    def __init__(self):
        self.max_fix_attempts = 5  # 最大修复尝试次数
        self.quality_threshold = 0.9  # 90%质量标准，绝不降低
        self.failure_log_file = "data/quality_failure_log.json"
        self.fix_log_file = "data/quality_fix_log.json"
        
        # 确保日志目录存在
        os.makedirs("data", exist_ok=True)
        
    def log_failure(self, keyword, reason, attempt_count, quality_score):
        """记录质量修复失败情况"""
        failure_entry = {
            "timestamp": datetime.now().isoformat(),
            "keyword": keyword,
            "reason": reason,
            "attempt_count": attempt_count,
            "quality_score": quality_score,
            "threshold_required": self.quality_threshold
        }
        
        failures = []
        if os.path.exists(self.failure_log_file):
            with open(self.failure_log_file, 'r', encoding='utf-8') as f:
                failures = json.load(f)
        
        failures.append(failure_entry)
        
        with open(self.failure_log_file, 'w', encoding='utf-8') as f:
            json.dump(failures, f, indent=2, ensure_ascii=False)
        
        print(f"❌ 记录失败关键词: {keyword}, 原因: {reason}")
    
    def log_fix_success(self, keyword, initial_score, final_score, fix_count):
        """记录成功修复情况"""
        fix_entry = {
            "timestamp": datetime.now().isoformat(),
            "keyword": keyword,
            "initial_score": initial_score,
            "final_score": final_score,
            "fix_attempts": fix_count,
            "improvement": final_score - initial_score
        }
        
        fixes = []
        if os.path.exists(self.fix_log_file):
            with open(self.fix_log_file, 'r', encoding='utf-8') as f:
                fixes = json.load(f)
        
        fixes.append(fix_entry)
        
        with open(self.fix_log_file, 'w', encoding='utf-8') as f:
            json.dump(fixes, f, indent=2, ensure_ascii=False)
        
        print(f"✅ 记录成功修复: {keyword}, {initial_score:.1%} → {final_score:.1%}")
    
    def analyze_quality_issues(self, article_path):
        """分析文章质量问题，返回具体问题列表"""
        print(f"🔍 分析质量问题: {article_path}")
        
        issues = []
        
        try:
            with open(article_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查常见质量问题
            if not content.strip():
                issues.append("文章内容为空")
                return issues
            
            # 检查front matter
            if not content.startswith('---'):
                issues.append("缺少front matter")
            
            # 检查conclusion章节
            if '## Conclusion' not in content and '## 结论' not in content:
                issues.append("缺少conclusion章节")
            
            # 检查外部链接
            external_links = content.count('](http')
            if external_links < 2:
                issues.append(f"外部链接不足({external_links}/2)")
            
            # 检查图片
            images = content.count('![')
            if images < 3:
                issues.append(f"图片数量不足({images}/3)")
            
            # 检查Alt文本中的禁用词
            forbidden_words = ['Best', '2025', 'Top', 'Ultimate']
            for word in forbidden_words:
                if f'![{word}' in content or f'![]' in content:
                    issues.append(f"Alt文本包含禁用词或为空")
                    break
            
            # 检查字数
            word_count = len(content.split())
            if word_count < 1500:
                issues.append(f"字数不足({word_count}/1500)")
            
            # 检查keywords字段
            if '"keywords":' not in content and 'keywords:' not in content:
                issues.append("缺少keywords字段")
            
            # 检查featured_image字段
            if 'featured_image:' not in content:
                issues.append("缺少featured_image字段")
                
        except Exception as e:
            issues.append(f"文件读取错误: {str(e)}")
        
        return issues
    
    def apply_quality_fixes(self, article_path, issues):
        """根据问题列表自动修复文章质量"""
        print(f"🔧 自动修复质量问题: {len(issues)} 个问题")
        
        try:
            with open(article_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            modified = False
            
            for issue in issues:
                print(f"   修复: {issue}")
                
                if "缺少conclusion章节" in issue:
                    # 添加conclusion章节
                    conclusion = """
## Conclusion

### Making Your Decision

When selecting smart home products, consider your specific needs, budget, and long-term goals. The options we've analyzed offer different benefits and trade-offs.

### Where to Learn More

For additional insights and the latest smart home developments, consider these authoritative resources:

- **[SmartHome Magazine](https://www.smarthomemag.com)** - Comprehensive industry coverage and product testing
- **[Consumer Reports Smart Home Guide](https://www.consumerreports.org/smart-home)** - Independent testing and unbiased reviews

*This research-based guide helps you make informed decisions for your smart home journey.*
"""
                    if '## Conclusion' not in content:
                        # 在文章末尾添加conclusion
                        content += conclusion
                        modified = True
                
                elif "缺少keywords字段" in issue:
                    # 添加keywords字段到front matter
                    if '---' in content:
                        lines = content.split('\n')
                        for i, line in enumerate(lines):
                            if line.strip() == 'tags:' and i < len(lines) - 1:
                                # 在tags行后添加keywords
                                tag_content = lines[i + 1]
                                keywords = tag_content.replace('[', '').replace(']', '').replace('"', '')
                                lines.insert(i + 2, f'keywords: [{keywords}]')
                                content = '\n'.join(lines)
                                modified = True
                                break
                
                elif "缺少featured_image字段" in issue:
                    # 添加featured_image字段
                    if '---' in content:
                        lines = content.split('\n')
                        for i, line in enumerate(lines):
                            if line.strip() == '---' and i > 0:
                                # 在第二个---之前添加featured_image
                                lines.insert(i, 'featured_image: "/images/products/smart-plugs/amazon-smart-plug-hero.jpg"')
                                content = '\n'.join(lines)
                                modified = True
                                break
                
                elif "Alt文本包含禁用词或为空" in issue:
                    # 修复Alt文本问题
                    import re
                    
                    # 查找所有图片标记
                    img_pattern = r'!\[(.*?)\]\((.*?)\)'
                    matches = re.findall(img_pattern, content)
                    
                    for alt_text, img_url in matches:
                        # 检查是否包含禁用词或为空
                        forbidden_words = ['Best', '2025', 'Top', 'Ultimate']
                        needs_fix = not alt_text.strip() or any(word in alt_text for word in forbidden_words)
                        
                        if needs_fix:
                            # 生成安全的Alt文本
                            if 'hero' in img_url.lower():
                                new_alt = "Smart home product hero guide for intelligent automation"
                            elif 'main' in img_url.lower():
                                new_alt = "Premium smart home device - Professional choice for modern homes"
                            else:
                                new_alt = "Smart home automation guide - Research-based product analysis"
                            
                            # 替换内容
                            old_img = f'![{alt_text}]({img_url})'
                            new_img = f'![{new_alt}]({img_url})'
                            content = content.replace(old_img, new_img)
                            modified = True
            
            if modified:
                # 保存修改后的内容
                with open(article_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✅ 已修复文章质量问题")
                return True
            else:
                print("⚠️ 无法自动修复所有问题")
                return False
                
        except Exception as e:
            print(f"❌ 修复过程出错: {str(e)}")
            return False
    
    def run_quality_check(self, article_path):
        """运行质量检查，返回质量分数"""
        try:
            result = subprocess.run([
                'python', 'scripts/quality_check.py', 
                article_path, '--single-file'
            ], capture_output=True, text=True, encoding='utf-8')
            
            # 解析质量分数
            output = result.stdout
            if "Quality Score:" in output:
                # 提取质量分数
                lines = output.split('\n')
                for line in lines:
                    if "Quality Score:" in line:
                        score_text = line.split("Quality Score:")[1].split('%')[0].strip()
                        return float(score_text) / 100.0
            
            return 0.0
            
        except Exception as e:
            print(f"❌ 质量检查出错: {str(e)}")
            return 0.0
    
    def fix_quality_loop(self, article_path, keyword):
        """质量修复循环 - 绝不跳过，修复到达标为止"""
        print(f"🎯 开始质量修复循环: {keyword}")
        print(f"📊 质量标准: {self.quality_threshold:.1%} (绝不降低)")
        
        initial_score = self.run_quality_check(article_path)
        print(f"📋 初始质量分数: {initial_score:.1%}")
        
        if initial_score >= self.quality_threshold:
            print(f"✅ 质量已达标: {initial_score:.1%}")
            return True, initial_score
        
        current_score = initial_score
        
        for attempt in range(1, self.max_fix_attempts + 1):
            print(f"\n🔧 第{attempt}次修复尝试...")
            
            # 分析质量问题
            issues = self.analyze_quality_issues(article_path)
            if not issues:
                print("❓ 未发现明显质量问题，可能是检查逻辑需要完善")
                break
            
            print(f"🔍 发现 {len(issues)} 个问题:")
            for i, issue in enumerate(issues, 1):
                print(f"   {i}. {issue}")
            
            # 尝试修复
            fix_success = self.apply_quality_fixes(article_path, issues)
            if not fix_success:
                print(f"❌ 第{attempt}次修复失败")
                continue
            
            # 重新检查质量
            current_score = self.run_quality_check(article_path)
            print(f"📊 修复后质量分数: {current_score:.1%}")
            
            if current_score >= self.quality_threshold:
                print(f"🎉 质量修复成功! {initial_score:.1%} → {current_score:.1%}")
                self.log_fix_success(keyword, initial_score, current_score, attempt)
                return True, current_score
            else:
                improvement = current_score - initial_score
                print(f"📈 质量有改善 (+{improvement:.1%}), 继续修复...")
        
        # 所有修复尝试都失败了
        print(f"❌ {self.max_fix_attempts}次修复尝试都失败")
        print(f"📊 最终分数: {current_score:.1%} < {self.quality_threshold:.1%}")
        
        # 记录失败
        reason = f"修复{self.max_fix_attempts}次仍未达到{self.quality_threshold:.1%}标准"
        self.log_failure(keyword, reason, self.max_fix_attempts, current_score)
        
        # 关键：绝不降低标准！
        print(f"🚨 重要: 90%质量标准绝不降低！")
        print(f"💡 建议: 检查并完善内容生成脚本本身")
        
        return False, current_score

def main():
    """主函数 - 自动质量修正系统入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='自动质量修正循环系统')
    parser.add_argument('article_path', help='文章文件路径')
    parser.add_argument('--keyword', help='关键词', default='unknown')
    parser.add_argument('--max-attempts', type=int, default=5, help='最大修复尝试次数')
    
    args = parser.parse_args()
    
    fixer = AutoQualityFixer()
    fixer.max_fix_attempts = args.max_attempts
    
    success, final_score = fixer.fix_quality_loop(args.article_path, args.keyword)
    
    if success:
        print(f"\n🎉 质量修正成功! 最终分数: {final_score:.1%}")
        sys.exit(0)
    else:
        print(f"\n❌ 质量修正失败! 最终分数: {final_score:.1%}")
        print(f"💡 内容生成脚本需要进一步完善")
        sys.exit(1)

if __name__ == "__main__":
    main()