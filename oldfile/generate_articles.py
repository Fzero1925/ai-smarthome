#!/usr/bin/env python3
"""
Article Generation Script for AI Smart Home Hub

This script generates high-quality, SEO-optimized articles about smart home devices
using the anti-AI detection content generator and trending keyword data.
"""

import os
import sys
import json
import argparse
from datetime import datetime, timedelta
from pathlib import Path

# Add modules to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.keyword_tools.keyword_analyzer import SmartHomeKeywordAnalyzer
from modules.content_generator.anti_ai_content_generator import AntiAIContentGenerator


def load_trending_keywords(max_age_hours=24):
    """Load trending keywords from cache or generate fresh ones"""
    cache_file = Path("data/trending_keywords_cache.json")
    
    # Check if cache exists and is fresh
    if cache_file.exists():
        cache_age = datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime)
        if cache_age < timedelta(hours=max_age_hours):
            print(f"📊 Loading cached trending keywords (age: {cache_age})")
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
    
    # Generate fresh trending keywords
    print("🔍 Analyzing trending keywords...")
    analyzer = SmartHomeKeywordAnalyzer()
    
    try:
        trends = analyzer.analyze_trending_topics()
        
        # Cache the results
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(trends, f, indent=2, default=str)
        
        return trends
    
    except Exception as e:
        print(f"⚠️ Error fetching trends: {e}")
        # Return fallback trending topics
        return [
            {'keyword': 'smart plug alexa', 'category': 'smart_plugs', 'trend_score': 0.8},
            {'keyword': 'robot vacuum pet hair', 'category': 'robot_vacuums', 'trend_score': 0.9},
            {'keyword': 'outdoor security camera', 'category': 'security_cameras', 'trend_score': 0.7},
            {'keyword': 'color changing smart bulbs', 'category': 'smart_bulbs', 'trend_score': 0.8},
            {'keyword': 'smart thermostat energy saving', 'category': 'smart_thermostats', 'trend_score': 0.6}
        ]


def check_existing_content(keyword, max_age_days=30):
    """Check if similar content already exists"""
    content_dir = Path("content/articles")
    if not content_dir.exists():
        return False
    
    # Create a normalized version of the keyword for comparison
    normalized_keyword = keyword.lower().replace(' ', '-').replace(',', '').replace(':', '')
    
    cutoff_date = datetime.now() - timedelta(days=max_age_days)
    
    for article_file in content_dir.glob("*.md"):
        # Check if filename contains similar keywords
        if any(word in article_file.stem for word in normalized_keyword.split('-')[:2]):
            # Check file age
            file_age = datetime.fromtimestamp(article_file.stat().st_mtime)
            if file_age > cutoff_date:
                print(f"📄 Similar content exists: {article_file.name} (created {file_age.strftime('%Y-%m-%d')})")
                return True
    
    return False


