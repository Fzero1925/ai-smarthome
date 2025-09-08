#!/usr/bin/env python3
"""
Real-time trending workflow script for GitHub Actions
Separated from YAML for better error handling and debugging
"""

import asyncio
import json
import sys
import os
import argparse
import codecs
from datetime import datetime, timezone

# 解决Windows编码问题
if sys.platform == "win32":
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

def setup_environment():
    """设置环境和模块路径"""
    sys.path.append('.')
    
    # 创建必要的目录
    os.makedirs('data/realtime_trends', exist_ok=True)
    os.makedirs('data/generation_history', exist_ok=True)
    os.makedirs('data/trending_cache', exist_ok=True)

async def run_trending_analysis(force_analysis=False, check_only=False, max_articles=2):
    """执行实时热点分析和内容生成触发"""
    
    try:
        from modules.trending.realtime_trigger import manual_trigger_check
        from modules.trending.realtime_analyzer import analyze_current_trends
        
        print('🔍 分析当前热点趋势...')
        
        # 分析热点
        trends_result = await analyze_current_trends(force_analysis=force_analysis)
        
        print(f"📊 发现 {trends_result['analysis_summary']['total_topics']} 个热点话题")
        print(f"📈 紧急话题: {trends_result['analysis_summary']['urgent_topics']} 个")
        print(f"💰 高商业价值: {trends_result['analysis_summary']['high_commercial_value']} 个")
        
        # 检查是否仅分析
        if check_only:
            print('ℹ️ 仅分析模式，不触发文章生成')
            result = {
                'action': 'analysis_only',
                'trends_analyzed': trends_result['analysis_summary']['total_topics'],
                'urgent_topics': trends_result['analysis_summary']['urgent_topics'],
                'generated_articles': 0
            }
        else:
            # 执行触发检查
            print('🚀 检查是否需要触发文章生成...')
            trigger_result = await manual_trigger_check(force=True)
            
            result = {
                'action': 'trigger_check',
                'trends_analyzed': trends_result['analysis_summary']['total_topics'],
                'triggers_attempted': trigger_result['analysis_summary']['triggers_attempted'],
                'successful_generations': trigger_result['analysis_summary']['successful_generations'],
                'failed_generations': trigger_result['analysis_summary']['failed_generations'],
                'generated_articles': trigger_result['analysis_summary']['successful_generations']
            }
        
        # 输出结果到文件
        with open('trigger_result.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        # 设置GitHub Actions输出变量
        if os.environ.get('GITHUB_OUTPUT'):
            print('设置GitHub Actions输出变量...')
            with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
                f.write(f"action={result['action']}\n")
                f.write(f"trends_analyzed={result['trends_analyzed']}\n")
                f.write(f"generated_articles={result.get('generated_articles', 0)}\n")
                f.write(f"has_new_content={'true' if result.get('generated_articles', 0) > 0 else 'false'}\n")
        
        print('✅ 热点分析完成!')
        return result
        
    except Exception as e:
        print(f'❌ 热点分析失败: {e}')
        import traceback
        traceback.print_exc()
        
        # 设置错误状态
        error_result = {
            'action': 'error',
            'trends_analyzed': 0,
            'generated_articles': 0,
            'error_message': str(e)
        }
        
        with open('trigger_result.json', 'w', encoding='utf-8') as f:
            json.dump(error_result, f, indent=2, ensure_ascii=False)
        
        if os.environ.get('GITHUB_OUTPUT'):
            with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
                f.write('action=error\n')
                f.write('trends_analyzed=0\n')
                f.write('generated_articles=0\n')
                f.write('has_new_content=false\n')
        
        return error_result

def main():
    """主函数，处理命令行参数"""
    parser = argparse.ArgumentParser(description='Real-time trending analysis and content generation')
    parser.add_argument('--force-analysis', action='store_true', 
                       help='Force analysis regardless of time zone restrictions')
    parser.add_argument('--check-only', action='store_true', 
                       help='Only analyze trends, do not generate articles')
    parser.add_argument('--max-articles', type=int, default=2, 
                       help='Maximum number of articles to generate')
    
    args = parser.parse_args()
    
    print(f"🚀 开始实时热点工作流程...")
    print(f"⚙️ 参数: force_analysis={args.force_analysis}, check_only={args.check_only}, max_articles={args.max_articles}")
    
    # 设置环境
    setup_environment()
    
    # 运行分析
    result = asyncio.run(run_trending_analysis(
        force_analysis=args.force_analysis,
        check_only=args.check_only,
        max_articles=args.max_articles
    ))
    
    # 根据结果设置退出代码
    if result['action'] == 'error':
        sys.exit(1)
    else:
        print(f"🎉 工作流程完成: {result['action']}")
        sys.exit(0)

if __name__ == '__main__':
    main()