#!/usr/bin/env python3
"""
Content Refresh and Rewriter for AI Smart Home Hub

This script periodically refreshes old content to maintain SEO relevance
and improve search engine rankings for aging articles.

Features:
- Identifies articles older than specified threshold
- Adds fresh content snippets and updates
- Updates publication dates while preserving original content
- Tracks refresh history and prevents over-refreshing
- Smart content variation to avoid duplicate content penalties

Usage:
    python scripts/content/refresh_content.py --days-old 30
    python scripts/content/refresh_content.py --force --target-articles 5
"""

import os
import glob
import random
import argparse
from datetime import datetime, timedelta
from pathlib import Path
import json
import re

# Fresh content snippets for different contexts
REFRESH_SNIPPETS = {
    "smart_plugs": [
        "🔌 **Latest Update**: Smart plug technology continues to evolve with improved energy monitoring and faster WiFi connectivity in 2024 models.",
        "📊 **Market Trends**: Recent data shows smart plugs remain the most popular entry point for home automation, with over 40% adoption rate.",
        "💡 **New Features**: Modern smart plugs now offer advanced scheduling, usage analytics, and better integration with voice assistants.",
        "⚡ **Energy Savings**: Updated studies confirm smart plugs can reduce standby power consumption by up to 23% when used correctly.",
        "🏠 **Integration**: Latest smart plugs work seamlessly with major platforms including Alexa, Google Home, and Apple HomeKit."
    ],
    
    "smart_bulbs": [
        "💡 **Technology Update**: LED smart bulbs now offer improved color accuracy with CRI ratings above 90 in premium models.",
        "🌈 **Color Range**: 2024 models support over 16 million colors with smooth transitions and circadian rhythm features.",
        "📱 **App Improvements**: Manufacturer apps now provide better scheduling, scene management, and energy usage tracking.",
        "🔋 **Efficiency**: Latest smart bulbs consume 75% less energy than traditional incandescent while lasting 15+ years.",
        "🎵 **Music Sync**: New models can sync with music and provide immersive lighting experiences for entertainment."
    ],
    
    "security_cameras": [
        "📹 **Video Quality**: 2024 security cameras offer 4K recording with improved night vision and AI-powered motion detection.",
        "☁️ **Cloud Storage**: Major brands now provide more generous free cloud storage plans with enhanced security features.",
        "🔒 **Privacy**: Enhanced encryption and local storage options address growing privacy concerns among consumers.",
        "📱 **Mobile Alerts**: Real-time notifications with smart filtering reduce false alarms by up to 80% compared to older models.",
        "🏠 **Integration**: Modern cameras integrate better with smart doorbells, locks, and home security systems."
    ],
    
    "robot_vacuums": [
        "🤖 **AI Advancement**: 2024 robot vacuums feature improved mapping, object recognition, and smarter cleaning patterns.",
        "🧹 **Suction Power**: Latest models offer 30% more suction power while maintaining quiet operation under 60dB.",
        "🗺️ **Smart Mapping**: Advanced LIDAR and camera systems create more accurate floor plans with room-specific cleaning.",
        "🔋 **Battery Life**: Extended battery life now supports up to 180 minutes of continuous cleaning on a single charge.",
        "📱 **App Control**: Enhanced mobile apps provide detailed cleaning reports, maintenance alerts, and scheduling options."
    ],
    
    "smart_speakers": [
        "🔊 **Audio Quality**: Premium smart speakers now feature improved drivers and spatial audio for richer sound.",
        "🗣️ **Voice Recognition**: Advanced AI provides better voice recognition even in noisy environments.",
        "🏠 **Hub Function**: Latest speakers serve as comprehensive smart home hubs with Zigbee and Thread support.",
        "🎵 **Music Services**: Expanded compatibility with streaming services and high-resolution audio formats.",
        "🔒 **Privacy**: Enhanced privacy controls allow users to delete voice recordings and limit data collection."
    ],
    
    "general": [
        "📈 **Market Growth**: The smart home market continues expanding with 25% year-over-year growth in device adoption.",
        "🔧 **Installation**: Modern smart home devices feature simplified setup processes, often completing in under 5 minutes.",
        "💰 **Cost Savings**: Smart home automation can reduce energy bills by 10-20% through intelligent scheduling and monitoring.",
        "🎯 **User Experience**: Improved user interfaces and voice control make smart homes more accessible to all age groups.",
        "🔄 **Interoperability**: Matter/Thread standards are improving device compatibility across different brands and platforms."
    ]
}

