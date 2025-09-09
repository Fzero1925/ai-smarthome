#!/usr/bin/env python3
"""
测试v2增强Telegram通知格式
本地验证所有新功能
"""

import sys
import os

# 添加路径以便导入notify_telegram模块
sys.path.append('scripts')

try:
    from notify_telegram import format_v2_test_message, format_v2_keyword_analysis, format_alternative_keywords_analysis, format_v2_system_status, format_decision_transparency
    print("✅ 成功导入v2通知模块")
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    sys.exit(1)

def test_v2_functions():
    """测试各个v2功能函数"""
    print("\n🧪 测试v2功能函数...")
    
    # 测试关键词数据
    test_keyword = {
        'keyword': 'smart thermostat wifi',
        'search_volume': 12500,
        'trend_score': 0.75,
        'commercial_intent': 0.85,
        'difficulty_score': 0.50,
        'opportunity_score': 71.5,
        'est_value_usd': 385.20,
        'seasonality_score': 0.60,
        'site_fit_score': 0.88,
        'source': 'youtube',
        'why_selected': {
            'trend': 'Last-30% mean +12% vs overall',
            'intent': 'Intent hits: wifi, smart, thermostat',
            'difficulty': 'Medium; seasonal advantage opportunity'
        },
        'revenue_breakdown': {
            'adsense': 280.40,
            'amazon': 385.20
        }
    }
    
    # 测试备选关键词
    alt_keywords = [
        {
            'keyword': 'nest thermostat review 2025',
            'opportunity_score': 66.8,
            'est_value_usd': 342.60,
            'search_volume': 11200,
            'commercial_intent': 0.92,
            'difficulty_score': 0.58
        }
    ]
    
    print("\n📊 测试v2关键词分析格式:")
    keyword_analysis = format_v2_keyword_analysis(test_keyword)
    print(keyword_analysis)
    
    print("\n📋 测试备选关键词分析:")
    alt_analysis = format_alternative_keywords_analysis(alt_keywords, test_keyword)
    print(alt_analysis)
    
    print("\n🛠️ 测试v2系统状态:")
    system_status = format_v2_system_status()
    print(system_status)
    
    print("\n🔍 测试决策透明化:")
    decision_analysis = format_decision_transparency(test_keyword)
    print(decision_analysis)

def test_complete_v2_message():
    """测试完整的v2消息格式"""
    print("\n" + "="*60)
    print("🚀 测试完整v2通知消息格式")
    print("="*60)
    
    try:
        message = format_v2_test_message()
        print(message)
        
        # 分析消息长度和结构
        lines = message.split('\n')
        print(f"\n📊 消息分析:")
        print(f"  总长度: {len(message)} 字符")
        print(f"  行数: {len(lines)}")
        print(f"  包含emoji: {'✅' if any('🎯' in line for line in lines) else '❌'}")
        print(f"  包含v2标识: {'✅' if 'v2' in message.lower() else '❌'}")
        print(f"  包含机会评分: {'✅' if 'opportunity_score' in message or '机会评分' in message else '❌'}")
        print(f"  包含收入预测: {'✅' if 'est_value_usd' in message or '预测' in message else '❌'}")
        
    except Exception as e:
        print(f"❌ 完整消息测试失败: {e}")
        import traceback
        traceback.print_exc()

def main():
    print("🧪 Keyword Engine v2 通知系统测试")
    print("="*50)
    
    # 测试各个功能函数
    test_v2_functions()
    
    # 测试完整消息格式
    test_complete_v2_message()
    
    print("\n" + "="*50)
    print("🎉 v2通知系统测试完成！")
    print("\n💡 使用说明:")
    print("  python scripts/notify_telegram.py --type v2_test")
    print("  (需要设置TELEGRAM_BOT_TOKEN和TELEGRAM_CHAT_ID)")

if __name__ == "__main__":
    main()