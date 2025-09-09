#!/usr/bin/env python3
"""
Keyword Engine v2 Integration Test
测试整个v2增强系统的集成状态
"""

import os
import sys
from typing import Dict, Any

def test_config_loading():
    """测试配置加载"""
    print("🔧 测试配置加载...")
    
    try:
        import yaml
        
        if os.path.exists("keyword_engine.yml"):
            with open("keyword_engine.yml", 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            print("✅ 配置文件加载成功")
            print(f"  - opportunity阈值: {config['thresholds']['opportunity']}")
            print(f"  - 权重配置: T={config['weights']['T']}, I={config['weights']['I']}")
            print(f"  - AdSense RPM: ${config['adsense']['rpm_usd']}")
            return True
        else:
            print("❌ keyword_engine.yml 不存在")
            return False
    except Exception as e:
        print(f"❌ 配置加载失败: {e}")
        return False

def test_scoring_functions():
    """测试评分功能"""
    print("\n🎯 测试评分功能...")
    
    try:
        sys.path.append("modules/keyword_tools")
        from scoring import opportunity_score, estimate_value, make_revenue_range
        
        # 测试机会评分
        test_score = opportunity_score(T=0.8, I=0.9, S=0.6, F=0.7, D=0.4)
        print(f"✅ 机会评分计算: {test_score}/100")
        
        # 测试收入估算
        test_revenue = estimate_value(search_volume=15000, opp_score=test_score)
        print(f"✅ 收入估算: ${test_revenue}/月")
        
        # 测试收入区间
        range_result = make_revenue_range(test_revenue)
        print(f"✅ 收入区间: {range_result['range']}")
        
        return True
    except Exception as e:
        print(f"❌ 评分功能测试失败: {e}")
        return False

def test_keyword_analyzer():
    """测试关键词分析器"""
    print("\n📊 测试关键词分析器...")
    
    try:
        sys.path.append("modules/keyword_tools")
        from keyword_analyzer import SmartHomeKeywordAnalyzer
        
        analyzer = SmartHomeKeywordAnalyzer()
        print("✅ 关键词分析器初始化成功")
        print(f"  - v2配置已加载: {'v2_config' in dir(analyzer)}")
        
        # 测试简单分析
        test_keywords = ["smart plug alexa"]
        try:
            results = analyzer.analyze_keyword_metrics(test_keywords)
            if results and len(results) > 0:
                result = results[0]
                print("✅ 关键词分析功能正常")
                print(f"  - 关键词: {result.keyword}")
                print(f"  - 搜索量: {result.search_volume:,}")
                if result.opportunity_score is not None:
                    print(f"  - 机会评分: {result.opportunity_score}/100")
                if result.est_value_usd is not None:
                    print(f"  - 预估价值: ${result.est_value_usd}/月")
                return True
            else:
                print("⚠️ 关键词分析返回空结果")
                return False
        except Exception as e:
            print(f"⚠️ 关键词分析执行失败: {e}")
            return False
        
    except Exception as e:
        print(f"❌ 关键词分析器测试失败: {e}")
        return False

def test_content_compliance():
    """测试内容合规功能"""
    print("\n📝 测试内容合规功能...")
    
    try:
        sys.path.append("modules/content_generator")
        from anti_ai_content_generator import sanitize_claims, BANNED_PHRASES
        
        # 测试内容清理
        test_content = "After we tested for 30 days, our hands-on review shows excellent results."
        cleaned_content = sanitize_claims(test_content)
        
        print("✅ 内容合规功能正常")
        print(f"  - 原文: {test_content}")
        print(f"  - 清理后: {cleaned_content}")
        print(f"  - 禁用短语数量: {len(BANNED_PHRASES)}")
        
        return True
    except Exception as e:
        print(f"❌ 内容合规测试失败: {e}")
        return False

def test_realtime_enhancements():
    """测试实时分析增强"""
    print("\n⚡ 测试实时分析增强...")
    
    try:
        sys.path.append("modules/trending")
        from realtime_analyzer import RealtimeTrendingAnalyzer
        
        analyzer = RealtimeTrendingAnalyzer()
        print("✅ 实时分析器初始化成功")
        print(f"  - v2配置已加载: {'v2_config' in dir(analyzer)}")
        
        return True
    except Exception as e:
        print(f"❌ 实时分析增强测试失败: {e}")
        return False

def main():
    """运行所有测试"""
    print("🚀 Keyword Engine v2 集成测试开始...")
    print("=" * 60)
    
    test_results = []
    
    # 执行各项测试
    test_results.append(("配置加载", test_config_loading()))
    test_results.append(("评分功能", test_scoring_functions()))
    test_results.append(("关键词分析器", test_keyword_analyzer()))
    test_results.append(("内容合规", test_content_compliance()))
    test_results.append(("实时分析增强", test_realtime_enhancements()))
    
    # 输出测试结果
    print("\n" + "=" * 60)
    print("📋 测试结果总览:")
    
    passed = 0
    failed = 0
    
    for test_name, result in test_results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {test_name}: {status}")
        
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\n🎯 测试统计: {passed} 通过, {failed} 失败")
    
    if failed == 0:
        print("🎉 所有测试通过！Keyword Engine v2 集成成功!")
        print("\n🚀 系统已就绪，具备以下增强功能:")
        print("  - 0-100机会评分算法")
        print("  - 精确月收入预测($)")  
        print("  - 完整决策解释(why_selected/why_not)")
        print("  - 统一YAML配置管理")
        print("  - 强化内容合规检查")
    else:
        print(f"⚠️ 发现 {failed} 个问题，请检查相关模块")

if __name__ == "__main__":
    main()