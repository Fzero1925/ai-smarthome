#!/usr/bin/env python3
"""
Content Quality Check Script
Simplified quality validation for generated articles
"""

import os
import sys
import argparse
import re
import codecs
from pathlib import Path

# 解决Windows编码问题
if sys.platform == "win32":
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

def check_article_quality(filepath):
    """Check quality metrics for a single article"""
    issues = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Word count check
        word_count = len(content.split())
        if word_count < 1500:
            issues.append(f"Too short: {word_count} words (minimum: 1500)")
        elif word_count > 4000:
            issues.append(f"Too long: {word_count} words (maximum: 4000)")
        
        # Section headings check
        section_count = len(re.findall(r'^## ', content, re.MULTILINE))
        if section_count < 3:
            issues.append(f"Too few sections: {section_count} (minimum: 3)")
        
        # Front matter validation
        if not content.startswith('---'):
            issues.append("Missing front matter")
        else:
            front_matter = content.split('---')[1] if '---' in content else ""
            required_fields = ['title:', 'description:', 'date:', 'categories:', 'tags:']
            for field in required_fields:
                if field not in front_matter:
                    issues.append(f"Missing front matter field: {field}")
        
        # Basic content structure checks
        if 'Introduction' not in content:
            issues.append("Missing Introduction section")
        if 'Conclusion' not in content:
            issues.append("Missing Conclusion section")
        
        return {
            'file': os.path.basename(filepath),
            'word_count': word_count,
            'sections': section_count,
            'issues': issues,
            'status': 'PASS' if len(issues) == 0 else 'WARN' if len(issues) <= 2 else 'FAIL'
        }
        
    except Exception as e:
        return {
            'file': os.path.basename(filepath),
            'word_count': 0,
            'sections': 0,
            'issues': [f"Error reading file: {e}"],
            'status': 'ERROR'
        }

def main():
    parser = argparse.ArgumentParser(description='Check content quality')
    parser.add_argument('directory', help='Directory containing articles to check')
    parser.add_argument('--recent-only', action='store_true', help='Only check recently generated files')
    
    args = parser.parse_args()
    
    print("🔍 Starting content quality check...")
    
    # Get files to check
    if args.recent_only and os.path.exists('generated_files.txt'):
        with open('generated_files.txt', 'r') as f:
            files_to_check = [line.strip() for line in f if line.strip()]
        print(f"📋 Checking {len(files_to_check)} recently generated files")
    else:
        files_to_check = list(Path(args.directory).glob('*.md'))
        print(f"📋 Checking all {len(files_to_check)} files in {args.directory}")
    
    if not files_to_check:
        print("❌ No files found to check")
        return False
    
    # Check each file
    results = []
    total_issues = 0
    
    for filepath in files_to_check:
        result = check_article_quality(filepath)
        results.append(result)
        total_issues += len(result['issues'])
        
        # Print individual result
        status_emoji = {'PASS': '✅', 'WARN': '⚠️', 'FAIL': '❌', 'ERROR': '💥'}
        emoji = status_emoji.get(result['status'], '❓')
        print(f"{emoji} {result['file']}: {result['word_count']} words, {result['sections']} sections")
        
        if result['issues']:
            for issue in result['issues']:
                print(f"  • {issue}")
    
    # Summary
    print(f"\n📊 Quality Check Summary:")
    passed = sum(1 for r in results if r['status'] == 'PASS')
    warned = sum(1 for r in results if r['status'] == 'WARN')
    failed = sum(1 for r in results if r['status'] == 'FAIL')
    errors = sum(1 for r in results if r['status'] == 'ERROR')
    
    print(f"  ✅ Passed: {passed}")
    print(f"  ⚠️ Warnings: {warned}")
    print(f"  ❌ Failed: {failed}")
    print(f"  💥 Errors: {errors}")
    print(f"  📋 Total issues: {total_issues}")
    
    # Determine overall success
    if errors > 0 or failed > 3:
        print("❌ Quality check failed - too many issues")
        return False
    elif total_issues == 0:
        print("🎉 All quality checks passed!")
        return True
    else:
        print("⚠️ Quality check passed with minor issues")
        return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)