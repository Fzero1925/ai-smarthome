#!/usr/bin/env python3
"""
Direct Telegram notification test script
"""
import os
import sys

# Add the current directory to Python path
sys.path.append('.')

# Set up environment variables for testing (you'll need to set these)
# Uncomment and set these with your actual values for testing:
# os.environ['TELEGRAM_BOT_TOKEN'] = 'your_bot_token_here'
# os.environ['TELEGRAM_CHAT_ID'] = 'your_chat_id_here'

try:
    from scripts.notify_telegram import TelegramNotifier
    
    print("🔧 Direct Telegram Notification Test")
    print("=" * 50)
    
    # Test basic connectivity
    try:
        notifier = TelegramNotifier()
        print("✅ TelegramNotifier initialized successfully")
        
        # Test article notification
        test_articles = [
            {
                'title': 'Best Smart Plugs 2025: Complete Guide',
                'category': 'smart-plugs',
                'word_count': 2500,
                'keywords': ['smart plug', 'alexa', 'wifi']
            }
        ]
        
        print("📝 Testing article notification...")
        result = notifier.send_article_notification(
            articles=test_articles,
            site_url='https://ai-smarthome.vercel.app',
            force=True  # Force send even during quiet hours
        )
        
        if result:
            print("✅ Article notification sent successfully!")
        else:
            print("❌ Article notification failed")
            
        # Test build notification
        print("🔧 Testing build notification...")
        build_result = notifier.send_build_notification(
            status='success',
            site_url='https://ai-smarthome.vercel.app',
            commit_message='test: 测试Telegram通知功能',
            duration='2m 30s',
            force=True
        )
        
        if build_result:
            print("✅ Build notification sent successfully!")
        else:
            print("❌ Build notification failed")
            
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("\n💡 To test this script:")
        print("1. Set TELEGRAM_BOT_TOKEN environment variable")
        print("2. Set TELEGRAM_CHAT_ID environment variable")
        print("3. Run: python direct_telegram_test.py")
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure the notify_telegram.py script exists and is working")

print("=" * 50)
print("Test completed.")