def generate_article(keyword, category, article_type="review", target_length=2500, force=False):
    """Generate a single article"""
    
    # Check for existing content unless forced
    if not force and check_existing_content(keyword):
        print(f"⏭️ Skipping '{keyword}' - similar content exists")
        return None
    
    print(f"📝 Generating article for: {keyword} ({category})")
    
    try:
        generator = AntiAIContentGenerator()
        article = generator.generate_smart_home_article(
            keyword=keyword,
            category=category,
            article_type=article_type,
            target_length=target_length
        )
        
        # Create safe filename
        safe_title = keyword.lower().replace(' ', '-').replace(',', '').replace(':', '').replace('/', '-')
        date_str = datetime.now().strftime("%Y%m%d")
        filename = f"{safe_title}-{date_str}.md"
        
        # Ensure content directory exists
        content_dir = Path("content/articles")
        content_dir.mkdir(parents=True, exist_ok=True)
        
        filepath = content_dir / filename
        
        # Generate comprehensive Hugo front matter
        metadata = article['metadata']
        
        front_matter = f"""---
title: "{article['title']}"
description: "{metadata.get('description', f'Complete guide and review of {keyword} devices. Compare features, prices, and find the best options for your smart home.')[:160]}"
date: {datetime.now().isoformat()}Z
lastmod: {datetime.now().isoformat()}Z
categories: {json.dumps(metadata.get('categories', [category.replace('_', '-')]))}
tags: {json.dumps(metadata.get('tags', [keyword.lower(), 'smart home', 'review']))}
keywords: {json.dumps([keyword] + metadata.get('tags', [])[:5])}
featured: true
weight: 1
rating: {4.0 + (hash(keyword) % 10) / 10:.1f}
price: "{10 + (hash(keyword) % 50)}"
author: "Smart Home Team"
image: "/images/smart-home-{category.replace('_', '-')}-hero.jpg"
toc: true
draft: false
sitemap:
  changefreq: 'weekly'
  priority: 0.8
seo:
  title: "{article['title']}"
  description: "{metadata.get('description', f'Complete guide to {keyword}')[:160]}"
  canonical: ""
  noindex: false
"""

        # Add FAQ if available
        if article.get('faq'):
            front_matter += f"""faq:
"""
            for faq_item in article['faq']:
                front_matter += f"""  - question: "{faq_item['question']}"
    answer: "{faq_item['answer']}"
"""

        # Add featured products if available
        if article.get('featured_products', {}).get('products'):
            front_matter += f"""featured_products:
"""
            for product in article['featured_products']['products'][:3]:  # Limit to top 3
                front_matter += f"""  - name: "{product['name']}"
    rating: {product['rating']}
    reviews: {product.get('reviews', 1000)}
    current_price: {product['current_price']}
    features: {json.dumps(product.get('features', []))}
    amazon_url: "{product.get('amazon_url', '#')}"
    badge: "{product.get('badge', 'Recommended')}"
"""
                if product.get('pros_cons'):
                    front_matter += f"""    pros_cons:
      pros: {json.dumps(product['pros_cons'].get('pros', []))}
      cons: {json.dumps(product['pros_cons'].get('cons', []))}
"""

        front_matter += "---\n\n"
        
        # Write the complete article
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(front_matter)
            f.write(article['content'])
        
        print(f"✅ Generated: {filepath}")
        print(f"   📊 Word count: {article['word_count']}")
        print(f"   🤖 Anti-AI score: {article['anti_ai_score']:.2f}")
        print(f"   🔍 SEO score: {metadata.get('seo_score', 0):.2f}")
        
        return filepath
        
    except Exception as e:
        print(f"❌ Error generating article for '{keyword}': {str(e)}")
        return None


def generate_batch(batch_size=3, force=False, specific_keywords=None):
    """Generate a batch of articles"""
    
    if specific_keywords:
        # Use provided keywords
        trends = [{'keyword': kw, 'category': 'smart_plugs'} for kw in specific_keywords]
    else:
        # Load trending keywords
        trends = load_trending_keywords()
    
    if not trends:
        print("❌ No trending keywords available")
        return []
    
    # Sort by trend score and select top candidates
    sorted_trends = sorted(trends, key=lambda x: x.get('trend_score', 0), reverse=True)
    selected_trends = sorted_trends[:batch_size * 2]  # Get more than needed as backup
    
    generated_files = []
    successful_generations = 0
    
    print(f"🎯 Target: {batch_size} articles")
    print(f"📝 Candidate keywords: {len(selected_trends)}")
    
    for i, trend in enumerate(selected_trends):
        if successful_generations >= batch_size:
            break
            
        keyword = trend.get('keyword', '')
        category = trend.get('category', 'smart_plugs')
        
        if not keyword:
            continue
            
        print(f"\n--- Article {successful_generations + 1}/{batch_size} ---")
        
        filepath = generate_article(
            keyword=keyword,
            category=category,
            force=force
        )
        
        if filepath:
            generated_files.append(str(filepath))
            successful_generations += 1
    
    print(f"\n🎉 Generation complete!")
    print(f"✅ Successfully generated: {successful_generations} articles")
    print(f"📁 Files created: {len(generated_files)}")
    
    return generated_files