# Update markers to avoid duplicate refreshes
UPDATE_MARKERS = [
    "📅 **Content Updated**:",
    "🔄 **Last Refreshed**:", 
    "⏰ **Updated Information**:",
    "📊 **Latest Data**:"
]

def extract_frontmatter_and_content(file_content):
    """Extract YAML frontmatter and content from markdown file"""
    if not file_content.startswith('---'):
        return {}, file_content
    
    try:
        parts = file_content.split('---', 2)
        if len(parts) < 3:
            return {}, file_content
        
        frontmatter_text = parts[1].strip()
        content = parts[2].strip()
        
        metadata = {}
        for line in frontmatter_text.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                
                # Handle array fields
                if value.startswith('[') and value.endswith(']'):
                    value = [item.strip().strip('"').strip("'") 
                            for item in value[1:-1].split(',') if item.strip()]
                
                metadata[key] = value
        
        return metadata, content
        
    except Exception as e:
        print(f"⚠️ Error parsing frontmatter: {e}")
        return {}, file_content

def detect_article_category(metadata, content):
    """Detect article category for appropriate refresh snippets"""
    categories = metadata.get('categories', [])
    tags = metadata.get('tags', [])
    title = metadata.get('title', '').lower()
    content_lower = content.lower()
    
    # Combine all text for analysis
    all_text = f"{title} {' '.join(categories) if isinstance(categories, list) else categories} {' '.join(tags) if isinstance(tags, list) else tags} {content_lower}"
    
    # Category detection
    if any(term in all_text for term in ['smart plug', 'outlet', 'switch']):
        return 'smart_plugs'
    elif any(term in all_text for term in ['smart bulb', 'led', 'lighting', 'lamp']):
        return 'smart_bulbs'
    elif any(term in all_text for term in ['security camera', 'doorbell', 'surveillance']):
        return 'security_cameras'
    elif any(term in all_text for term in ['robot vacuum', 'roomba', 'cleaning robot']):
        return 'robot_vacuums'
    elif any(term in all_text for term in ['smart speaker', 'alexa', 'google home', 'echo']):
        return 'smart_speakers'
    else:
        return 'general'

def get_old_articles(content_dir="content/articles", days_old=30):
    """Find articles older than specified days"""
    old_files = []
    cutoff_date = datetime.now() - timedelta(days=days_old)
    
    content_path = Path(content_dir)
    if not content_path.exists():
        return old_files
    
    for file_path in content_path.glob("**/*.md"):
        try:
            # Check file modification time
            mod_time = datetime.fromtimestamp(file_path.stat().st_mtime)
            if mod_time < cutoff_date:
                old_files.append(str(file_path))
        except Exception as e:
            print(f"⚠️ Error checking {file_path}: {e}")
            continue
    
    return old_files

def has_been_refreshed_recently(content, days=7):
    """Check if article has been refreshed recently"""
    for marker in UPDATE_MARKERS:
        if marker in content:
            # Try to extract date from refresh marker
            date_pattern = r'(\d{4}-\d{2}-\d{2})'
            matches = re.findall(date_pattern, content)
            if matches:
                try:
                    last_refresh = datetime.strptime(matches[-1], '%Y-%m-%d')
                    if datetime.now() - last_refresh < timedelta(days=days):
                        return True
                except:
                    pass
    return False

