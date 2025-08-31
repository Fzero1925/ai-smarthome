#!/usr/bin/env python3
"""
Test script for Telegram notification functionality
"""
import os
import sys
import requests
from datetime import datetime
import pytz

def test_telegram_connection():
    """Test basic Telegram bot connection"""
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    if not bot_token or not chat_id:
        print("❌ Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID environment variables")
        return False
    
    # Test bot info
    try:
        url = f"https://api.telegram.org/bot{bot_token}/getMe"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        bot_info = response.json()
        if bot_info.get('ok'):
            bot_name = bot_info['result'].get('first_name', 'Unknown')
            print(f"✅ Bot connection successful: {bot_name}")
        else:
            print(f"❌ Bot API error: {bot_info.get('description', 'Unknown error')}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")
        return False
    
    return True

def send_test_message():
    """Send a test message"""
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    if not bot_token or not chat_id:
        return False
    
    # Format China time
    china_tz = pytz.timezone('Asia/Shanghai')
    china_time = datetime.now(china_tz).strftime('%m-%d %H:%M')
    
    message = f"""🧪 *Telegram 通知测试* | {china_time}

*测试项目*:
✅ Bot连接正常
✅ 消息发送功能
✅ 中国时区显示
✅ Markdown格式支持

*系统信息*:
📍 测试时间: {datetime.now().isoformat()}
🌐 [网站地址](https://ai-smarthome.vercel.app/)

_🤖 Claude Code 测试完成_"""
    
    try:
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
            print("✅ Test message sent successfully")
            return True
        else:
            print(f"❌ Message send failed: {result.get('description', 'Unknown error')}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to send message: {e}")
        return False

def main():
    """Main test function"""
    print("🔧 Testing Telegram notification system...")
    print("=" * 50)
    
    # Test 1: Check environment variables
    print("1. Checking environment variables...")
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    if bot_token:
        print(f"   ✅ TELEGRAM_BOT_TOKEN: {bot_token[:10]}...")
    else:
        print("   ❌ TELEGRAM_BOT_TOKEN: Not found")
    
    if chat_id:
        print(f"   ✅ TELEGRAM_CHAT_ID: {chat_id}")
    else:
        print("   ❌ TELEGRAM_CHAT_ID: Not found")
    
    print()
    
    # Test 2: Bot connection
    print("2. Testing bot connection...")
    connection_ok = test_telegram_connection()
    print()
    
    # Test 3: Send test message
    if connection_ok:
        print("3. Sending test message...")
        message_ok = send_test_message()
        print()
        
        if message_ok:
            print("🎉 All tests passed! Telegram notifications are working.")
        else:
            print("⚠️ Message sending failed, but bot connection is OK.")
    else:
        print("❌ Bot connection failed, skipping message test.")
    
    print("=" * 50)
    print("Test completed.")

if __name__ == "__main__":
    main()