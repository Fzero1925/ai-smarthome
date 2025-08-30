# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is AI Smart Home Hub - a fully automated smart home product review website built with Hugo and Python. The site generates revenue through Google AdSense and Amazon affiliate marketing while creating high-quality, SEO-optimized content automatically.

## Common Development Commands

### Local Development
```bash
# Start Hugo development server
hugo server -D

# Build for production
hugo --minify

# Generate new articles (manual)
python scripts/generate_articles.py --batch-size=3

# Update keyword trends
python modules/keyword_tools/keyword_analyzer.py --update-trends
```

### Content Management
```bash
# Generate articles for specific keywords
python scripts/generate_articles.py --keywords "smart plug alexa" "robot vacuum"

# Check existing content before generation
python scripts/generate_articles.py --dry-run --batch-size=5

# Force generation even if similar content exists
python scripts/generate_articles.py --force --batch-size=2
```

### Testing and Quality Assurance
```bash
# Check content quality scores
python modules/content_generator/anti_ai_content_generator.py

# Validate Hugo configuration
hugo config

# Test Telegram notifications
python scripts/notify_telegram.py --type build --status success --site-url http://localhost:1313
```

### Maintenance Tasks
```bash
# Clean old cached data
find data/keyword_cache -name "*.json" -mtime +7 -delete

# Update Python dependencies
pip install -r requirements.txt --upgrade

# Check for broken internal links
hugo --printUnusedTemplates
```

## Architecture and Key Components

### Content Generation Pipeline
The site uses a sophisticated multi-stage content generation system:

1. **Keyword Research** (`modules/keyword_tools/keyword_analyzer.py`)
   - Integrates with Google Trends via Pytrends
   - Analyzes keyword competition, search volume, and commercial intent
   - Caches results for 24 hours to avoid API limits
   - Generates topic suggestions and related queries

2. **Anti-AI Content Generator** (`modules/content_generator/anti_ai_content_generator.py`)
   - Creates human-like content that passes AI detection tools
   - Uses sophisticated text variation algorithms
   - Implements multiple writing patterns and styles
   - Generates 1500-4000 word articles with 65+ readability scores

3. **Product Database Integration**
   - Maintains realistic product recommendations with pricing
   - Includes detailed feature comparisons and pros/cons
   - Supports Amazon, eBay, and direct manufacturer links
   - Tracks price changes and discount information

### Hugo Theme Structure
The custom theme is optimized for monetization and SEO:

- **Responsive Design**: Mobile-first approach with progressive enhancement
- **Ad Integration**: Strategic ad placement with rotation between networks
- **Affiliate Links**: Automatic Amazon affiliate tag insertion
- **SEO Optimization**: Structured data, meta tags, sitemap generation
- **Performance**: Lazy loading, image optimization, minified assets

### Automation System
The site runs entirely automated through GitHub Actions:

1. **Daily Content Generation** (`.github/workflows/daily-content.yml`)
   - Runs at 3:00 AM UTC daily
   - Analyzes trending keywords automatically
   - Generates 1-3 new articles based on trends
   - Commits and pushes new content

2. **Deployment Pipeline** (`.github/workflows/deploy.yml`)
   - Triggers on every push to main branch
   - Builds Hugo site with optimizations
   - Deploys to GitHub Pages
   - Sends notifications via Telegram

### Revenue Optimization Features
- **Multi-Network Ad Rotation**: AdSense, Media.net, PropellerAds
- **Smart Affiliate Integration**: Context-aware product recommendations
- **Conversion Tracking**: UTM parameters and analytics integration
- **A/B Testing Ready**: Template variations for optimization

## Development Workflow

### Adding New Product Categories
1. Update `smart_home_categories` in `modules/keyword_tools/keyword_analyzer.py`
2. Add product data to `modules/content_generator/anti_ai_content_generator.py`
3. Create category-specific templates in `data/templates/`
4. Test content generation with `--dry-run` flag

### Content Quality Guidelines
- Target word count: 2500-3500 words for product reviews
- Anti-AI detection score: Minimum 0.7 (target 0.8+)
- SEO optimization score: Minimum 0.8
- Readability: Flesch Reading Ease score of 65+
- Include FAQ, pros/cons, and detailed product comparisons

