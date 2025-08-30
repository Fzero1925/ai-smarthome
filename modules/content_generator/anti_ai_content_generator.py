"""
Advanced Anti-AI Detection Content Generator

This module creates high-quality, human-like content that passes AI detection tools
while maintaining SEO optimization and user value. Uses sophisticated text variation
techniques, natural language patterns, and contextual intelligence.
"""

import random
import re
import os
import json
from datetime import datetime, date
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass
from jinja2 import Template, Environment, FileSystemLoader
import pandas as pd
from pathlib import Path


@dataclass
class ContentVariation:
    """Container for content variation patterns"""
    sentence_starters: List[str]
    transition_phrases: List[str]
    conclusion_patterns: List[str]
    expertise_markers: List[str]
    personal_touches: List[str]


class AntiAIContentGenerator:
    """
    Sophisticated content generator designed to create human-like articles
    that bypass AI detection while maintaining high quality and SEO value.
    """
    
    def __init__(self, templates_dir: str = "data/templates"):
        self.templates_dir = Path(templates_dir)
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize Jinja2 environment
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Load content variation patterns
        self.variations = self._load_content_variations()
        
        # Product database for realistic recommendations
        self.product_database = self._load_product_database()
        
        # Anti-AI detection patterns
        self.human_patterns = self._initialize_human_patterns()
        
        # Content quality metrics
        self.quality_thresholds = {
            'min_word_count': 1500,
            'max_word_count': 4000,
            'min_paragraphs': 8,
            'min_headings': 6,
            'readability_target': 65  # Flesch Reading Ease
        }
    
    def _load_content_variations(self) -> ContentVariation:
        """Load sophisticated content variation patterns"""
        return ContentVariation(
            sentence_starters=[
                "Based on extensive testing with over {} devices,",
                "After spending {} hours researching and comparing options,",
                "In my {} years of smart home expertise,",
                "Having personally tested {} different models,",
                "Through careful analysis of user feedback and technical specifications,",
                "Drawing from real-world testing across {} different scenarios,",
                "After consulting with industry experts and analyzing {} data points,",
                "Following comprehensive evaluation of performance metrics,",
                "Based on hands-on experience with leading manufacturers,",
                "After examining user reviews from {} verified purchases,"
            ],
            
            transition_phrases=[
                "However, it's worth noting that",
                "On the flip side,",
                "That said,", 
                "Interestingly,",
                "What's particularly impressive is",
                "One thing that stands out is",
                "It's also worth mentioning",
                "Another key consideration is",
                "From a practical standpoint,",
                "In real-world usage,",
                "Based on user feedback,",
                "According to our testing,",
                "What many people don't realize is",
                "Here's the thing though:",
                "The reality is that"
            ],
            
            conclusion_patterns=[
                "The bottom line is that {} offers exceptional value for most users.",
                "At the end of the day, {} delivers on its promises.",
                "When all factors are considered, {} emerges as a solid choice.",
                "For most homeowners, {} provides the right balance of features and affordability.",
                "If you're looking for reliable performance, {} won't disappoint.",
                "While no product is perfect, {} comes pretty close for its intended use case.",
                "The verdict? {} is definitely worth considering for your smart home setup.",
                "After thorough evaluation, {} earns our recommendation.",
                "Despite minor drawbacks, {} delivers impressive overall value.",
                "For the target audience, {} hits all the right notes."
            ],
            
            expertise_markers=[
                "In my professional experience,",
                "From a technical standpoint,",
                "What I've learned from testing dozens of similar products is",
                "Industry insiders know that",
                "Professional installers often recommend",
                "Based on feedback from the smart home community,",
                "Expert tip:",
                "Pro insight:",
                "Here's something most reviews won't tell you:",
                "After years in the industry, I can say"
            ],
            
            personal_touches=[
                "I was genuinely surprised by",
                "What caught my attention was",
                "I'll be honest -",
                "To be fair,",
                "I have to admit,",
                "Personally, I find that",
                "In my household, we've noticed",
                "I've recommended this to several friends because",
                "What impressed me most was",
                "I wasn't expecting much, but"
            ]
        )
    
    def _load_product_database(self) -> Dict[str, List[Dict]]:
        """Load realistic product data for authentic recommendations"""
        return {
            'smart_plugs': [
                {
                    'name': 'Amazon Smart Plug',
                    'price': 12.99,
                    'original_price': 24.99,
                    'rating': 4.5,
                    'reviews': 89247,
                    'features': ['Works with Alexa', 'Compact design', 'Easy setup', 'Voice control'],
                    'pros': ['Native Alexa integration', 'Reliable connectivity', 'Simple setup'],
                    'cons': ['No energy monitoring', 'Single outlet only'],
                    'best_for': 'Alexa users wanting seamless integration'
                },
                {
                    'name': 'TP-Link Kasa Smart Plug HS103',
                    'price': 7.99,
                    'original_price': 12.99,
                    'rating': 4.4,
                    'reviews': 45632,
                    'features': ['Energy monitoring', 'Scheduling', 'Away mode', 'No hub required'],
                    'pros': ['Energy tracking', 'Excellent app', 'Great value'],
                    'cons': ['Slightly larger', '2.4GHz only'],
                    'best_for': 'Users wanting energy monitoring on a budget'
                },
                {
                    'name': 'Govee Smart Plug WiFi',
                    'price': 8.99,
                    'original_price': 15.99,
                    'rating': 4.2,
                    'reviews': 12847,
                    'features': ['Energy monitoring', 'Voice control', 'Timer function', 'Scene modes'],
                    'pros': ['Great price', 'Energy monitoring', 'Good app'],
                    'cons': ['Basic build quality', 'Limited features'],
                    'best_for': 'Budget-conscious users'
                }
            ],
            
            'smart_bulbs': [
                {
                    'name': 'Philips Hue White and Color A19',
                    'price': 49.99,
                    'original_price': 59.99,
                    'rating': 4.7,
                    'reviews': 28471,
                    'features': ['16 million colors', 'Hub required', 'Dimming', 'Voice control'],
                    'pros': ['Excellent colors', 'Reliable', 'Great ecosystem'],
                    'cons': ['Expensive hub', 'Higher cost'],
                    'best_for': 'Users wanting premium smart lighting'
                },
                {
                    'name': 'LIFX A19 Wi-Fi Smart Bulb',
                    'price': 39.99,
                    'original_price': 49.99,
                    'rating': 4.3,
                    'reviews': 15234,
                    'features': ['No hub required', '1100 lumens', 'Music sync', 'WiFi direct'],
                    'pros': ['No hub needed', 'Very bright', 'Rich colors'],
                    'cons': ['WiFi dependent', 'Connectivity issues'],
                    'best_for': 'No-hub smart lighting solution'
                }
            ]
        }
    
    def _initialize_human_patterns(self) -> Dict[str, List[str]]:
        """Initialize patterns that make content appear more human-written"""
        return {
            'contractions': [
                ("do not", "don't"), ("will not", "won't"), ("cannot", "can't"),
                ("would not", "wouldn't"), ("should not", "shouldn't"),
                ("could not", "couldn't"), ("is not", "isn't"), ("are not", "aren't"),
                ("was not", "wasn't"), ("were not", "weren't"), ("have not", "haven't"),
                ("has not", "hasn't"), ("had not", "hadn't"), ("you will", "you'll"),
                ("we will", "we'll"), ("they will", "they'll"), ("I will", "I'll")
            ],
            
            'casual_phrases': [
                "Let's be real", "Here's the deal", "Bottom line", "To put it simply",
                "In plain English", "The truth is", "Between you and me", "Let's face it",
                "No sugarcoating", "Straight up", "The reality check", "Cut to the chase"
            ],
            
            'hedging_language': [
                "seems to", "appears to", "tends to", "generally", "typically",
                "usually", "often", "frequently", "commonly", "in most cases",
                "for the most part", "by and large", "more or less"
            ],
            
            'emphasis_markers': [
                "absolutely", "definitely", "certainly", "undoubtedly", "without a doubt",
                "clearly", "obviously", "frankly", "honestly", "surprisingly",
                "remarkably", "impressively", "unexpectedly", "fortunately"
            ]
        ]
    
    def generate_smart_home_article(self, 
                                  keyword: str, 
                                  category: str,
                                  article_type: str = "review",
                                  target_length: int = 2500) -> Dict[str, Any]:
        """
        Generate comprehensive smart home article with anti-AI detection features
        
        Args:
            keyword: Primary keyword for the article
            category: Product category (smart_plugs, smart_bulbs, etc.)
            article_type: Type of article (review, guide, comparison)
            target_length: Target word count
            
        Returns:
            Dictionary containing article content and metadata
        """
        
        # Generate article structure
        structure = self._create_article_structure(keyword, category, article_type)
        
        # Create content sections
        content_sections = {}
        
        # Generate introduction with human patterns
        content_sections['introduction'] = self._generate_introduction(
            keyword, category, target_length
        )
        
        # Generate main content sections
        content_sections['main_content'] = self._generate_main_sections(
            keyword, category, structure
        )
        
        # Generate product recommendations if applicable
        if category in self.product_database:
            content_sections['product_recommendations'] = self._generate_product_section(
                keyword, category
            )
        
        # Generate FAQ section
        content_sections['faq'] = self._generate_faq_section(keyword, category)
        
        # Generate conclusion
        content_sections['conclusion'] = self._generate_conclusion(keyword, category)
        
        # Apply human-like text transformations
        for section_key in content_sections:
            content_sections[section_key] = self._apply_humanization(
                content_sections[section_key]
            )
        
        # Combine all sections
        full_content = self._combine_sections(content_sections, structure)
        
        # Generate metadata
        metadata = self._generate_metadata(keyword, category, full_content)
        
        return {
            'title': structure['title'],
            'content': full_content,
            'metadata': metadata,
            'featured_products': content_sections.get('product_recommendations', {}),
            'faq': content_sections['faq'],
            'word_count': len(full_content.split()),
            'generation_date': datetime.now(),
            'anti_ai_score': self._calculate_anti_ai_score(full_content)
        }
    
    def _create_article_structure(self, keyword: str, category: str, article_type: str) -> Dict:
        """Create intelligent article structure based on keyword and category"""
        
        # Title variations to avoid repetitive patterns
        title_patterns = {
            'review': [
                f"Best {keyword.title()} 2025: Complete Review & Buying Guide",
                f"{keyword.title()} Review: Top Picks for Smart Home Enthusiasts", 
                f"Ultimate Guide to {keyword.title()}: Reviews, Features & Pricing",
                f"{keyword.title()} Comparison: Which Models Deliver Real Value?"
            ],
            'guide': [
                f"How to Choose the Perfect {keyword.title()}: Expert Guide 2025",
                f"{keyword.title()} Setup Guide: From Unboxing to Smart Integration",
                f"Complete {keyword.title()} Installation & Optimization Guide",
                f"{keyword.title()} for Beginners: Everything You Need to Know"
            ],
            'comparison': [
                f"{keyword.title()} Showdown: Comparing Top Models Side-by-Side",
                f"Best {keyword.title()} Comparison: Features, Pricing & Performance",
                f"{keyword.title()} Face-Off: Which Brand Offers Better Value?"
            ]
        }
        
        structure = {
            'title': random.choice(title_patterns.get(article_type, title_patterns['review'])),
            'sections': self._generate_section_outline(keyword, category, article_type),
            'word_distribution': self._calculate_section_lengths(2500)  # Target length
        }
        
        return structure
    
    def _generate_section_outline(self, keyword: str, category: str, article_type: str) -> List[Dict]:
        """Generate intelligent section outline"""
        
        base_sections = [
            {'heading': 'Introduction', 'type': 'introduction'},
            {'heading': f'Why {keyword.title()} Matters in 2025', 'type': 'context'},
            {'heading': 'Key Features to Consider', 'type': 'features'},
            {'heading': 'Top Product Recommendations', 'type': 'products'},
            {'heading': 'Installation & Setup Guide', 'type': 'guide'},
            {'heading': 'Troubleshooting Common Issues', 'type': 'troubleshooting'},
            {'heading': 'Frequently Asked Questions', 'type': 'faq'},
            {'heading': 'Final Verdict', 'type': 'conclusion'}
        ]
        
        # Customize sections based on category
        category_specific = {
            'smart_plugs': [
                {'heading': 'Energy Monitoring vs Basic Control', 'type': 'comparison'},
                {'heading': 'Voice Assistant Compatibility', 'type': 'features'}
            ],
            'smart_bulbs': [
                {'heading': 'Color vs White Light: Which Do You Need?', 'type': 'comparison'},
                {'heading': 'Hub vs No-Hub Solutions', 'type': 'technical'}
            ],
            'security_cameras': [
                {'heading': 'Indoor vs Outdoor Camera Requirements', 'type': 'comparison'},
                {'heading': 'Privacy and Data Security Considerations', 'type': 'security'}
            ]
        }
        
        # Insert category-specific sections
        if category in category_specific:
            # Insert after features section
            insert_pos = 3
            for section in reversed(category_specific[category]):
                base_sections.insert(insert_pos, section)
        
        return base_sections
    
    def _calculate_section_lengths(self, target_length: int) -> Dict[str, int]:
        """Calculate optimal word count distribution across sections"""
        return {
            'introduction': int(target_length * 0.15),
            'context': int(target_length * 0.12),
            'features': int(target_length * 0.18),
            'products': int(target_length * 0.25),
            'guide': int(target_length * 0.12),
            'troubleshooting': int(target_length * 0.08),
            'faq': int(target_length * 0.08),
            'conclusion': int(target_length * 0.02)
        }
    
    def _generate_introduction(self, keyword: str, category: str, target_length: int) -> str:
        """Generate engaging, human-like introduction"""
        
        # Random expert credentials to establish authority
        credentials = random.choice([
            f"After testing over {random.randint(50, 150)} smart home devices",
            f"With {random.randint(5, 12)} years in home automation",
            f"Having consulted for {random.randint(3, 8)} major tech companies",
            f"Following {random.randint(100, 500)} hours of hands-on testing"
        ])
        
        # Opening hook variations
        hooks = [
            f"The {keyword} market has exploded in recent years, but finding the right device for your specific needs shouldn't feel like solving a puzzle.",
            f"If you're tired of mediocre {keyword} options that promise the world but deliver disappointment, you're not alone.",
            f"Smart home technology has reached a tipping point where {keyword} devices actually deliver on their promises—when you choose the right ones.",
            f"The difference between a great {keyword} and a frustrating paperweight often comes down to details most reviews completely ignore."
        ]
        
        # Problem statement with personal touch
        problems = [
            f"I've personally experienced the frustration of {keyword} devices that work great in demos but fail in real-world conditions.",
            f"Too many people waste money on {keyword} products that looked perfect online but turned out to be completely wrong for their situation.",
            f"The {keyword} space is crowded with options that seem identical on paper but perform drastically differently in practice."
        ]
        
        # Solution preview
        solutions = [
            f"In this comprehensive guide, I'll share the insights I've gained from extensive testing and real-world usage.",
            f"This article cuts through the marketing fluff to give you the practical information you need to make a confident decision.",
            f"I'll walk you through everything from technical specifications to hidden gotchas that other reviews conveniently skip."
        ]
        
        introduction_parts = [
            random.choice(hooks),
            f"{credentials}, {random.choice(problems)}",
            random.choice(solutions),
            f"Whether you're new to smart home technology or upgrading existing equipment, you'll find actionable insights that save both time and money."
        ]
        
        return " ".join(introduction_parts)
    
    def _generate_main_sections(self, keyword: str, category: str, structure: Dict) -> List[str]:
        """Generate main content sections with variation and depth"""
        
        sections = []
        
        for section in structure['sections']:
            if section['type'] in ['introduction', 'faq', 'conclusion']:
                continue  # Handle separately
                
            section_content = self._generate_section_content(
                section, keyword, category
            )
            sections.append(f"## {section['heading']}\n\n{section_content}")
        
        return sections
    
    def _generate_section_content(self, section: Dict, keyword: str, category: str) -> str:
        """Generate content for individual sections"""
        
        section_type = section['type']
        heading = section['heading']
        
        if section_type == 'context':
            return self._generate_context_section(keyword, category)
        elif section_type == 'features':
            return self._generate_features_section(keyword, category)
        elif section_type == 'comparison':
            return self._generate_comparison_section(keyword, category)
        elif section_type == 'guide':
            return self._generate_guide_section(keyword, category)
        elif section_type == 'troubleshooting':
            return self._generate_troubleshooting_section(keyword, category)
        else:
            return self._generate_generic_section(heading, keyword, category)
    
    def _generate_context_section(self, keyword: str, category: str) -> str:
        """Generate contextual background section"""
        
        market_insights = [
            f"The {keyword} market has matured significantly, with manufacturers focusing more on reliability and user experience rather than just adding flashy features.",
            f"Consumer expectations for {keyword} devices have evolved beyond basic functionality to include seamless integration, energy efficiency, and long-term reliability.",
            f"Recent industry developments have made {keyword} technology more accessible while improving performance across the board."
        ]
        
        user_benefits = {
            'smart_plugs': [
                "Energy monitoring capabilities help identify power-hungry devices",
                "Remote control prevents the 'did I leave it on?' anxiety",
                "Scheduled automation reduces energy waste without sacrificing convenience"
            ],
            'smart_bulbs': [
                "Circadian rhythm support improves sleep quality naturally",
                "Customizable scenes enhance home ambiance for different activities", 
                "Energy efficiency reduces electricity costs while providing better lighting control"
            ],
            'security_cameras': [
                "Real-time alerts provide immediate notification of important events",
                "Cloud storage ensures footage is preserved even if equipment is damaged",
                "Integration with smart home systems enables automated responses to security events"
            ]
        }
        
        current_trends = [
            f"Matter compatibility is becoming standard, ensuring {keyword} devices work with multiple smart home platforms",
            f"AI-powered features are moving beyond gimmicks to provide genuinely useful automation",
            f"Privacy-focused designs address growing consumer concerns about data collection"
        ]
        
        content_parts = [
            random.choice(market_insights),
            f"For homeowners considering {keyword} upgrades, the benefits extend beyond convenience:",
            "\n".join([f"• {benefit}" for benefit in user_benefits.get(category, ["Enhanced control", "Improved efficiency", "Better integration"])]),
            f"\n{random.choice(current_trends)} This shift means your investment in {keyword} technology will remain relevant longer."
        ]
        
        return "\n\n".join(content_parts)
    
    def _generate_features_section(self, keyword: str, category: str) -> str:
        """Generate detailed features analysis"""
        
        feature_categories = {
            'smart_plugs': {
                'Essential Features': [
                    'WiFi connectivity with 2.4GHz support for reliable connection',
                    'Voice control compatibility with Alexa, Google Assistant, or Siri', 
                    'Mobile app with intuitive scheduling and timer functions',
                    'Compact design that doesn\'t block adjacent outlets'
                ],
                'Advanced Features': [
                    'Energy monitoring with detailed usage analytics',
                    'Away mode for security with randomized on/off patterns',
                    'Integration with IFTTT for complex automation rules',
                    'Surge protection to safeguard connected devices'
                ]
            },
            'smart_bulbs': {
                'Lighting Quality': [
                    'Color temperature range from warm (2700K) to daylight (6500K)',
                    'High Color Rendering Index (CRI 90+) for accurate color representation',
                    'Smooth dimming without flicker across the full brightness range',
                    'Consistent color accuracy across multiple bulbs'
                ],
                'Smart Features': [
                    'Music sync for entertainment lighting effects',
                    'Circadian rhythm support with automatic color temperature adjustment',
                    'Scene presets for common activities like reading or relaxing',
                    'Vacation mode to simulate occupancy while away'
                ]
            }
        }
        
        category_features = feature_categories.get(category, {
            'Core Features': ['Reliable connectivity', 'Easy setup', 'Voice control'],
            'Advanced Features': ['Automation support', 'Integration capabilities']
        })
        
        content_sections = []
        
        for feature_group, features in category_features.items():
            content_sections.append(f"### {feature_group}")
            
            # Add expert insight
            expert_intro = random.choice(self.variations.expertise_markers)
            content_sections.append(f"{expert_intro} these features separate quality {keyword} devices from budget alternatives that might look similar on paper:")
            
            # List features with brief explanations
            for feature in features:
                content_sections.append(f"• **{feature.split(' ')[0]} {feature.split(' ')[1] if len(feature.split()) > 1 else ''}**: {feature}")
        
        # Add practical advice
        practical_note = random.choice([
            f"When evaluating {keyword} options, prioritize features you'll actually use daily rather than impressive-sounding capabilities you might try once.",
            f"The most expensive {keyword} isn't always the best choice—focus on features that align with your specific use case and home setup.",
            f"Consider your existing smart home ecosystem when choosing {keyword} devices to ensure seamless integration."
        ])
        
        content_sections.append(f"\n**Pro tip:** {practical_note}")
        
        return "\n\n".join(content_sections)
    
    def _generate_product_section(self, keyword: str, category: str) -> Dict:
        """Generate realistic product recommendations with detailed analysis"""
        
        if category not in self.product_database:
            return {}
        
        products = self.product_database[category][:3]  # Top 3 recommendations
        
        product_content = []
        featured_products = []
        
        for i, product in enumerate(products, 1):
            # Generate detailed product analysis
            analysis_intro = random.choice([
                f"After extensive testing, the {product['name']} consistently delivers",
                f"What sets the {product['name']} apart is its",
                f"The {product['name']} impressed me with its",
                f"In real-world usage, the {product['name']} excels at"
            ])
            
            # Create nuanced review
            review_parts = [
                f"### {i}. {product['name']} - {product['best_for']}",
                f"{analysis_intro} reliable performance across different scenarios.",
                f"**Key Strengths:**"
            ]
            
            for pro in product['pros']:
                review_parts.append(f"• {pro}")
            
            review_parts.extend([
                f"\n**Considerations:**"
            ])
            
            for con in product['cons']:
                review_parts.append(f"• {con}")
            
            # Add personal experience note
            personal_note = random.choice(self.variations.personal_touches)
            review_parts.append(f"\n{personal_note} how well this device handles edge cases that cheaper alternatives struggle with.")
            
            # Pricing context
            if product['original_price'] > product['price']:
                discount = int(((product['original_price'] - product['price']) / product['original_price']) * 100)
                review_parts.append(f"At ${product['price']} (regularly ${product['original_price']}), this {discount}% discount makes it particularly attractive.")
            
            product_content.append("\n".join(review_parts))
            
            # Format for Hugo template
            featured_products.append({
                'name': product['name'],
                'rating': product['rating'],
                'reviews': product['reviews'],
                'current_price': product['price'],
                'original_price': product.get('original_price', product['price']),
                'features': product['features'],
                'pros_cons': {
                    'pros': product['pros'],
                    'cons': product['cons']
                },
                'amazon_url': f"https://amazon.com/dp/example{i}",
                'badge': ['Editor\'s Choice', 'Best Value', 'Budget Pick'][i-1] if i <= 3 else 'Recommended'
            })
        
        return {
            'content': "\n\n".join(product_content),
            'products': featured_products
        }
    
    def _generate_faq_section(self, keyword: str, category: str) -> List[Dict[str, str]]:
        """Generate realistic FAQ section"""
        
        faq_templates = {
            'smart_plugs': [
                {
                    'question': f'Do {keyword} work without WiFi?',
                    'answer': 'Most smart plugs require WiFi for remote control and scheduling features. However, some models with Bluetooth connectivity can be controlled locally when your phone is nearby. For full smart home integration, WiFi connectivity is essential.'
                },
                {
                    'question': f'How much energy do {keyword} consume when in standby?',
                    'answer': 'Quality smart plugs typically consume 0.5-2 watts in standby mode, which translates to approximately $2-5 per year in electricity costs. This minimal consumption is offset by the energy savings from better device management and scheduling.'
                },
                {
                    'question': f'Can {keyword} handle high-power appliances?',
                    'answer': 'Standard smart plugs are rated for 15 amps (1800 watts), suitable for most household electronics and small appliances. For high-power devices like space heaters or power tools, look for heavy-duty models specifically rated for higher loads.'
                }
            ],
            'smart_bulbs': [
                {
                    'question': f'Do {keyword} work with dimmer switches?',
                    'answer': 'Smart bulbs should not be used with traditional dimmer switches, as this can cause compatibility issues and potential damage. Smart bulbs have built-in dimming capabilities controlled through apps or voice commands.'
                },
                {
                    'question': f'How long do {keyword} typically last?',
                    'answer': 'Quality LED smart bulbs typically last 15,000-25,000 hours (10-20 years with normal usage). However, the smart components may require firmware updates or could become obsolete before the LED itself fails.'
                },
                {
                    'question': f'Can I use {keyword} outdoors?',
                    'answer': 'Only use smart bulbs specifically rated for outdoor use (IP65 or higher). Indoor smart bulbs lack weather protection and will fail quickly in outdoor conditions. Check temperature ratings for your climate zone.'
                }
            ]
        }
        
        # Get category-specific FAQs or use generic ones
        faqs = faq_templates.get(category, [
            {
                'question': f'What makes {keyword} "smart"?',
                'answer': f'Smart {keyword} connect to your home WiFi network, allowing remote control via smartphone apps, voice commands, and automated scheduling based on time, location, or other triggers.'
            },
            {
                'question': f'Are {keyword} secure?',
                'answer': 'Security varies by manufacturer. Look for devices with WPA2/WPA3 encryption, regular firmware updates, and established brands with good security track records. Change default passwords and keep firmware updated.'
            },
            {
                'question': f'Do I need a smart home hub for {keyword}?',
                'answer': f'Many modern {keyword} connect directly to WiFi without requiring a separate hub. However, hub-based systems often provide more reliable connectivity and advanced automation features.'
            }
        ])
        
        return faqs[:4]  # Limit to 4 FAQs to avoid overwhelming readers
    
    def _generate_conclusion(self, keyword: str, category: str) -> str:
        """Generate compelling conclusion with call-to-action"""
        
        conclusion_elements = [
            # Summary of key points
            random.choice([
                f"Choosing the right {keyword} doesn't have to be complicated when you focus on your specific needs and use case.",
                f"The {keyword} market offers excellent options at every price point, making smart home automation more accessible than ever.",
                f"Quality {keyword} devices provide years of reliable service when properly selected and configured."
            ]),
            
            # Reinforce expertise
            random.choice(self.variations.expertise_markers) + random.choice([
                f" the most important factor is choosing devices that integrate well with your existing setup and lifestyle.",
                f" reliability and ease of use matter more than having the latest bells and whistles.",
                f" starting with one or two quality devices is better than buying multiple mediocre ones."
            ]),
            
            # Final recommendation
            random.choice(self.variations.conclusion_patterns).format(keyword),
            
            # Future-looking statement
            f"As smart home technology continues to evolve, investing in quality {keyword} from established manufacturers ensures your setup remains compatible and functional for years to come."
        ]
        
        return " ".join(conclusion_elements)
    
    def _apply_humanization(self, text: str) -> str:
        """Apply human-like writing patterns to reduce AI detection"""
        
        # Apply contractions naturally
        for formal, casual in self.human_patterns['contractions']:
            # Only replace in natural contexts (not in headings or formal sections)
            if random.random() < 0.3:  # 30% chance to apply each contraction
                text = text.replace(formal, casual)
        
        # Add casual phrases occasionally
        sentences = text.split('. ')
        for i, sentence in enumerate(sentences):
            if random.random() < 0.1 and i > 0:  # 10% chance, not first sentence
                casual_phrase = random.choice(self.human_patterns['casual_phrases'])
                sentences[i] = f"{casual_phrase}, {sentence.lower()}"
        
        text = '. '.join(sentences)
        
        # Add hedging language to soften absolute statements
        absolute_patterns = [
            (r'\bwill\b', lambda m: random.choice(['will likely', 'should', 'will typically'])),
            (r'\balways\b', lambda m: random.choice(['usually', 'generally', 'typically'])),
            (r'\bnever\b', lambda m: random.choice(['rarely', 'seldom', 'hardly ever']))
        ]
        
        for pattern, replacement in absolute_patterns:
            if random.random() < 0.4:  # 40% chance to soften absolutes
                text = re.sub(pattern, replacement, text)
        
        return text
    
    def _combine_sections(self, sections: Dict[str, Any], structure: Dict) -> str:
        """Combine all content sections into final article"""
        
        article_parts = [
            sections['introduction'],
            "\n".join(sections['main_content'])
        ]
        
        # Add product recommendations if available
        if 'product_recommendations' in sections and sections['product_recommendations']:
            article_parts.append(f"## Top {structure['title'].split(':')[0]} Recommendations")
            article_parts.append(sections['product_recommendations'].get('content', ''))
        
        # Add conclusion
        article_parts.append(f"## Conclusion")
        article_parts.append(sections['conclusion'])
        
        return "\n\n".join(article_parts)
    
    def _generate_metadata(self, keyword: str, category: str, content: str) -> Dict:
        """Generate comprehensive article metadata"""
        
        word_count = len(content.split())
        
        # Generate categories and tags
        categories = [category.replace('_', '-'), 'home-automation']
        
        tags = [
            keyword.lower(),
            'smart home',
            'automation',
            'review',
            'buying guide'
        ]
        
        # Add category-specific tags
        category_tags = {
            'smart_plugs': ['alexa', 'google home', 'energy monitoring', 'wifi outlet'],
            'smart_bulbs': ['led lighting', 'color changing', 'dimming', 'voice control'],
            'security_cameras': ['surveillance', 'home security', 'motion detection', 'night vision']
        }
        
        if category in category_tags:
            tags.extend(category_tags[category])
        
        return {
            'word_count': word_count,
            'categories': categories,
            'tags': tags[:8],  # Limit to 8 tags
            'estimated_read_time': max(1, word_count // 200),  # Rough reading time
            'seo_score': self._calculate_seo_score(content, keyword),
            'readability_score': self._estimate_readability(content)
        }
    
    def _calculate_anti_ai_score(self, content: str) -> float:
        """Calculate a score indicating how human-like the content appears"""
        score = 0.0
        
        # Check for contractions
        contraction_count = sum(1 for formal, casual in self.human_patterns['contractions'] 
                              if casual in content)
        score += min(0.2, contraction_count * 0.02)
        
        # Check for casual phrases
        casual_count = sum(1 for phrase in self.human_patterns['casual_phrases'] 
                          if phrase.lower() in content.lower())
        score += min(0.2, casual_count * 0.05)
        
        # Check for personal touches
        personal_count = sum(1 for phrase in self.variations.personal_touches 
                           if phrase.lower() in content.lower())
        score += min(0.3, personal_count * 0.1)
        
        # Check sentence length variation
        sentences = content.split('. ')
        if len(sentences) > 5:
            lengths = [len(s.split()) for s in sentences]
            avg_length = sum(lengths) / len(lengths)
            length_variance = sum((l - avg_length) ** 2 for l in lengths) / len(lengths)
            score += min(0.3, length_variance / 100)  # Normalize variance
        
        return min(1.0, score)
    
    def _calculate_seo_score(self, content: str, keyword: str) -> float:
        """Calculate basic SEO optimization score"""
        score = 0.0
        content_lower = content.lower()
        keyword_lower = keyword.lower()
        
        # Keyword density (aim for 1-2%)
        word_count = len(content.split())
        keyword_count = content_lower.count(keyword_lower)
        keyword_density = keyword_count / word_count
        
        if 0.01 <= keyword_density <= 0.02:
            score += 0.3
        elif keyword_density > 0:
            score += 0.1
        
        # Headings with keyword
        headings = re.findall(r'^#+\s+(.+)$', content, re.MULTILINE)
        heading_with_keyword = sum(1 for h in headings if keyword_lower in h.lower())
        if heading_with_keyword > 0:
            score += 0.2
        
        # Content length
        if 1500 <= word_count <= 3000:
            score += 0.3
        elif word_count >= 1000:
            score += 0.2
        
        # Internal structure
        if content.count('##') >= 5:  # Multiple sections
            score += 0.2
        
        return min(1.0, score)
    
    def _estimate_readability(self, content: str) -> int:
        """Estimate Flesch Reading Ease score (simplified)"""
        sentences = len(re.findall(r'[.!?]+', content))
        words = len(content.split())
        syllables = sum(self._count_syllables(word) for word in content.split())
        
        if sentences == 0 or words == 0:
            return 0
        
        # Simplified Flesch formula
        score = 206.835 - (1.015 * (words / sentences)) - (84.6 * (syllables / words))
        return max(0, min(100, int(score)))
    
    def _count_syllables(self, word: str) -> int:
        """Simple syllable counting for readability estimation"""
        word = word.lower().strip('.,!?;:"')
        vowels = 'aeiouy'
        syllable_count = 0
        prev_was_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not prev_was_vowel:
                syllable_count += 1
            prev_was_vowel = is_vowel
        
        # Handle silent e
        if word.endswith('e') and syllable_count > 1:
            syllable_count -= 1
        
        return max(1, syllable_count)  # At least 1 syllable per word


# Example usage and testing
if __name__ == "__main__":
    generator = AntiAIContentGenerator()
    
    # Test article generation
    test_keywords = [
        ('smart plug alexa', 'smart_plugs'),
        ('color changing smart bulb', 'smart_bulbs')
    ]
    
    for keyword, category in test_keywords:
        print(f"\nGenerating article for: {keyword}")
        print("=" * 50)
        
        article = generator.generate_smart_home_article(
            keyword=keyword,
            category=category,
            article_type='review',
            target_length=2500
        )
        
        print(f"Title: {article['title']}")
        print(f"Word Count: {article['word_count']}")
        print(f"Anti-AI Score: {article['anti_ai_score']:.2f}")
        print(f"SEO Score: {article['metadata']['seo_score']:.2f}")
        print(f"Readability: {article['metadata']['readability_score']}")
        
        # Save sample
        output_file = f"sample_{category}_{datetime.now().strftime('%Y%m%d_%H%M')}.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"# {article['title']}\n\n")
            f.write(article['content'])
        
        print(f"Sample saved to: {output_file}")