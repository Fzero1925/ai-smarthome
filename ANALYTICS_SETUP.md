# Google Analytics & Search Console Setup Guide

## Google Analytics 4 (GA4) Setup

### Step 1: Create Google Analytics Account
1. Visit https://analytics.google.com/
2. Click "Start measuring"
3. Create Account name: "AI Smart Home Hub"
4. Choose data sharing settings (recommended: all checked for insights)

### Step 2: Create Property
1. Property name: "AI Smart Home Hub Website"
2. Time zone: Select your local timezone
3. Currency: USD (or your local currency)
4. Industry category: "Internet & Telecom > Internet & Telecom Other"
5. Business size: "Small" (1-10 employees)

### Step 3: Set Up Data Stream
1. Choose "Web" platform
2. Website URL: https://ai-smarthomehub.com
3. Stream name: "Main Website"
4. Copy the Measurement ID (format: G-XXXXXXXXXX)

### Step 4: Update Hugo Configuration
1. Open `config.yaml`
2. Replace `G-XXXXXXXXXX` with your actual Measurement ID
3. Save the file

### Step 5: Enable Enhanced Measurement
In GA4 property settings, ensure these are enabled:
- [ ] Page views (auto-enabled)
- [ ] Scrolls (90% scroll depth)
- [ ] Outbound clicks
- [ ] Site search
- [ ] Video engagement
- [ ] File downloads

## Google Search Console Setup

### Step 1: Add Property
1. Visit https://search.google.com/search-console/
2. Click "Add property"
3. Choose "URL prefix" method
4. Enter: https://ai-smarthomehub.com

### Step 2: Verify Ownership
Choose one verification method:
- **HTML tag method** (easiest):
  1. Copy the meta tag provided
  2. Add to Hugo's `<head>` section in baseof.html template
  3. Deploy site and click "Verify"

- **Google Analytics method** (if GA4 is already set up):
  1. Select "Google Analytics" 
  2. Click "Verify" (automatic if same Google account)

### Step 3: Submit Sitemap
1. In Search Console, go to "Sitemaps" in left menu
2. Add new sitemap: https://ai-smarthomehub.com/sitemap.xml
3. Click "Submit"

### Step 4: Set Up URL Inspection
Test important pages:
- https://ai-smarthomehub.com/ (homepage)
- https://ai-smarthomehub.com/about/ (about page)
- https://ai-smarthomehub.com/contact/ (contact page)
- Key article pages

## AdSense Preparation Tracking

### Key Metrics to Monitor Before AdSense Application

#### Traffic Requirements
- **Page views**: Aim for 1,000+ monthly page views
- **Unique visitors**: Target 300+ monthly unique visitors  
- **Session duration**: Maintain 2+ minute average sessions
- **Pages per session**: Target 1.5+ pages per session
- **Bounce rate**: Keep below 70%

#### Content Quality Metrics
- **Total articles**: Need 20+ high-quality articles
- **Average word count**: 1,500+ words per article
- **Fresh content**: Regular publishing (2-3 articles/week)
- **Internal linking**: 5+ internal links per article
- **External authority links**: Link to reputable sources

#### User Engagement Indicators
- **Organic search traffic**: 60%+ from search engines
- **Direct traffic**: 20%+ direct visits (bookmarks, typed URL)
- **Social referrals**: Some traffic from social media
- **Return visitors**: 30%+ returning users

### Monthly Reporting Checklist

Create monthly reports tracking:
- [ ] Total page views and trend
- [ ] Unique visitors and growth rate
- [ ] Top performing articles
- [ ] Search engine rankings for key terms
- [ ] Page loading speed (Core Web Vitals)
- [ ] Mobile usability score
- [ ] Security issues (Search Console)

## Timeline for AdSense Application

### Month 1-2: Foundation Building
- [ ] Install and configure GA4
- [ ] Set up Search Console
- [ ] Publish 15+ articles
- [ ] Achieve 500+ monthly page views
- [ ] Fix any technical SEO issues

### Month 2-3: Traffic Growth
- [ ] Reach 1,000+ monthly page views
- [ ] Publish 25+ total articles
- [ ] Improve Core Web Vitals scores
- [ ] Build organic search presence
- [ ] Establish returning visitor base

### Month 3-4: AdSense Readiness
- [ ] Maintain 1,500+ monthly page views
- [ ] Achieve 2+ minute session duration
- [ ] Complete privacy policy compliance
- [ ] Ensure mobile-friendly design
- [ ] **Submit AdSense application**

## Critical AdSense Approval Factors

### Content Quality Requirements
- [ ] Original, high-quality content (no duplicates)
- [ ] Proper grammar and spelling
- [ ] Comprehensive coverage of topics
- [ ] Regular publication schedule
- [ ] User-focused value (not just for search engines)

### Technical Requirements  
- [ ] Fast loading speed (<3 seconds)
- [ ] Mobile-responsive design
- [ ] HTTPS security certificate
- [ ] Working navigation and search
- [ ] No broken links or 404 errors

### Legal and Policy Compliance
- [ ] Comprehensive privacy policy
- [ ] Clear terms of service
- [ ] Proper affiliate disclosure
- [ ] Contact information easily accessible
- [ ] About page with site purpose

### Traffic Quality
- [ ] Organic search traffic majority
- [ ] No artificial traffic inflation
- [ ] Engaged user behavior metrics
- [ ] Global traffic distribution
- [ ] Consistent monthly growth

## Tools and Resources

### Free Analytics Tools
- Google Analytics 4: Core traffic and behavior data
- Google Search Console: SEO performance and indexing
- Google PageSpeed Insights: Core Web Vitals testing
- Google Tag Assistant: Verify tracking code installation

### SEO and Content Tools  
- Ubersuggest: Keyword research and site audit
- AnswerThePublic: Content idea generation
- Hemingway Editor: Content readability improvement
- Yoast SEO Plugin: On-page optimization guidance

### Monitoring and Alerts
Set up automatic alerts for:
- Sudden traffic drops (>20% week-over-week)
- Core Web Vitals issues
- Search Console error notifications
- Site downtime or security issues

---

**Note**: This setup should be completed within the first 2 weeks of launch. Early tracking is crucial for establishing baseline metrics and demonstrating consistent traffic growth to AdSense reviewers.

**Next Steps**: After setup, focus on content creation and SEO optimization while monitoring these metrics weekly. AdSense applications are most successful after 60-90 days of consistent operation with proven traffic and engagement.