def update_generation_stats(generated_count, total_requested):
    """Update generation statistics"""
    stats_file = Path("data/stats/generation_stats.json")
    stats_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Load existing stats
    if stats_file.exists():
        with open(stats_file, 'r', encoding='utf-8') as f:
            stats = json.load(f)
    else:
        stats = {
            'total_articles_generated': 0,
            'total_runs': 0,
            'successful_runs': 0,
            'average_success_rate': 0,
            'last_generation': None,
            'generation_history': []
        }
    
    # Update stats
    stats['total_articles_generated'] += generated_count
    stats['total_runs'] += 1
    
    if generated_count > 0:
        stats['successful_runs'] += 1
    
    stats['average_success_rate'] = stats['successful_runs'] / stats['total_runs']
    stats['last_generation'] = datetime.now().isoformat()
    
    # Add to history (keep last 20 entries)
    stats['generation_history'].insert(0, {
        'date': datetime.now().isoformat(),
        'requested': total_requested,
        'generated': generated_count,
        'success_rate': generated_count / total_requested if total_requested > 0 else 0
    })
    stats['generation_history'] = stats['generation_history'][:20]
    
    # Save updated stats
    with open(stats_file, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2)
    
    print(f"📊 Updated generation stats: {stats['total_articles_generated']} total articles")


def main():
    parser = argparse.ArgumentParser(description='Generate smart home articles')
    parser.add_argument('--batch-size', type=int, default=1, help='Number of articles to generate')
    parser.add_argument('--force', action='store_true', help='Generate even if similar content exists')
    parser.add_argument('--keywords', nargs='+', help='Specific keywords to generate content for')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be generated without creating files')
    parser.add_argument('--list-trends', action='store_true', help='List current trending keywords')
    
    args = parser.parse_args()
    
    if args.list_trends:
        print("📊 Current trending keywords:")
        trends = load_trending_keywords()
        for i, trend in enumerate(sorted(trends, key=lambda x: x.get('trend_score', 0), reverse=True)[:10], 1):
            score = trend.get('trend_score', 0)
            keyword = trend.get('keyword', 'N/A')
            category = trend.get('category', 'N/A')
            print(f"{i:2d}. {keyword} ({category}) - Score: {score:.2f}")
        return
    
    if args.dry_run:
        print("🔍 DRY RUN - No files will be created")
        trends = load_trending_keywords()
        selected = sorted(trends, key=lambda x: x.get('trend_score', 0), reverse=True)[:args.batch_size]
        
        print(f"Would generate {len(selected)} articles:")
        for i, trend in enumerate(selected, 1):
            keyword = trend.get('keyword', 'N/A')
            category = trend.get('category', 'N/A')
            exists = check_existing_content(keyword)
            status = "SKIP (exists)" if exists and not args.force else "GENERATE"
            print(f"{i}. {keyword} ({category}) - {status}")
        return
    
    # Generate articles
    generated_files = generate_batch(
        batch_size=args.batch_size,
        force=args.force,
        specific_keywords=args.keywords
    )
    
    # Update statistics
    update_generation_stats(len(generated_files), args.batch_size)
    
    # Output results for GitHub Actions
    if generated_files:
        print(f"\n📋 Generated files:")
        for filepath in generated_files:
            print(f"  - {filepath}")
    
    # Exit with appropriate code
    if len(generated_files) == args.batch_size:
        print("✅ All requested articles generated successfully")
        sys.exit(0)
    elif len(generated_files) > 0:
        print(f"⚠️ Partial success: {len(generated_files)}/{args.batch_size} articles generated")
        sys.exit(0)  # Still considered success if at least one article was generated
    else:
        print("❌ No articles were generated")
        sys.exit(1)


if __name__ == "__main__":
    main()