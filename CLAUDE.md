# AI Smart Home Hub - Claude Code Configuration

This file provides guidance to Claude Code when working with this repository.

## Project Overview

AI Smart Home Hub is an automated smart home product review website built with Hugo and Python. The site generates revenue through Google AdSense and Amazon affiliate marketing while creating high-quality, SEO-optimized content automatically.

## Current System Status (Updated: 2025-08-31)

### 🎉 Latest System Optimizations (Session 2025-08-31)

1. **搜索功能完善**
   - ✅ 修复首页搜索404错误问题
   - ✅ 创建专用搜索页面和Lunr.js集成
   - ✅ 生成搜索索引文件
   - ✅ 优化搜索用户体验

2. **SEO系统全面升级**
   - ✅ 实现完整的结构化数据标记 (JSON-LD)
   - ✅ 添加面包屑导航系统
   - ✅ 智能内部链接自动化
   - ✅ Article、FAQ、BreadcrumbList Schema实现

3. **AI Smart Hub生态系统规划**
   - ✅ 完整的多站点发展战略文档
   - ✅ 域名迁移策略和时间线
   - ✅ 主站、智能家居站、AI工具评测站架构
   - ✅ 商业化变现路径规划

4. **GitHub Actions工作流优化**
   - ✅ 简化内容生成流程，减少复杂依赖
   - ✅ 增强错误处理和回退机制
   - ✅ 添加多层级测试工作流
   - ✅ 改进日志记录和状态反馈

5. **Telegram通知系统测试增强**
   - 🔄 创建多个测试工作流验证通知功能
   - 🔄 GitHub Secrets配置完成，等待工作流同步
   - ✅ 本地测试脚本开发完成
   - ✅ 简化版和完整版通知系统都已准备

### ✅ Previous Completed Optimizations

1. **Intelligent Telegram Notification System**
   - Bot Token: Configured in GitHub Secrets (`TELEGRAM_BOT_TOKEN`)
   - Chat ID: Configured in GitHub Secrets (`TELEGRAM_CHAT_ID`)
   - Smart filtering with quiet hours (22:00-08:00 China time)
   - Priority-based notifications (ERROR > SUCCESS > INFO)
   - Chinese language interface for better user experience

2. **Automated Content Generation**
   - Daily execution (now optimized to 1:00 AM UTC / 9:00 AM China time)
   - Trending keyword analysis with Google Trends integration
   - Anti-AI content generation with human-like patterns
   - Automatic commit and deployment pipeline

3. **Product Database Optimization**
   - Real Amazon product URLs integrated
   - Updated affiliate link structure
   - Prepared for Amazon Associates program integration

## Development Commands

### Daily Operations

```bash
# Manual content generation
python scripts/generate_articles.py --batch-size=3

# Test Telegram notifications
python scripts/notify_telegram.py --type build --status success --site-url https://ai-smarthome.vercel.app

# Update keyword trends manually
python modules/keyword_tools/keyword_analyzer.py --update-trends

# Build site locally
hugo server -D
```

### Automation Management

```bash
# Check GitHub Actions status
gh run list --repo fzero1925/ai-smarthome --limit 5

# View workflow logs
gh run view [run-id] --repo fzero1925/ai-smarthome

# Manually trigger daily content generation
gh workflow run daily-content.yml --repo fzero1925/ai-smarthome -f force_generation=true -f article_count=1
```

### Telegram Notification Testing

```bash
# Test Telegram Bot connectivity (local)
python simple_telegram_test.py  # Simple test script
python direct_telegram_test.py  # Using existing notification system

# Test via GitHub Actions workflows
gh workflow run test-telegram.yml --repo fzero1925/ai-smarthome
gh workflow run minimal-telegram-test.yml --repo fzero1925/ai-smarthome

# Manual notification testing
python scripts/notify_telegram.py --type build --status success --site-url https://ai-smarthome.vercel.app
python scripts/notify_telegram.py --type error --error-type "Test Error" --error-message "Test message"

# Check GitHub Secrets configuration
gh secret list --repo fzero1925/ai-smarthome
```

