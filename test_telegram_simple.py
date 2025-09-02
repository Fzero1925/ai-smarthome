#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单Telegram测试脚本 - 解决Windows编码问题
"""

import os
import sys
import requests

# 解决Windows中文编码问题
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

def test_telegram_connection():
    """测试Telegram连接"""
    bot_token = "8494031502:AAHrT6csi5COqeUgG-wk_SiaYNjiXOFB-m4"
    chat_id = "6041888803"
    
    if not bot_token or not chat_id:
        print("ERROR: 缺少Telegram凭据")
        return False
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    message = """🧪 测试通知 | 09-02 20:50

✅ Python环境正常
✅ 核心依赖已安装  
🤖 新workflow准备就绪

_Claude Code 测试成功_"""
    
    payload = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'Markdown',
        'disable_web_page_preview': True
    }
    
    try:
        print("正在发送Telegram测试消息...")
        response = requests.post(url, data=payload, timeout=10)
        
        if response.status_code == 200:
            print("✅ Telegram通知发送成功!")
            return True
        else:
            print(f"❌ Telegram API错误: {response.status_code}")
            print(f"响应: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return False

if __name__ == "__main__":
    success = test_telegram_connection()
    sys.exit(0 if success else 1)