#!/usr/bin/env python3
"""
测试增强后的Telegram通知格式
显示新的消息格式和功能
"""

import sys
import os
sys.path.append('scripts')

# 导入notify_telegram模块的函数
from notify_telegram import format_daily_content_message, format_keyword_info, load_keyword_analysis

def test_enhanced_notification():
    """测试增强后的通知格式"""
    print("🧪 测试增强后的Telegram通知格式")
    print("=" * 50)
    
    # 测试成功的内容生成通知
    message = format_daily_content_message('success', 'true', 'keyword analysis complete', 1)
    
    print("📱 增强后的消息格式:")
    print("-" * 30)
    print(message)
    print("-" * 30)
    
    # 测试关键词分析功能
    keywords_data = load_keyword_analysis()
    if keywords_data:
        print("\n🔍 关键词分析测试:")
        print("-" * 30)
        keyword_info = format_keyword_info(keywords_data)
        print(keyword_info)
        print("-" * 30)
    else:
        print("\n⚠️ 没有找到关键词分析数据")
    
    print("\n✅ 测试完成！")
    print("\n📊 增强功能总结:")
    print("• ✅ 详细的质量评分和星级显示")
    print("• ✅ 商业化进展跟踪")
    print("• ✅ 系统状态监控")
    print("• ✅ 收益潜力分析")
    print("• ✅ 竞争难度可视化")
    print("• ✅ 预期排名评估")
    print("• ✅ 下一步行动提醒")

if __name__ == "__main__":
    test_enhanced_notification()