def refresh_article_content(file_path, force=False):
    """Refresh content of a single article"""
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        metadata, content = extract_frontmatter_and_content(original_content)
        
        # Skip if recently refreshed (unless forced)
        if not force and has_been_refreshed_recently(content):
            print(f"⏭️ Recently refreshed: {Path(file_path).name}")
            return False
        
        # Detect category for appropriate snippets
        category = detect_article_category(metadata, content)
        
        # Select refresh snippet
        available_snippets = REFRESH_SNIPPETS.get(category, REFRESH_SNIPPETS['general'])
        refresh_snippet = random.choice(available_snippets)
        
        # Create refresh section
        today = datetime.now().strftime('%Y-%m-%d')
        refresh_marker = random.choice(UPDATE_MARKERS)
        
        refresh_section = f"\n\n---\n\n{refresh_marker} {today}\n\n{refresh_snippet}\n"
        
        # Remove old refresh sections to avoid accumulation
        for marker in UPDATE_MARKERS:
            pattern = rf"\n\n---\s*\n\n{re.escape(marker)}[^\n]*\n\n[^\n]*\n"
            content = re.sub(pattern, "", content, flags=re.MULTILINE)
        
        # Add new refresh section
        updated_content = content.strip() + refresh_section
        
        # Update lastmod in frontmatter if it exists
        if 'lastmod' in metadata:
            metadata['lastmod'] = datetime.now().isoformat() + 'Z'
        
        # Reconstruct full content with frontmatter
        if metadata:
            frontmatter_text = "---\n"
            for key, value in metadata.items():
                if isinstance(value, list):
                    frontmatter_text += f"{key}: {value}\n"
                else:
                    frontmatter_text += f'{key}: "{value}"\n'
            frontmatter_text += "---\n\n"
            
            final_content = frontmatter_text + updated_content
        else:
            final_content = updated_content
        
        # Write updated content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(final_content)
        
        print(f"🔄 Refreshed: {Path(file_path).name} ({category} category)")
        return True
        
    except Exception as e:
        print(f"❌ Error refreshing {file_path}: {e}")
        return False

def update_refresh_stats(refreshed_count, total_candidates):
    """Update refresh statistics"""
    stats_file = Path("data/stats/content_refresh_stats.json")
    stats_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Load existing stats
    if stats_file.exists():
        try:
            with open(stats_file, 'r', encoding='utf-8') as f:
                stats = json.load(f)
        except:
            stats = {}
    else:
        stats = {
            'total_refreshes': 0,
            'total_runs': 0,
            'last_refresh': None,
            'refresh_history': []
        }
    
    # Update stats
    stats['total_refreshes'] += refreshed_count
    stats['total_runs'] += 1
    stats['last_refresh'] = datetime.now().isoformat()
    
    # Add to history
    stats['refresh_history'].insert(0, {
        'date': datetime.now().isoformat(),
        'refreshed_articles': refreshed_count,
        'candidate_articles': total_candidates
    })
    
    # Keep only last 20 entries
    stats['refresh_history'] = stats['refresh_history'][:20]
    
    # Save updated stats
    with open(stats_file, 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    
    print(f"📊 Updated refresh stats: {stats['total_refreshes']} total refreshes")

def main():
    parser = argparse.ArgumentParser(description='Refresh old content for SEO')
    parser.add_argument('--days-old', type=int, default=30, 
                       help='Consider articles older than X days (default: 30)')
    parser.add_argument('--max-articles', type=int, default=10,
                       help='Maximum articles to refresh in one run (default: 10)')
    parser.add_argument('--force', action='store_true',
                       help='Force refresh even if recently updated')
    parser.add_argument('--content-dir', default='content/articles',
                       help='Content directory path (default: content/articles)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be refreshed without making changes')
    
    args = parser.parse_args()
    
    print("🔄 Content Refresh Tool")
    print("=" * 50)
    
    # Find old articles
    old_articles = get_old_articles(args.content_dir, args.days_old)
    
    if not old_articles:
        print(f"✅ No articles older than {args.days_old} days found")
        return
    
    print(f"📄 Found {len(old_articles)} articles older than {args.days_old} days")
    
    # Limit articles to refresh
    articles_to_refresh = old_articles[:args.max_articles]
    
    if args.dry_run:
        print("\n🔍 DRY RUN - Articles that would be refreshed:")
        for article in articles_to_refresh:
            print(f"  - {Path(article).name}")
        return
    
    # Refresh articles
    refreshed_count = 0
    
    for article_path in articles_to_refresh:
        if refresh_article_content(article_path, force=args.force):
            refreshed_count += 1
    
    # Update statistics
    update_refresh_stats(refreshed_count, len(old_articles))
    
    print(f"\n🎉 Content refresh completed!")
    print(f"   📄 Processed: {len(articles_to_refresh)} articles")
    print(f"   ✅ Refreshed: {refreshed_count} articles")
    print(f"   ⏭️ Skipped: {len(articles_to_refresh) - refreshed_count} articles")
    
    if refreshed_count > 0:
        print(f"\n💡 Next steps:")
        print(f"   1. Review refreshed articles for quality")
        print(f"   2. Run SEO optimization: python scripts/seo/optimize_internal_links.py")
        print(f"   3. Update search index: python scripts/seo/build_search_index.py")
        print(f"   4. Submit to Google: python scripts/seo/submit_to_google.py")

if __name__ == "__main__":
    main()