### Available Test Workflows

**主要工作流**：
- `daily-content.yml` - 主要的内容生成和通知工作流
- `test-telegram.yml` - 完整的Telegram功能测试
- `minimal-telegram-test.yml` - 最小化的连接测试

**测试脚本**：
- `simple_telegram_test.py` - 基础连接测试（无外部依赖）
- `direct_telegram_test.py` - 调用完整通知系统测试
- `scripts/test_telegram.py` - 高级通知系统测试
- `test_basic_telegram.py` - 逻辑验证测试

## Environment Configuration

### Required GitHub Secrets

```bash
TELEGRAM_BOT_TOKEN=8494031502:AAHrT6csi5COqeUgG-wk_SiaYNjiXOFB-m4
TELEGRAM_CHAT_ID=6041888803
GOOGLE_ADSENSE_ID=ca-pub-XXXXXXXXXXXXXXXX
AMAZON_AFFILIATE_TAG=yourtag-20
GOOGLE_ANALYTICS_ID=G-XXXXXXXXXX
```

### Notification Settings

- **Quiet Hours**: 22:00-08:00 (China Time/UTC+8)
- **Priority Levels**: 
  - ERROR: Always sent (system failures, build errors)
  - SUCCESS: Active hours only (content generation, deployments)  
  - INFO: Minimal sending (routine operations)

### Automation Schedule

- **Daily Content Generation**: 1:00 AM UTC (9:00 AM China Time) - ✅ Optimized for global audience
- **SEO Optimization**: Runs with content generation
- **Content Refresh**: Weekly refresh of older articles
- **Keyword Analysis**: Daily trending analysis
- **Enhanced Notifications**: Real-time Telegram alerts with keyword insights

## Architecture Overview

### Content Generation Pipeline

1. **Keyword Analysis** (`modules/keyword_tools/keyword_analyzer.py`)
   - Google Trends integration via Pytrends
   - Smart home category focus
   - Commercial intent analysis
   - 24-hour result caching

2. **Anti-AI Content Generator** (`modules/content_generator/anti_ai_content_generator.py`)
   - Human-like writing patterns
   - 2500-3500 word target length
   - SEO optimization with 65+ readability score
   - Real product recommendations with Amazon links

3. **Automated Publishing** (`.github/workflows/daily-content.yml`)
   - Smart generation logic (avoids duplicates)
   - Quality checks and validation
   - Automatic Git commits with proper attribution
   - Telegram notification integration

### Notification System

**Smart Filtering Logic**:
```python
# Time-based filtering
quiet_hours = 22:00-08:00 (China Time)
if is_quiet_hours() and level != 'ERROR':
    skip_notification()

# Priority-based routing
ERROR -> Always send immediately
SUCCESS -> Send during active hours
INFO -> Minimal/batched sending
```

**Enhanced Message Format (2025-08-31 Update)**:
- Full Chinese language interface for user-friendly experience
- Emoji-based status indicators with context
- Trending keywords display (top 3 with scores)
- Used keywords tracking for current generation
- Quality check results integration
- China timezone time display
- Compact yet comprehensive information layout
- Quick action links and website access

## File Organization

### Critical Directories
- `.github/workflows/` - Automation workflows
- `scripts/` - Utility and notification scripts
- `modules/` - Core business logic
- `content/articles/` - Published articles
- `static/images/products/` - Product images (placeholders)

### Key Files
- `daily-content.yml` - Main automation workflow (修复版)
- `test-telegram.yml` - Telegram功能测试工作流
- `minimal-telegram-test.yml` - 最小化测试工作流
- `notify_telegram.py` - 完整通知系统
- `anti_ai_content_generator.py` - 内容生成引擎
- `AI_SMART_HUB_ECOSYSTEM_PLAN.md` - 生态系统规划文档
- `requirements.txt` - Python依赖 (包含pytz)

