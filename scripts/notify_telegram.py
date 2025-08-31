#!/usr/bin/env python3
"""
Telegram Notification Script for AI Smart Home Hub

This script sends notifications to Telegram about various events:
- New article publications
- Build/deployment status
- Performance metrics
- Error alerts
"""

import os
import sys
import argparse
import requests
import json
from datetime import datetime, timedelta
from pathlib import Path
import pytz


class TelegramNotifier:
    """Handle Telegram notifications for the AI Smart Home Hub"""
    
    def __init__(self, bot_token=None, chat_id=None):
        self.bot_token = bot_token or os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = chat_id or os.getenv('TELEGRAM_CHAT_ID')
        
        if not self.bot_token or not self.chat_id:
            raise ValueError("Telegram bot token and chat ID are required")
        
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        
        # Notification settings
        self.notification_levels = {
            'ERROR': 1,    # Critical errors - always send
            'WARNING': 2,  # Warnings - send during active hours
            'SUCCESS': 3,  # Success notifications - smart filtering
            'INFO': 4      # Info notifications - minimal sending
        }
        
        # China timezone for quiet hours
        self.china_tz = pytz.timezone('Asia/Shanghai')
    
    def _is_quiet_hours(self):
        """Check if current time is in quiet hours (22:00-08:00 China time)"""
        try:
            china_time = datetime.now(self.china_tz)
            hour = china_time.hour
            return hour >= 22 or hour < 8
        except:
            return False
    
    def _should_send_notification(self, level='INFO', force=False):
        """Determine if notification should be sent based on level and time"""
        if force:
            return True
        
        # Always send ERROR notifications
        if level == 'ERROR':
            return True
        
        # During quiet hours, only send ERROR and critical SUCCESS
        if self._is_quiet_hours():
            return level in ['ERROR']
        
        # During active hours, send ERROR, WARNING, and important SUCCESS
        return level in ['ERROR', 'WARNING', 'SUCCESS']
    
    def send_message(self, text, parse_mode="Markdown", disable_web_preview=True):
        """Send a message to Telegram"""
        url = f"{self.base_url}/sendMessage"
        
        payload = {
            'chat_id': self.chat_id,
            'text': text,
            'parse_mode': parse_mode,
            'disable_web_page_preview': disable_web_preview
        }
        
        try:
            response = requests.post(url, data=payload, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Failed to send Telegram message: {e}")
            return None
    
    def send_article_notification(self, articles, site_url=None, force=False):
        """Send notification about new articles with smart filtering"""
        if not articles:
            return False
        
        # Check if we should send this notification
        if not self._should_send_notification('SUCCESS', force):
            print(f"⏰ Skipping article notification - quiet hours or filtered")
            return False
        
        article_count = len(articles)
        emoji = "📝" if article_count == 1 else "📚"
        
        # More compact and informative message
        china_time = datetime.now(self.china_tz).strftime('%m-%d %H:%M')
        
        message = f"{emoji} *新内容发布* | {china_time}\n\n"
        
        if article_count == 1:
            article = articles[0]
            title = article.get('title', 'Untitled')
            # Shorten title if too long
            if len(title) > 60:
                title = title[:60] + "..."
            
            message += f"📄 *{title}*\n"
            message += f"🏷️ {article.get('category', 'General').replace('-', ' ').title()}\n"
            message += f"📊 {article.get('word_count', 'N/A')} 字\n"
            
            if article.get('keywords'):
                keywords = article['keywords'][:2]  # Only show first 2
                message += f"🔍 {', '.join(keywords)}\n"
        else:
            message += f"📚 *批量发布 {article_count} 篇文章*\n\n"
            for i, article in enumerate(articles[:3], 1):  # Show only first 3
                title = article.get('title', 'Untitled')
                if len(title) > 45:
                    title = title[:45] + "..."
                message += f"{i}. {title}\n"
            
            if len(articles) > 3:
                message += f"➕ 还有 {len(articles) - 3} 篇文章\n"
        
        if site_url:
            message += f"\n🌐 [查看网站]({site_url})"
        
        message += f"\n\n_🤖 自动化内容生成_"
        
        return self.send_message(message)
    
    def send_build_notification(self, status, site_url=None, commit_hash=None, commit_message=None, duration=None, force=False):
        """Send build/deployment notification with smart filtering"""
        
        # Determine notification level
        level = 'ERROR' if status.lower() == 'failure' else 'SUCCESS'
        
        # Check if we should send this notification
        if not self._should_send_notification(level, force):
            if status.lower() != 'failure':  # Always log failures
                print(f"⏰ Skipping build notification - quiet hours or filtered")
                return False
        
        status_emoji = {
            'success': '✅',
            'failure': '❌', 
            'cancelled': '⚠️',
            'in_progress': '🔄'
        }.get(status.lower(), '📋')
        
        # Simplified Chinese messages
        status_text_cn = {
            'success': '构建成功',
            'failure': '构建失败', 
            'cancelled': '构建取消',
            'in_progress': '正在构建'
        }.get(status.lower(), f'构建{status}')
        
        china_time = datetime.now(self.china_tz).strftime('%m-%d %H:%M')
        message = f"{status_emoji} *{status_text_cn}* | {china_time}\n\n"
        
        # Only show essential information
        if status.lower() == 'failure':
            message += f"🚨 *需要注意*\n"
            if commit_message:
                short_msg = commit_message[:50] + "..." if len(commit_message) > 50 else commit_message
                message += f"📝 {short_msg}\n"
        else:
            # For successful builds, be more concise
            if commit_message and 'Auto:' in commit_message:
                message += f"📝 自动更新\n"
            elif commit_message:
                short_msg = commit_message[:40] + "..." if len(commit_message) > 40 else commit_message
                message += f"📝 {short_msg}\n"
        
        if duration:
            message += f"⏱️ {duration}\n"
        
        if commit_hash:
            short_hash = commit_hash[:7]
            message += f"🔗 `{short_hash}`\n"
        
        if site_url and status.lower() == 'success':
            message += f"\n🌐 [查看网站]({site_url})"
        
        message += f"\n\n_🤖 GitHub Actions_"
        
        return self.send_message(message)
    
    def send_performance_alert(self, metrics, thresholds=None):
        """Send performance alert based on metrics"""
        thresholds = thresholds or {
            'response_time': 3.0,  # seconds
            'error_rate': 0.05,    # 5%
            'uptime': 0.95         # 95%
        }
        
        alerts = []
        
        # Check response time
        if metrics.get('response_time', 0) > thresholds['response_time']:
            alerts.append(f"⚠️ High response time: {metrics['response_time']:.2f}s (threshold: {thresholds['response_time']:.1f}s)")
        
        # Check error rate
        if metrics.get('error_rate', 0) > thresholds['error_rate']:
            alerts.append(f"⚠️ High error rate: {metrics['error_rate']:.2%} (threshold: {thresholds['error_rate']:.1%})")
        
        # Check uptime
        if metrics.get('uptime', 1) < thresholds['uptime']:
            alerts.append(f"⚠️ Low uptime: {metrics['uptime']:.2%} (threshold: {thresholds['uptime']:.1%})")
        
        if not alerts:
            return  # No alerts needed
        
        message = "🚨 *AI Smart Home Hub - Performance Alert*\n\n"
        message += "\n".join(alerts)
        message += f"\n\n*Checked:* {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}"
        message += "\n_🤖 Automated monitoring_"
        
        return self.send_message(message)
    
    def send_revenue_update(self, revenue_data):
        """Send revenue update notification"""
        message = "💰 *AI Smart Home Hub - Revenue Update*\n\n"
        
        if revenue_data.get('daily_revenue'):
            message += f"*Today:* ${revenue_data['daily_revenue']:.2f}\n"
        
        if revenue_data.get('monthly_revenue'):
            message += f"*This Month:* ${revenue_data['monthly_revenue']:.2f}\n"
        
        if revenue_data.get('adsense_earnings'):
            message += f"*AdSense:* ${revenue_data['adsense_earnings']:.2f}\n"
        
        if revenue_data.get('affiliate_earnings'):
            message += f"*Affiliate:* ${revenue_data['affiliate_earnings']:.2f}\n"
        
        if revenue_data.get('traffic_stats'):
            stats = revenue_data['traffic_stats']
            message += f"\n*Traffic Today:*\n"
            message += f"• Visitors: {stats.get('visitors', 'N/A')}\n"
            message += f"• Page Views: {stats.get('page_views', 'N/A')}\n"
            message += f"• Bounce Rate: {stats.get('bounce_rate', 'N/A')}\n"
        
        message += f"\n*Updated:* {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}"
        message += "\n_📊 Automated revenue tracking_"
        
        return self.send_message(message)
    
    def send_error_alert(self, error_type, error_message, context=None, force=True):
        """Send error alert notification - always sent regardless of time"""
        # Errors are always sent (force=True by default)
        if not self._should_send_notification('ERROR', force):
            return False
        
        china_time = datetime.now(self.china_tz).strftime('%m-%d %H:%M')
        message = f"🚨 *系统错误* | {china_time}\n\n"
        
        message += f"🔸 *类型:* {error_type}\n"
        
        # Show abbreviated error message
        short_error = error_message[:150] + "..." if len(error_message) > 150 else error_message
        message += f"🔸 *错误:* `{short_error}`\n"
        
        if context:
            message += f"🔸 *环境:* {context}\n"
        
        message += f"\n⚠️ *需要人工检查*"
        message += f"\n\n_🤖 自动错误监控_"
        
        return self.send_message(message)
    
    def send_keyword_trends_update(self, trending_keywords):
        """Send trending keywords update"""
        if not trending_keywords:
            return
        
        message = "📈 *AI Smart Home Hub - Trending Keywords Update*\n\n"
        
        for i, trend in enumerate(trending_keywords[:5], 1):
            keyword = trend.get('keyword', 'N/A')
            score = trend.get('trend_score', 0)
            category = trend.get('category', 'N/A')
            
            # Add trend direction indicator
            if score > 0.8:
                trend_icon = "🔥"
            elif score > 0.6:
                trend_icon = "📈"
            else:
                trend_icon = "📊"
            
            message += f"{trend_icon} *{keyword}*\n"
            message += f"   Category: {category.replace('_', ' ').title()}\n"
            message += f"   Score: {score:.2f}\n\n"
        
        message += f"*Updated:* {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}\n"
        message += "_🔍 Automated keyword research_"
        
        return self.send_message(message)


def load_article_data(filepath):
    """Load article data from markdown file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse front matter
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                front_matter = parts[1]
                article_content = parts[2]
                
                # Basic parsing of YAML front matter
                data = {}
                for line in front_matter.strip().split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        key = key.strip()
                        value = value.strip().strip('"\'')
                        
                        # Handle arrays
                        if value.startswith('[') and value.endswith(']'):
                            value = [item.strip().strip('"\'') for item in value[1:-1].split(',')]
                        
                        data[key] = value
                
                # Add word count
                data['word_count'] = len(article_content.split())
                
                return data
    except Exception as e:
        print(f"Error loading article data from {filepath}: {e}")
    
    return {}


def main():
    parser = argparse.ArgumentParser(description='Send Telegram notifications')
    parser.add_argument('--type', choices=['article', 'build', 'performance', 'revenue', 'error', 'keywords'], 
                       required=True, help='Type of notification')
    
    # Article notification args
    parser.add_argument('--articles', nargs='+', help='Article files to notify about')
    
    # Build notification args
    parser.add_argument('--status', help='Build status')
    parser.add_argument('--commit-hash', help='Commit hash')
    parser.add_argument('--commit-message', help='Commit message')
    parser.add_argument('--duration', help='Build duration')
    
    # General args
    parser.add_argument('--site-url', help='Site URL')
    parser.add_argument('--message', help='Custom message')
    
    # Error args
    parser.add_argument('--error-type', help='Error type')
    parser.add_argument('--error-message', help='Error message')
    parser.add_argument('--context', help='Error context')
    
    args = parser.parse_args()
    
    try:
        notifier = TelegramNotifier()
        
        if args.type == 'article':
            if args.articles:
                articles_data = []
                for article_path in args.articles:
                    if os.path.exists(article_path):
                        data = load_article_data(article_path)
                        if data:
                            articles_data.append(data)
                
                notifier.send_article_notification(articles_data, args.site_url)
            else:
                print("No article files provided")
                
        elif args.type == 'build':
            notifier.send_build_notification(
                status=args.status or 'unknown',
                site_url=args.site_url,
                commit_hash=args.commit_hash,
                commit_message=args.commit_message,
                duration=args.duration
            )
            
        elif args.type == 'error':
            notifier.send_error_alert(
                error_type=args.error_type or 'Unknown',
                error_message=args.error_message or 'No details provided',
                context=args.context
            )
            
        elif args.type == 'keywords':
            # Load trending keywords from cache
            cache_file = Path("data/trending_keywords_cache.json")
            if cache_file.exists():
                with open(cache_file, 'r', encoding='utf-8') as f:
                    trends = json.load(f)
                notifier.send_keyword_trends_update(trends)
            else:
                print("No trending keywords cache found")
                
        else:
            print(f"Notification type '{args.type}' not implemented")
            sys.exit(1)
    
    except ValueError as e:
        print(f"Configuration error: {e}")
        print("Make sure TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID environment variables are set")
        sys.exit(1)
    
    except Exception as e:
        print(f"Error sending notification: {e}")
        sys.exit(1)
    
    print("✅ Notification sent successfully")


if __name__ == "__main__":
    main()