#!/usr/bin/env python3
"""
AI Smart Home Hub Monitoring Dashboard

A Streamlit-based dashboard for monitoring content generation, SEO performance,
and site analytics for the AI Smart Home Hub.

Features:
- Content generation statistics
- Keyword coverage analysis  
- SEO optimization tracking
- Performance metrics visualization
- Content quality scoring

Usage:
    streamlit run scripts/monitoring/dashboard.py

Requirements:
    pip install streamlit plotly pandas
"""

import streamlit as st
import os
import json
import glob
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Page configuration
st.set_page_config(
    page_title="AI Smart Home Hub - Dashboard", 
    page_icon="🏠",
    layout="wide"
)

# Styling
st.markdown("""
<style>
.metric-card {
    background: white;
    padding: 1rem;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    margin: 0.5rem 0;
}

.status-success {
    color: #28a745;
}

.status-warning {
    color: #ffc107;
}

.status-error {
    color: #dc3545;
}
</style>
""", unsafe_allow_html=True)

def load_article_data(content_dir="content/articles"):
    """Load all articles with metadata"""
    articles = []
    content_path = Path(content_dir)
    
    if not content_path.exists():
        return articles
    
    for file_path in content_path.glob("**/*.md"):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Simple frontmatter parsing
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    frontmatter_text = parts[1].strip()
                    article_content = parts[2].strip()
                    
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
                    
                    articles.append({
                        'title': metadata.get('title', file_path.stem),
                        'file_path': str(file_path),
                        'slug': file_path.stem,
                        'date': metadata.get('date', ''),
                        'tags': metadata.get('tags', []),
                        'categories': metadata.get('categories', []),
                        'rating': metadata.get('rating', 0),
                        'featured': metadata.get('featured', False),
                        'word_count': len(article_content.split()),
                        'content_length': len(article_content),
                        'last_modified': datetime.fromtimestamp(file_path.stat().st_mtime)
                    })
        except Exception as e:
            st.error(f"Error loading {file_path}: {e}")
            continue
    
    return articles

