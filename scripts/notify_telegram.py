#!/usr/bin/env python3
"""
Simple & Reliable Telegram Notification Script
Optimized for stability and speed (7-second target)
"""

import os
import sys
import argparse
import codecs
import requests
from datetime import datetime
import pytz

# 解决Windows编码问题
if sys.platform == "win32":
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

def send_telegram_message(message, bot_token=None, chat_id=None):
    """Send a simple message to Telegram - reliable single function"""
    bot_token = bot_token or os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = chat_id or os.getenv('TELEGRAM_CHAT_ID')
    
    if not bot_token or not chat_id:
        print("❌ Missing Telegram credentials")
        return False
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'Markdown',
        'disable_web_page_preview': True
    }
    
    try:
        response = requests.post(url, data=payload, timeout=5)
        if response.status_code == 200:
            print("✅ Telegram notification sent successfully")
            return True
        else:
            print(f"❌ Telegram API error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Failed to send Telegram message: {e}")
        return False

def get_china_time():
    """Get current time in China timezone"""
    try:
        china_tz = pytz.timezone('Asia/Shanghai')
        return datetime.now(china_tz).strftime('%m-%d %H:%M')
    except:
        return datetime.now().strftime('%m-%d %H:%M')

def format_daily_content_message(status, generated, reason, article_count=0):
    """Format message for daily content workflow"""
    china_time = get_china_time()
    
    if status == "success" and generated == "true":
        status_emoji = "✅"
        status_text = "内容生成成功"
        details = f"📝 生成: {article_count} 篇新文章"
    elif status == "success" and generated == "false":
        status_emoji = "ℹ️"
        status_text = "内容生成跳过"
        details = f"原因: {reason}"
    else:
        status_emoji = "❌"
        status_text = "内容生成失败"
        details = "请检查工作流日志"
    
    return f"""{status_emoji} *AI智能家居中心* | {china_time}

*状态*: {status_text}

{details}

*网站*: [ai-smarthome.vercel.app](https://ai-smarthome.vercel.app/)

_🤖 Claude Code 自动化_"""

def count_generated_articles():
    """Count articles from generated_files.txt"""
    try:
        if os.path.exists('generated_files.txt'):
            with open('generated_files.txt', 'r') as f:
                return len([line for line in f if line.strip()])
    except:
        pass
    return 0

def main():
    parser = argparse.ArgumentParser(description='Send simple Telegram notifications')
    parser.add_argument('--type', required=True, help='Notification type')
    parser.add_argument('--status', help='Job status')
    parser.add_argument('--generated', help='Content was generated (true/false)')
    parser.add_argument('--reason', help='Reason for generation/skip')
    parser.add_argument('--message', help='Custom message')
    
    args = parser.parse_args()
    
    try:
        if args.type == 'daily_content':
            article_count = count_generated_articles()
            message = format_daily_content_message(
                args.status or 'unknown',
                args.generated or 'false', 
                args.reason or 'unknown',
                article_count
            )
            
        elif args.type == 'simple_test':
            china_time = get_china_time()
            message = f"""🧪 *测试通知* | {china_time}

✅ Telegram 连接正常
🤖 新workflow运行中

_Claude Code 测试_"""
            
        elif args.type == 'custom':
            message = args.message or "📢 自定义通知"
            
        else:
            message = f"📢 {args.type}: {args.status or 'OK'}"
        
        success = send_telegram_message(message)
        sys.exit(0 if success else 1)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()