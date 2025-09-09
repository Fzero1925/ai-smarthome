#!/usr/bin/env python3
"""
一键图片设置脚本
快速为网站配置专业图片系统
"""

import os
import sys
import asyncio
import codecs
from pathlib import Path

# 解决Windows编码问题
if sys.platform == "win32":
    try:
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
        sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())
    except Exception:
        pass

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.image_manager import SmartImageManager
from scripts.image_config import ImageAPIConfig


async def setup_images_for_website():
    """为网站设置图片系统"""
    print("🖼️ AI Smart Home Hub - 图片系统设置")
    print("=" * 50)
    
    # 检查API配置
    config = ImageAPIConfig()
    status = config.get_current_status()
    
    print(f"📊 当前API状态:")
    print(f"   ✅ 已配置: {len(status['configured_apis'])} 个API")
    print(f"   ⚡ 可用额度: {status['total_rate_limit_per_hour']} 次/小时")
    
    if not status['configured_apis']:
        print("\n⚠️ 暂无API密钥，将使用演示模式")
        print("💡 申请API密钥后可获得真实的高质量图片")
        
        response = input("\n是否继续演示模式? (y/n): ").lower()
        if response != 'y':
            print("\n📋 API申请指南:")
            print(config.get_signup_instructions())
            return
    
    # 创建图片管理器
    print(f"\n🚀 初始化图片管理系统...")
    manager = SmartImageManager()
    
    # 设置API密钥（如果有的话）
    api_keys = config.get_api_keys()
    if api_keys:
        manager.setup_api_keys(api_keys)
        print(f"🔑 已配置 {len(api_keys)} 个API密钥")
    
    # 创建必要目录
    print(f"📁 创建图片目录结构...")
    image_dirs = [
        "static/images/products/smart-plugs",
        "static/images/products/smart-thermostats", 
        "static/images/products/smart-bulbs",
        "static/images/products/security-cameras",
        "static/images/products/robot-vacuums",
        "static/images/products/general",
        "logs"
    ]
    
    for dir_path in image_dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    print(f"✅ 目录结构创建完成")
    
    # 检查现有文章
    articles_dir = Path("content/articles")
    if articles_dir.exists():
        md_files = list(articles_dir.glob("*.md"))
        print(f"\n📝 发现 {len(md_files)} 篇文章需要处理图片")
        
        if md_files:
            response = input("是否立即处理所有文章? (y/n): ").lower()
            if response == 'y':
                print(f"\n🔄 开始批量处理文章图片...")
                results = await manager.batch_process_articles()
                
                # 显示处理结果
                successful = sum(1 for r in results if r.get('success'))
                total_images = sum(r.get('images_found', 0) for r in results if r.get('success'))
                
                print(f"\n✅ 批量处理完成!")
                print(f"📊 处理统计:")
                print(f"   - 成功处理: {successful}/{len(results)} 篇文章")
                print(f"   - 匹配图片: {total_images} 张")
                
                # 显示前几个成功的结果
                print(f"\n📋 处理结果预览:")
                shown = 0
                for result in results:
                    if result.get('success') and shown < 3:
                        print(f"   📄 {result['article']}")
                        print(f"      🔍 关键词: {result['keyword']}")
                        print(f"      📷 找到图片: {result['images_found']} 张")
                        print(f"      📂 类别: {result['category']}")
                        shown += 1
    else:
        print(f"\n⚠️ 文章目录 'content/articles' 不存在")
        print(f"💡 请确保在正确的项目目录中运行此脚本")
    
    # 显示后续步骤
    print(f"\n🎯 下一步操作建议:")
    
    if not status['configured_apis']:
        print(f"   1. 📝 申请免费API密钥 (Unsplash, Pexels, Pixabay)")
        print(f"   2. ⚙️ 配置环境变量或调用 setup_api_keys()")
        print(f"   3. 🔄 重新运行此脚本获得真实图片")
    else:
        print(f"   1. 🧹 检查生成的图片质量和相关性")
        print(f"   2. 🔧 手动调整不匹配的图片")
        print(f"   3. 🚀 运行 Hugo 构建网站")
    
    print(f"\n💡 高级功能:")
    print(f"   - 使用 image_manager.py 单独处理文章")
    print(f"   - 使用 image_config.py 管理API配置")
    print(f"   - 集成到GitHub Actions自动化流程")
    
    print(f"\n🌟 图片系统配置完成! AdSense申请就绪 🎉")


def main():
    """主入口点"""
    try:
        asyncio.run(setup_images_for_website())
    except KeyboardInterrupt:
        print(f"\n\n👋 用户取消操作")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()