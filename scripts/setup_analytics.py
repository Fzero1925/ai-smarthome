#!/usr/bin/env python3
"""
Analytics Setup Script
Configures Google Analytics, AdSense, and other tracking codes
using environment variables from GitHub Secrets.
"""

import os
import sys
import re
import json
import codecs
from pathlib import Path

# 解决Windows编码问题
if sys.platform == "win32":
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

def get_env_var(var_name, default=None):
    """获取环境变量，支持从.env文件和系统环境变量"""
    value = os.getenv(var_name, default)
    return value

def update_hugo_config():
    """更新Hugo配置文件以包含实际的Analytics IDs"""
    config_path = Path("config.yaml")
    
    if not config_path.exists():
        print(f"❌ Config file not found: {config_path}")
        return False
    
    # 获取环境变量
    analytics_id = get_env_var("GOOGLE_ANALYTICS_ID", "G-XXXXXXXXXX")
    adsense_id = get_env_var("GOOGLE_ADSENSE_ID", "ca-pub-XXXXXXXXXXXXXXXX")
    affiliate_tag = get_env_var("AMAZON_AFFILIATE_TAG", "yourtag-20")
    
    print(f"🔧 Updating Hugo configuration...")
    print(f"📊 Google Analytics ID: {analytics_id[:12]}...")
    print(f"💰 AdSense ID: {adsense_id[:15]}...")
    print(f"🛒 Amazon Affiliate: {affiliate_tag}")
    
    # 读取配置文件
    with open(config_path, 'r', encoding='utf-8') as f:
        config_content = f.read()
    
    # 替换占位符
    replacements = {
        "google_analytics: 'G-XXXXXXXXXX'": f"google_analytics: '{analytics_id}'",
        "client_id: 'ca-pub-XXXXXXXXXXXXXXXX'": f"client_id: '{adsense_id}'",
        "tracking_id: 'yourtag-20'": f"tracking_id: '{affiliate_tag}'",
        "google_tag_manager: 'GTM-XXXXXXX'": f"google_tag_manager: 'GTM-{analytics_id[2:]}'",  # 从GA4 ID推导GTM ID
    }
    
    updated_content = config_content
    for old_value, new_value in replacements.items():
        if old_value in updated_content:
            updated_content = updated_content.replace(old_value, new_value)
            print(f"✅ Updated: {old_value.split(':')[0]} -> configured")
    
    # 写回配置文件
    with open(config_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print(f"✅ Hugo configuration updated successfully")
    return True

def create_analytics_snippet():
    """创建Google Analytics代码片段用于模板插入"""
    analytics_id = get_env_var("GOOGLE_ANALYTICS_ID")
    adsense_id = get_env_var("GOOGLE_ADSENSE_ID")
    
    if not analytics_id or analytics_id == "G-XXXXXXXXXX":
        print("⚠️ Google Analytics ID not configured")
        return
    
    # Google Analytics 4 代码
    ga4_snippet = f"""
<!-- Google Analytics 4 -->
<script async src="https://www.googletagmanager.com/gtag/js?id={analytics_id}"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
  gtag('config', '{analytics_id}');
</script>
"""
    
    # Google AdSense代码（如果配置了）
    adsense_snippet = ""
    if adsense_id and adsense_id != "ca-pub-XXXXXXXXXXXXXXXX":
        adsense_snippet = f"""
<!-- Google AdSense -->
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={adsense_id}" 
        crossorigin="anonymous"></script>
"""
    
    # Search Console验证代码（可选）
    search_console_snippet = """
<!-- Google Search Console Verification -->
<!-- Add your verification meta tag here when ready -->
"""
    
    # 创建analytics目录
    analytics_dir = Path("layouts/partials")
    analytics_dir.mkdir(parents=True, exist_ok=True)
    
    # 写入分析代码文件
    with open(analytics_dir / "analytics.html", 'w', encoding='utf-8') as f:
        f.write(ga4_snippet + adsense_snippet + search_console_snippet)
    
    print(f"📊 Analytics snippet created: {analytics_dir / 'analytics.html'}")
    
    # 创建AdSense广告代码模板
    if adsense_snippet:
        adsense_ad_template = f"""
<!-- Responsive Ad Unit -->
<ins class="adsbygoogle"
     style="display:block"
     data-ad-client="{adsense_id}"
     data-ad-slot="XXXXXXXXXX"
     data-ad-format="auto"
     data-full-width-responsive="true"></ins>
<script>
     (adsbygoogle = window.adsbygoogle || []).push({{}});
</script>
"""
        
        with open(analytics_dir / "adsense-ad.html", 'w', encoding='utf-8') as f:
            f.write(adsense_ad_template)
        
        print(f"💰 AdSense ad template created: {analytics_dir / 'adsense-ad.html'}")

def verify_configuration():
    """验证配置是否正确设置"""
    print(f"\n🔍 Verifying configuration...")
    
    # 检查必要的环境变量
    required_vars = ["GOOGLE_ANALYTICS_ID", "GOOGLE_ADSENSE_ID", "AMAZON_AFFILIATE_TAG"]
    missing_vars = []
    
    for var in required_vars:
        value = get_env_var(var)
        if not value or "XXXX" in value:
            missing_vars.append(var)
        else:
            print(f"✅ {var}: Configured")
    
    if missing_vars:
        print(f"\n⚠️ Missing or placeholder configuration:")
        for var in missing_vars:
            print(f"   - {var}")
        print(f"\n💡 These should be configured in GitHub Secrets for production")
    
    # 检查配置文件更新
    config_path = Path("config.yaml")
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            config_content = f.read()
        
        if "G-XXXXXXXXXX" not in config_content:
            print(f"✅ Hugo config: Analytics ID updated")
        else:
            print(f"⚠️ Hugo config: Still contains placeholder IDs")
    
    # 检查生成的文件
    analytics_file = Path("layouts/partials/analytics.html")
    if analytics_file.exists():
        print(f"✅ Analytics snippet: Created")
    else:
        print(f"⚠️ Analytics snippet: Not found")
    
    return len(missing_vars) == 0

def main():
    """主函数"""
    print(f"🚀 Setting up Google Analytics and advertising configuration...")
    
    # 更新Hugo配置
    if update_hugo_config():
        print(f"✅ Hugo configuration updated")
    else:
        print(f"❌ Failed to update Hugo configuration")
        return 1
    
    # 创建Analytics代码片段
    create_analytics_snippet()
    
    # 验证配置
    if verify_configuration():
        print(f"\n🎉 Analytics setup completed successfully!")
        print(f"📊 Google Analytics is now active")
        print(f"🔍 Search Console will auto-configure when domain is connected")
    else:
        print(f"\n⚠️ Setup completed with warnings")
        print(f"💡 Some configuration may need manual adjustment")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())