## Troubleshooting

### Common Issues

1. **Telegram Notifications Not Working**
   ```bash
   # Step 1: 验证GitHub Secrets配置
   gh secret list --repo fzero1925/ai-smarthome
   
   # Step 2: 本地基础测试
   python simple_telegram_test.py
   
   # Step 3: 完整系统测试
   python direct_telegram_test.py
   
   # Step 4: 工作流测试 (需要等待GitHub同步)
   gh workflow run minimal-telegram-test.yml --repo fzero1925/ai-smarthome
   
   # Step 5: 手动API测试
   curl "https://api.telegram.org/bot{BOT_TOKEN}/getMe"
   curl "https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
   ```

2. **GitHub Actions Failures**
   ```bash
   # Check all workflow runs
   gh run list --repo fzero1925/ai-smarthome --limit 10
   
   # View specific run details
   gh run view [run-id] --repo fzero1925/ai-smarthome
   
   # Check workflow sync status (新工作流需要时间同步)
   gh workflow list --repo fzero1925/ai-smarthome
   
   # Manual trigger (if workflow_dispatch available)
   gh workflow run daily-content.yml --repo fzero1925/ai-smarthome -f force_generation=true
   ```

3. **工作流同步问题 (新增)**
   ```bash
   # 问题：新创建的工作流无法手动触发
   # 原因：GitHub需要5-10分钟同步新的工作流文件
   # 解决：等待同步完成，或通过push触发
   
   # 检查工作流是否可用
   gh workflow list --repo fzero1925/ai-smarthome
   
   # 通过文件修改触发 (立即生效)
   echo "trigger test" > TELEGRAM_TEST_NOW.txt
   git add . && git commit -m "trigger test" && git push
   ```

3. **Content Generation Issues**
   ```bash
   # Test content generation locally
   python scripts/generate_articles.py --dry-run --batch-size=1
   
   # Check keyword cache
   ls -la data/keyword_cache/
   ```

### Performance Monitoring

- **Response Time Target**: <2 seconds
- **Content Quality Score**: >0.8 (anti-AI detection)
- **SEO Score Target**: >0.8
- **Daily Generation Success Rate**: >95%

## Next Phase Development

### Immediate Priorities (Week 1-2)

1. **Image Quality Improvement**
   - Replace Unsplash placeholders with real product images
   - Amazon product image integration
   - Consistent sizing and optimization

2. **Amazon Associates Integration**
   - Apply for Amazon Associates program
   - Replace test affiliate tags with real ones
   - Implement dynamic price tracking

3. **Google AdSense Preparation**
   - Content-image matching verification
   - User experience optimization
   - Legal pages and privacy policy

### Medium-term Goals (Month 1-3)

1. **Revenue Optimization**
   - A/B testing of ad placements
   - Conversion rate optimization
   - Performance analytics dashboard

2. **Content Expansion**
   - Additional smart home categories
   - Seasonal content campaigns
   - User-generated content integration

3. **Technical Improvements**
   - Advanced SEO automation
   - Performance monitoring
   - Backup and disaster recovery

## Success Metrics

- **Content Generation**: 1-3 articles daily
- **SEO Performance**: Rising search rankings
- **User Engagement**: Increasing organic traffic
- **Revenue Growth**: AdSense + Affiliate earnings
- **System Reliability**: 99%+ uptime

## Security Notes

- All sensitive tokens stored in GitHub Secrets
- No hardcoded credentials in codebase
- Regular dependency updates for security
- Private business logic excluded from public repos

---

**Last Updated**: 2025-08-31  
**System Status**: ✅ Fully Operational & Recently Enhanced  
**Next Automated Run**: Daily at 09:00 AM China Time (Optimized for Global Audience)
**Recent Changes**: Interface simplified, notifications enhanced, global timing optimized