### Deployment Checklist
Before major deployments:
1. Test Hugo build locally with `hugo --minify`
2. Validate all markdown front matter
3. Check that all required environment variables are set
4. Verify GitHub Actions secrets are configured
5. Test Telegram notifications

## Environment Configuration

### Required Environment Variables (GitHub Secrets)
```bash
GOOGLE_ADSENSE_ID=ca-pub-XXXXXXXXXXXXXXXX
AMAZON_AFFILIATE_TAG=yourtag-20
GOOGLE_ANALYTICS_ID=G-XXXXXXXXXX
TELEGRAM_BOT_TOKEN=your_bot_token  # Optional
TELEGRAM_CHAT_ID=your_chat_id      # Optional
```

### Local Development Setup
```bash
# Clone and setup
git clone <repository>
cd ai-smarthome
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt

# Create .env file for local testing
echo "GOOGLE_ADSENSE_ID=ca-pub-test" > .env
echo "AMAZON_AFFILIATE_TAG=test-20" >> .env
```

## File Organization

### Critical Files and Directories
- `config.toml` - Hugo configuration with multi-language support
- `content/articles/` - Main English article content
- `content-zh/` - Chinese content (for expansion)
- `layouts/` - Hugo theme templates with ad integration
- `modules/` - Reusable Python components
- `scripts/` - Automation and maintenance scripts
- `data/` - Structured data and caches
- `dev-docs/` - Chinese development documentation (not deployed)

### Key Templates
- `layouts/index.html` - Homepage with hero section and category grid
- `layouts/_default/single.html` - Article template with ad slots
- `layouts/partials/adsense.html` - Ad network rotation logic
- `layouts/partials/affiliate.html` - Product recommendation cards

## Content Strategy

### Target Keywords and Categories
The site focuses on high-commercial-intent keywords in these categories:
- Smart Plugs and Outlets
- Smart Lighting and Bulbs  
- Security Cameras and Doorbells
- Robot Vacuums and Cleaners
- Smart Thermostats and Climate Control
- Voice Assistants and Smart Speakers

### SEO Best Practices Implemented
- Semantic HTML structure with proper heading hierarchy
- Internal linking between related articles
- Image optimization with alt text and lazy loading
- Schema.org structured data for reviews
- Fast loading times (target <2 seconds)
- Mobile-first responsive design

## Monetization Strategy

### Primary Revenue Streams
1. **Google AdSense**: Display ads with strategic placement
2. **Amazon Associates**: Product affiliate commissions
3. **Direct Affiliate Programs**: Manufacturer partnerships

### Conversion Optimization
- Product comparison tables with affiliate links
- Prominent "Buy Now" buttons with tracking
- Price alerts and discount notifications
- User reviews and rating displays
- Trust signals (expert reviews, testing credentials)

## Troubleshooting Common Issues

### Hugo Build Failures
- Check for malformed front matter in markdown files
- Validate TOML syntax in config.toml
- Ensure all required shortcodes and partials exist
- Use `hugo --debug` for detailed error information

### Content Generation Problems
- Verify Pytrends isn't hitting rate limits (implement longer delays)
- Check internet connectivity for API calls
- Clear keyword cache if data seems stale
- Review anti-AI detection parameters if content quality is poor

### GitHub Actions Failures
- Check that all required secrets are set in repository settings
- Verify Python dependencies in requirements.txt are current
- Ensure Hugo version matches what's specified in workflows
- Review workflow logs for specific error messages

## Performance Monitoring

### Key Metrics to Track
- Page load speed (target <2 seconds)
- Core Web Vitals scores
- Ad viewability and click-through rates
- Affiliate conversion rates
- Search engine ranking positions
- Organic traffic growth

### Monitoring Tools Integration
- Google Analytics 4 for comprehensive traffic analysis
- Google Search Console for SEO performance
- PageSpeed Insights for performance optimization
- AdSense reporting for revenue tracking

## Future Enhancement Opportunities

### Content Expansion
- Video content integration (YouTube embeds)
- Interactive product comparison tools
- User-generated reviews and ratings
- Seasonal content campaigns

### Technical Improvements
- Progressive Web App features
- Advanced caching strategies
- Machine learning for personalized recommendations
- Real-time price tracking and alerts

This architecture supports rapid scaling to other product verticals by simply updating the keyword categories and product databases while reusing the entire content generation and monetization infrastructure.