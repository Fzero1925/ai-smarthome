#!/usr/bin/env python3
"""
图片API配置管理
用于管理各种图片API的密钥和配置
"""

import os
from typing import Dict, Optional

class ImageAPIConfig:
    """图片API配置管理器"""
    
    def __init__(self):
        self.config = {
            # Unsplash API配置
            'unsplash': {
                'access_key': os.getenv('UNSPLASH_ACCESS_KEY', ''),
                'secret_key': os.getenv('UNSPLASH_SECRET_KEY', ''),
                'rate_limit_per_hour': 50,  # 免费版限制
                'signup_url': 'https://unsplash.com/developers',
                'description': '高质量专业摄影图片，免费商用'
            },
            
            # Pexels API配置
            'pexels': {
                'api_key': os.getenv('PEXELS_API_KEY', ''),
                'rate_limit_per_hour': 200,  # 免费版限制
                'signup_url': 'https://www.pexels.com/api/',
                'description': '免费高分辨率图片和视频'
            },
            
            # Pixabay API配置
            'pixabay': {
                'api_key': os.getenv('PIXABAY_API_KEY', ''),
                'rate_limit_per_hour': 100,  # 保守估计
                'signup_url': 'https://pixabay.com/api/docs/',
                'description': '超过250万张免费图片和视频'
            }
        }
    
    def get_api_keys(self) -> Dict[str, str]:
        """获取所有已配置的API密钥"""
        keys = {}
        
        if self.config['unsplash']['access_key']:
            keys['unsplash'] = self.config['unsplash']['access_key']
        
        if self.config['pexels']['api_key']:
            keys['pexels'] = self.config['pexels']['api_key']
        
        if self.config['pixabay']['api_key']:
            keys['pixabay'] = self.config['pixabay']['api_key']
        
        return keys
    
    def is_configured(self, api_name: str) -> bool:
        """检查特定API是否已配置"""
        if api_name == 'unsplash':
            return bool(self.config['unsplash']['access_key'])
        elif api_name == 'pexels':
            return bool(self.config['pexels']['api_key'])
        elif api_name == 'pixabay':
            return bool(self.config['pixabay']['api_key'])
        return False
    
    def get_signup_instructions(self) -> str:
        """获取API申请说明"""
        instructions = """
🔑 免费图片API申请指南
============================

为了获得高质量的图片资源，您需要申请以下免费API：

1. 📷 Unsplash API (推荐)
   - 网址: https://unsplash.com/developers
   - 限制: 50次/小时 (免费版)
   - 优势: 专业摄影师作品，质量极高
   - 步骤: 注册账户 → 创建应用 → 获取Access Key

2. 📸 Pexels API
   - 网址: https://www.pexels.com/api/
   - 限制: 200次/小时 (免费版)
   - 优势: 丰富的商用免费图片库
   - 步骤: 注册账户 → 获取API Key

3. 🌟 Pixabay API
   - 网址: https://pixabay.com/api/docs/
   - 限制: 5000次/月 (免费版)
   - 优势: 超过250万张免费图片
   - 步骤: 注册账户 → 获取API Key

💡 配置方法:
1. 获得API密钥后，设置环境变量:
   - UNSPLASH_ACCESS_KEY=your_key_here
   - PEXELS_API_KEY=your_key_here  
   - PIXABAY_API_KEY=your_key_here

2. 或者直接在代码中调用:
   manager.setup_api_keys({
       'unsplash': 'your_access_key',
       'pexels': 'your_api_key',
       'pixabay': 'your_api_key'
   })

🚀 优先级推荐:
1. Unsplash (质量最高)
2. Pexels (数量丰富)  
3. Pixabay (备用选择)

⚡ 速率限制策略:
- 系统会自动轮换API避免超限
- 智能缓存减少重复请求
- 失败自动降级到其他API
        """
        return instructions
    
    def get_current_status(self) -> Dict:
        """获取当前配置状态"""
        status = {
            'configured_apis': [],
            'total_rate_limit_per_hour': 0,
            'missing_apis': []
        }
        
        for api_name, config in self.config.items():
            if self.is_configured(api_name):
                status['configured_apis'].append(api_name)
                status['total_rate_limit_per_hour'] += config['rate_limit_per_hour']
            else:
                status['missing_apis'].append(api_name)
        
        return status


def main():
    """演示配置管理功能"""
    config = ImageAPIConfig()
    
    print("🔑 图片API配置状态检查")
    print("=" * 40)
    
    status = config.get_current_status()
    
    print(f"✅ 已配置的API: {', '.join(status['configured_apis']) if status['configured_apis'] else '无'}")
    print(f"❌ 缺失的API: {', '.join(status['missing_apis'])}")
    print(f"⚡ 总速率限制: {status['total_rate_limit_per_hour']} 次/小时")
    
    if not status['configured_apis']:
        print("\n" + config.get_signup_instructions())
    else:
        print(f"\n🎉 系统就绪! 可处理 {status['total_rate_limit_per_hour']} 次图片搜索/小时")


if __name__ == "__main__":
    main()