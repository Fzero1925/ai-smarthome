#!/usr/bin/env python3
"""
Simplified Telegram test using only basic libraries
"""
import os
import requests
from datetime import datetime

def test_telegram_basic():
    """Test basic Telegram functionality"""
    
    # You need to set these environment variables with your actual values
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    if not bot_token:
        print("❌ TELEGRAM_BOT_TOKEN not found")
        print("💡 Please set: export TELEGRAM_BOT_TOKEN='your_bot_token'")
        return False
        
    if not chat_id:
        print("❌ TELEGRAM_CHAT_ID not found")
        print("💡 Please set: export TELEGRAM_CHAT_ID='your_chat_id'")
        return False
    
    print(f"🔧 Testing Telegram Bot")
    print(f"📍 Bot Token: {bot_token[:10]}...")
    print(f"📍 Chat ID: {chat_id}")
    print("=" * 50)
    
    # Test 1: Bot info
    try:
        print("1️⃣ Testing bot connection...")
        url = f"https://api.telegram.org/bot{bot_token}/getMe"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        bot_info = response.json()
        if bot_info.get('ok'):
            bot_name = bot_info['result'].get('first_name', 'Unknown')
            print(f"   ✅ Bot connected: {bot_name}")
        else:
            print(f"   ❌ Bot error: {bot_info}")
            return False
            
    except Exception as e:
        print(f"   ❌ Connection failed: {e}")
        return False
    
    # Test 2: Send simple message
    try:
        print("2️⃣ Sending test message...")
        
        test_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        message = f"""🧪 *Telegram通知测试成功* 

*测试时间*: {test_time}
*测试内容*: 基础连接和消息发送
*系统状态*: ✅ 正常工作

*网站链接*: [ai-smarthome.vercel.app](https://ai-smarthome.vercel.app/)

_🤖 Claude Code 手动测试_"""
        
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            'chat_id': chat_id,
            'text': message,
            'parse_mode': 'Markdown',
            'disable_web_page_preview': True
        }
        
        response = requests.post(url, data=payload, timeout=10)
        response.raise_for_status()
        
        result = response.json()
        if result.get('ok'):
            print("   ✅ Test message sent successfully!")
            return True
        else:
            print(f"   ❌ Message failed: {result}")
            return False
            
    except Exception as e:
        print(f"   ❌ Send failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Simple Telegram Test Script")
    print("=" * 50)
    
    success = test_telegram_basic()
    
    print("=" * 50)
    if success:
        print("🎉 All tests passed! Telegram notifications are working.")
    else:
        print("❌ Tests failed. Please check your configuration.")
        print("\n💡 Next steps:")
        print("1. Verify your bot token and chat ID")
        print("2. Make sure the bot has permission to send messages")
        print("3. Check your network connection")
    
    print("\n📋 To use in production:")
    print("1. Set these as GitHub repository secrets:")
    print("   - TELEGRAM_BOT_TOKEN")
    print("   - TELEGRAM_CHAT_ID")
    print("2. The GitHub Actions workflow will use them automatically")