def load_generation_stats():
    """Load content generation statistics"""
    stats_file = Path("data/stats/content_generation.json")
    
    if not stats_file.exists():
        return {
            'total_runs': 0,
            'successful_runs': 0, 
            'articles_generated': 0,
            'last_runs': []
        }
    
    try:
        with open(stats_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

def load_seo_stats():
    """Load SEO optimization statistics"""
    seo_file = Path("data/seo_optimization_report.json")
    
    if not seo_file.exists():
        return {}
    
    try:
        with open(seo_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

def main():
    # Header
    st.title("🏠 AI Smart Home Hub - Monitoring Dashboard")
    st.markdown("---")
    
    # Load data
    articles = load_article_data()
    generation_stats = load_generation_stats()
    seo_stats = load_seo_stats()
    
    if not articles:
        st.warning("No articles found. Make sure content/articles directory exists with markdown files.")
        return
    
    # Overview metrics
    st.header("📊 Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="📝 Total Articles",
            value=len(articles),
            delta=generation_stats.get('articles_generated', 0)
        )
    
    with col2:
        avg_words = sum(a['word_count'] for a in articles) / len(articles) if articles else 0
        st.metric(
            label="📊 Avg Word Count", 
            value=f"{avg_words:.0f}",
            delta=f"Target: 2500"
        )
    
    with col3:
        success_rate = 0
        if generation_stats.get('total_runs', 0) > 0:
            success_rate = (generation_stats.get('successful_runs', 0) / generation_stats.get('total_runs', 1)) * 100
        st.metric(
            label="✅ Generation Success Rate",
            value=f"{success_rate:.1f}%",
            delta=f"{generation_stats.get('successful_runs', 0)} successful"
        )
    
    with col4:
        featured_count = sum(1 for a in articles if a.get('featured'))
        st.metric(
            label="⭐ Featured Articles",
            value=featured_count,
            delta=f"{featured_count/len(articles)*100:.1f}%" if articles else "0%"
        )
    
    # Content analysis
    st.header("📈 Content Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Articles by category
        all_categories = []
        for article in articles:
            cats = article.get('categories', [])
            if isinstance(cats, list):
                all_categories.extend(cats)
            elif cats:
                all_categories.append(cats)
        
        if all_categories:
            category_counts = pd.Series(all_categories).value_counts()
            
            fig_categories = px.pie(
                values=category_counts.values,
                names=category_counts.index,
                title="Articles by Category"
            )
            st.plotly_chart(fig_categories, use_container_width=True)
    
    with col2:
        # Word count distribution
        if articles:
            word_counts = [a['word_count'] for a in articles]
            
            fig_words = px.histogram(
                x=word_counts,
                bins=20,
                title="Word Count Distribution",
                labels={'x': 'Word Count', 'y': 'Number of Articles'}
            )
            fig_words.add_vline(x=2500, line_dash="dash", line_color="red", 
                               annotation_text="Target: 2500 words")
            st.plotly_chart(fig_words, use_container_width=True)
    
    # SEO Performance
    st.header("🔍 SEO Performance")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        internal_links = seo_stats.get('total_internal_links', 0)
        st.metric(
            label="🔗 Internal Links Added",
            value=internal_links,
            delta=f"Across {seo_stats.get('processed_files', 0)} files"
        )
    
    with col2:
        related_articles = seo_stats.get('total_related_articles', 0)
        st.metric(
            label="📋 Related Article Sections",
            value=related_articles,
            delta="Boost engagement"
        )
    
    with col3:
        # Calculate SEO score based on multiple factors
        seo_score = 0
        if articles:
            # Word count score (articles with 2000+ words)
            good_length = sum(1 for a in articles if a['word_count'] >= 2000)
            seo_score += (good_length / len(articles)) * 30
            
            # Internal links score
            if internal_links > 0:
                seo_score += min(internal_links / len(articles) * 20, 20)
            
            # Category coverage
            categories = set()
            for a in articles:
                cats = a.get('categories', [])
                if isinstance(cats, list):
                    categories.update(cats)
            seo_score += min(len(categories) * 5, 25)
            
            # Featured articles boost
            seo_score += (featured_count / len(articles)) * 25
        
        st.metric(
            label="📊 SEO Score",
            value=f"{seo_score:.1f}/100",
            delta="🎯 Target: 80+"
        )
    
    # Recent activity
    st.header("⏰ Recent Activity")
    
    # Recent articles
    recent_articles = sorted(articles, key=lambda x: x['last_modified'], reverse=True)[:10]
    
    st.subheader("📄 Recently Modified Articles")
    for article in recent_articles:
        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
        
        with col1:
            st.write(f"**{article['title'][:60]}**")
        
        with col2:
            st.write(f"{article['word_count']} words")
        
        with col3:
            if isinstance(article.get('categories'), list):
                categories = ', '.join(article['categories'][:2])
            else:
                categories = str(article.get('categories', ''))[:20]
            st.write(categories)
        
        with col4:
            st.write(article['last_modified'].strftime("%m/%d %H:%M"))
    
    # Generation history
    if generation_stats.get('last_runs'):
        st.subheader("🤖 Generation History")
        
        runs_df = pd.DataFrame(generation_stats['last_runs'])
        if 'date' in runs_df.columns:
            runs_df['date'] = pd.to_datetime(runs_df['date'])
            runs_df = runs_df.sort_values('date', ascending=False)
            
            for _, run in runs_df.head(5).iterrows():
                status_icon = "✅" if run.get('status') == 'success' else "❌"
                generated = "Generated content" if run.get('generated_content') else "Skipped"
                date_str = run['date'].strftime("%Y-%m-%d %H:%M") if pd.notna(run['date']) else "Unknown"
                
                st.write(f"{status_icon} {date_str} - {generated} ({run.get('reason', 'No reason')})")
    
    # Data quality alerts
    st.header("⚠️ Quality Alerts")
    
    alerts = []
    
    # Check for short articles
    short_articles = [a for a in articles if a['word_count'] < 1500]
    if short_articles:
        alerts.append(f"📏 {len(short_articles)} articles under 1500 words")
    
    # Check for articles without categories
    no_category = [a for a in articles if not a.get('categories')]
    if no_category:
        alerts.append(f"📂 {len(no_category)} articles missing categories")
    
    # Check for old articles (not modified in 30 days)
    thirty_days_ago = datetime.now() - timedelta(days=30)
    old_articles = [a for a in articles if a['last_modified'] < thirty_days_ago]
    if old_articles:
        alerts.append(f"⏰ {len(old_articles)} articles not updated in 30+ days")
    
    if alerts:
        for alert in alerts:
            st.warning(alert)
    else:
        st.success("✅ All quality checks passed!")
    
    # System status
    st.header("⚙️ System Status")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("📁 File Structure")
        paths_to_check = [
            "content/articles",
            "data/stats", 
            "scripts/seo",
            "scripts/monitoring",
            "static"
        ]
        
        for path in paths_to_check:
            if Path(path).exists():
                st.success(f"✅ {path}")
            else:
                st.error(f"❌ {path}")
    
    with col2:
        st.subheader("🔧 Scripts Status")
        scripts = [
            "scripts/generate_articles.py",
            "scripts/seo/submit_to_google.py", 
            "scripts/seo/build_search_index.py",
            "scripts/seo/optimize_internal_links.py"
        ]
        
        for script in scripts:
            if Path(script).exists():
                st.success(f"✅ {Path(script).name}")
            else:
                st.error(f"❌ {Path(script).name}")
    
    with col3:
        st.subheader("📊 Data Files")
        data_files = [
            "data/stats/content_generation.json",
            "data/seo_optimization_report.json",
            "static/search_index.json"
        ]
        
        for data_file in data_files:
            path = Path(data_file)
            if path.exists():
                size_kb = path.stat().st_size / 1024
                st.success(f"✅ {path.name} ({size_kb:.1f} KB)")
            else:
                st.warning(f"⚠️ {path.name} (not found)")

if __name__ == "__main__":
    main()