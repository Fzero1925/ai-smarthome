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


class TelegramNotifier:
    """Handle Telegram notifications for the AI Smart Home Hub"""
    
    def __init__(self, bot_token=None, chat_id=None):
        self.bot_token = bot_token or os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = chat_id or os.getenv('TELEGRAM_CHAT_ID')
        
        if not self.bot_token or not self.chat_id:
            raise ValueError("Telegram bot token and chat ID are required")
        
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
    
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
    
    def send_article_notification(self, articles, site_url=None):
        """Send notification about new articles"""
        if not articles:
            return
        
        article_count = len(articles)
        emoji = "📝" if article_count == 1 else "📚"
        
        message = f"{emoji} *AI Smart Home Hub - New Content Published*\n\n"
        
        if article_count == 1:
            article = articles[0]
            message += f"*New Article:* {article.get('title', 'Untitled')}\n"
            message += f"*Category:* {article.get('category', 'General')}\n"
            message += f"*Word Count:* {article.get('word_count', 'N/A')} words\n"
            if article.get('keywords'):
                keywords = article['keywords'][:3]  # First 3 keywords
                message += f"*Keywords:* {', '.join(keywords)}\n"
        else:
            message += f"*Published {article_count} new articles:*\n"
            for i, article in enumerate(articles[:5], 1):  # Limit to first 5
                title = article.get('title', 'Untitled')[:50] + "..." if len(article.get('title', '')) > 50 else article.get('title', 'Untitled')
                message += f"{i}. {title}\n"
            
            if len(articles) > 5:
                message += f"... and {len(articles) - 5} more\n"
        
        message += f"\n*Published:* {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}\n"
        
        if site_url:
            message += f"*Website:* [Visit Site]({site_url})\n"
        
        message += "\n_🤖 Automated by AI Smart Home Hub_"
        
        return self.send_message(message)
    
    def send_build_notification(self, status, site_url=None, commit_hash=None, commit_message=None, duration=None):
        """Send build/deployment notification"""
        status_emoji = {
            'success': '✅',
            'failure': '❌',
            'cancelled': '⚠️',
            'in_progress': '🔄'
        }.get(status.lower(), '📋')
        
        status_text = {
            'success': 'Build Successful',
            'failure': 'Build Failed',
            'cancelled': 'Build Cancelled',
            'in_progress': 'Build In Progress'
        }.get(status.lower(), f'Build {status.title()}')
        
        message = f"{status_emoji} *AI Smart Home Hub - {status_text}*\n\n"
        
        message += f"*Status:* {status_text}\n"
        message += f"*Time:* {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}\n"
        
        if duration:
            message += f"*Duration:* {duration}\n"
        
        if commit_hash:
            short_hash = commit_hash[:8]
            message += f"*Commit:* `{short_hash}`\n"
        
        if commit_message:
            # Truncate long commit messages
            truncated_message = commit_message[:100] + "..." if len(commit_message) > 100 else commit_message
            message += f"*Changes:* {truncated_message}\n"
        
        if site_url and status.lower() == 'success':
            message += f"*Website:* [View Site]({site_url})\n"
        
        message += "\n_🤖 Automated by GitHub Actions_"
        
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
    
    def send_error_alert(self, error_type, error_message, context=None):
        """Send error alert notification"""
        message = f"🚨 *AI Smart Home Hub - Error Alert*\n\n"
        message += f"*Type:* {error_type}\n"
        message += f"*Error:* `{error_message[:200]}{'...' if len(error_message) > 200 else ''}`\n"
        
        if context:
            message += f"*Context:* {context}\n"
        
        message += f"*Time:* {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}\n"
        message += "\n_🤖 Automated error monitoring_"
        
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