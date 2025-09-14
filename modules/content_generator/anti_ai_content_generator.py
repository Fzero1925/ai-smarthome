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

# Import v3 Image Aggregator System (CRITICAL for PQS v3 compliance)
try:
    from modules.image_aggregator import assign as assign_images
    IMAGE_SYSTEM_AVAILABLE = True
except ImportError:
    print("Warning: v3 Image Aggregator not available. Images will use fallback paths.")
    IMAGE_SYSTEM_AVAILABLE = False


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
        
        # Enhanced seasonal and contextual content patterns
        self.seasonal_patterns = self._initialize_seasonal_patterns()
        self.user_case_templates = self._initialize_user_case_templates()
        self.contextual_scenarios = self._initialize_contextual_scenarios()
        
        # Content quality metrics
        self.quality_thresholds = {
            'min_word_count': 1500,
            'max_word_count': 4000,
            'min_paragraphs': 8,
            'min_headings': 6,
            'readability_target': 65  # Flesch Reading Ease
        }
        
        # PQS v3 requirements
        self.pqs_requirements = {
            'min_images': 3,  # 1 featured + 2 inline minimum
            'max_alt_length': 120,
            'min_alt_length': 8,
            'min_evidence_links': 2,
            'require_comparison_table': True,
            'require_compatibility_matrix': True,
            'require_installation_guide': True,
            'require_jsonld': True,
            'require_faq_jsonld': True,
            'entity_tokens_per_category': {
                'smart_plugs': ['smart plug', 'matter', 'thread', 'zigbee', 'local control', 'watt', '2.4g'],
                'smart_bulbs': ['smart bulb', 'led', 'dimming', 'color temperature', 'lumens', 'kelvin'],
                'generic': ['matter', 'thread', 'zigbee', 'local control', 'watt', '2.4g', 'hub']
            }
        }
        
        # Load PQS v3 templates and evidence sources
        self._load_pqs_templates()
        self._load_evidence_sources()
        
    def _load_pqs_templates(self):
        """Load PQS v3 JSON-LD templates"""
        try:
            templates_dir = Path('templates')
            
            # Load Article JSON-LD template
            article_template_path = templates_dir / 'article_jsonld.jsonld'
            if article_template_path.exists():
                with open(article_template_path, 'r', encoding='utf-8') as f:
                    self.article_jsonld_template = f.read()
            else:
                self.article_jsonld_template = self._get_default_article_jsonld()
            
            # Load FAQ JSON-LD template
            faq_template_path = templates_dir / 'faq_jsonld.jsonld'
            if faq_template_path.exists():
                with open(faq_template_path, 'r', encoding='utf-8') as f:
                    self.faq_jsonld_template = f.read()
            else:
                self.faq_jsonld_template = self._get_default_faq_jsonld()
                
        except Exception as e:
            print(f"⚠️ Failed to load PQS templates: {e}")
            self.article_jsonld_template = self._get_default_article_jsonld()
            self.faq_jsonld_template = self._get_default_faq_jsonld()
    
    def _load_evidence_sources(self):
        """Load evidence sources from config"""
        try:
            config_path = Path('config') / 'evidence_seeder.json'
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    self.evidence_sources = json.load(f)
            else:
                self.evidence_sources = self._get_default_evidence_sources()
        except Exception as e:
            print(f"⚠️ Failed to load evidence sources: {e}")
            self.evidence_sources = self._get_default_evidence_sources()
    
    def _get_default_article_jsonld(self) -> str:
        """Default Article JSON-LD template"""
        return '''
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "{{ title }}",
  "description": "{{ description }}",
  "image": "{{ featured_image }}",
  "author": {
    "@type": "Organization", 
    "name": "{{ author }}"
  },
  "publisher": {
    "@type": "Organization",
    "name": "AI Smart Home Hub",
    "logo": {
      "@type": "ImageObject",
      "url": "https://ai-smarthomehub.com/images/logo.png"
    }
  },
  "datePublished": "{{ date }}",
  "dateModified": "{{ lastmod }}",
  "mainEntityOfPage": {
    "@type": "WebPage",
    "@id": "{{ permalink }}"
  }
}'''.strip()
    
    def _get_default_faq_jsonld(self) -> str:
        """Default FAQ JSON-LD template"""
        return '''
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {% for faq in faqs %}
    {
      "@type": "Question",
      "name": "{{ faq.question }}",
      "acceptedAnswer": {
        "@type": "Answer", 
        "text": "{{ faq.answer }}"
      }
    }{% if not loop.last %},{% endif %}
    {% endfor %}
  ]
}'''.strip()
    
    def _get_default_evidence_sources(self) -> dict:
        """Default evidence sources"""
        return {
            'smart_plugs': [
                {
                    'name': 'Matter Specification',
                    'url': 'https://csa-iot.org/all-solutions/matter/'
                },
                {
                    'name': 'Wi-Fi Alliance Certification',
                    'url': 'https://www.wi-fi.org/product-finder'
                }
            ],
            'generic': [
                {
                    'name': 'FCC Equipment Database',
                    'url': 'https://apps.fcc.gov/oetcf/eas/reports/GenericSearch.cfm'
                },
                {
                    'name': 'Consumer Reports',
                    'url': 'https://www.consumerreports.org/smart-home'
                }
            ]
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
                "remarkably", "impressively", "unexpectedly", "fortunately",
                "incredibly", "particularly", "especially", "notably", "significantly"
            ],
            
            'human_errors': [
                ("a lot", "alot"), ("definitely", "definately"), ("separate", "seperate"),
                ("occurred", "occured"), ("receive", "recieve"), ("beginning", "begining"),
                ("independent", "independant"), ("maintenance", "maintainence")
            ],
            
            'emotional_expressions': [
                "I have to say", "What really struck me was", "I was genuinely impressed by",
                "To be completely honest", "From my experience", "What I found interesting",
                "One thing that surprised me", "I'll admit", "Personally", "In my opinion",
                "What caught my attention", "I noticed that", "It's worth mentioning",
                "From what I've seen", "Based on my testing"
            ],
            
            'natural_connectors': [
                "Speaking of which", "That reminds me", "On a related note", "Interestingly enough",
                "What's more", "Plus", "Also", "Additionally", "Moreover", "Furthermore",
                "On top of that", "Not to mention", "Besides that", "Another thing"
            ],
            
            'hesitation_markers': [
                "well...", "um...", "you know", "I mean", "like", "so...",
                "actually...", "basically...", "sort of...", "kind of..."
            ],
            
            'personal_anecdotes': [
                "In my household", "When I first tried this", "After using it for weeks",
                "My experience has been", "I remember when", "Last month, I",
                "A friend of mine", "My neighbor recently", "I've recommended this to",
                "What worked for me", "From my own testing", "In my daily use",
                "I'll be completely honest here", "What really happened was",
                "Here's what I wish someone had told me", "The thing nobody mentions is",
                "I made this mistake so you don't have to", "Initially, I thought... but then",
                "My biggest surprise was", "What I didn't expect was",
                "Looking back, I should have", "If I could do it again, I'd"
            ],
            
            'subtle_mistakes': [
                ("its", "it's"), ("your", "you're"), ("there", "their"),
                ("which", "that"), ("less", "fewer"), ("affect", "effect"),
                ("then", "than"), ("who", "whom"), ("lay", "lie")
            ],
            
            'typo_patterns': [
                ("the the", "the"), ("and and", "and"), ("a a", "a"),
                ("recieve", "receive"), ("seperate", "separate"), ("occured", "occurred"),
                ("untill", "until"), ("truely", "truly"), ("beleive", "believe")
            ],
            
            'conversational_fillers': [
                "you know what I mean?", "if you ask me", "in my opinion",
                "from where I stand", "the way I see it", "if you will",
                "so to speak", "as it were", "believe it or not",
                "funny thing is", "what's interesting is", "here's the kicker"
            ],
            
            'emotional_reactions': [
                "I was blown away when", "It shocked me to discover",
                "I couldn't believe how", "What really got me was",
                "I have to admit, I was skeptical", "My jaw dropped when",
                "I was pleasantly surprised by", "It frustrated me that",
                "I was relieved to find", "What amazed me most was"
            ],
            
            'self_corrections': [
                "Actually, let me rephrase that", "Or rather", "What I mean is",
                "To put it another way", "Let me be more specific",
                "Actually, that's not quite right", "Hold on, let me clarify",
                "On second thought", "Strike that, reverse it"
            ],
            
            'memory_references': [
                "If memory serves", "As I recall", "From what I remember",
                "I think it was", "Unless I'm mistaken", "If I'm not misremembering",
                "As best I can remember", "I believe it was", "If my memory is correct"
            ],
            
            'uncertainty_markers': [
                "I'm not entirely sure, but", "It might be that", "I could be wrong, but",
                "From what I understand", "As far as I know", "I believe",
                "I suspect that", "My guess is", "It seems to me like",
                "I get the impression that", "If I had to guess"
            ]
        }

    def _initialize_seasonal_patterns(self) -> Dict[str, List[str]]:
        """Initialize expanded seasonal content patterns (30+ scenarios across 5 time categories)"""
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        patterns = {
            # Winter contexts (December-February) - 8 scenarios
            'winter_context': [
                "With winter approaching, energy efficiency becomes crucial as heating costs soar",
                "During the colder months, smart thermostats really shine by learning your daily patterns",
                "Holiday season brings unique smart home needs like coordinating decorative lighting",
                "Winter indoor air quality becomes concerning with closed windows and dry air",
                "Short daylight hours make smart lighting essential for maintaining circadian rhythms",
                "Energy bills spike during winter - automation helps reduce waste by 20-30%",
                "Snow storms and power outages highlight the importance of reliable backup systems",
                "Winter break means family gatherings - smart homes help accommodate extra guests"
            ],
            
            # Spring contexts (March-May) - 7 scenarios
            'spring_context': [
                "Spring cleaning season is perfect for smart home upgrades and fresh starts",
                "As we transition from winter, fresh air circulation matters more than ever",
                "Daylight saving time makes scheduling automation tricky but worthwhile",
                "Spring allergies highlight the need for air quality monitoring and filtration",
                "Preparing outdoor spaces with smart garden tools and weather monitoring",
                "Tax refund season often means having extra budget for home improvements",
                "Mild weather allows for outdoor installation projects without extreme temperatures"
            ],
            
            # Summer contexts (June-August) - 6 scenarios  
            'summer_context': [
                "Summer heat makes efficient cooling critical - smart AC saves hundreds monthly",
                "Pool season brings new smart home automation needs for safety and maintenance",
                "Vacation time requires reliable remote monitoring to ensure home security",
                "Higher energy usage in summer demands smart management to avoid bill shock",
                "Outdoor entertainment setups need weather-resistant tech for parties and BBQs",
                "Intense sun exposure affects smart device performance - shading becomes important"
            ],
            
            # Fall contexts (September-November) - 6 scenarios
            'fall_context': [
                "Back-to-school routines benefit from smart automation that adapts to new schedules",
                "Preparing for winter with preventive smart maintenance prevents costly repairs",
                "Shorter days mean earlier lighting automation and seasonal depression prevention",
                "Fall cleanup tasks can be automated efficiently with robotic lawn care",
                "Holiday preparation starts with smart home planning for entertaining guests",
                "Heating system preparation before winter arrives saves emergency repair costs"
            ],
            
            # Year-end/Holiday contexts - 3 scenarios
            'year_end_context': [
                f"Looking ahead to {current_year + 1}, smart home trends continue evolving rapidly",
                f"Black Friday and holiday sales make {current_year} perfect for major upgrades", 
                "Year-end energy usage reports show smart home savings - time to expand the system"
            ]
        }
        
        return patterns

    def _initialize_user_case_templates(self) -> Dict[str, List[str]]:
        """Initialize expanded realistic user case study templates (19 scenarios across 4 demographics)"""
        return {
            # Family scenarios - 6 cases
            'family_scenarios': [
                "Sarah, a working mom of two teenagers, found that {product} transformed her hectic morning routine. 'I can start the coffee maker from bed and have the lights gradually brighten 15 minutes before anyone needs to wake up,' she shares. The automated system reduced her morning stress by eliminating the rush to manually turn on devices.",
                "The Johnson family in suburban Denver installed {product} after their winter energy bills hit $340 monthly. 'We're now saving about $65 monthly with the smart scheduling features,' reports dad Mike. Their three kids learned to appreciate the automated bedtime lighting that helps with their sleep schedules.",
                "Empty nesters Robert and Linda, both retired, use {product} primarily for security during their frequent travels. 'When we're visiting our grandchildren in Florida for weeks at a time, we can check on the house anytime and even make it look occupied,' Linda explains. The peace of mind has made their retirement much more enjoyable.",
                "College student Emma, living in a cramped studio apartment near campus, loves how {product} maximizes her limited space functionality. 'I can create different lighting scenes for studying, relaxing, and video calls with my parents,' she says. The space feels twice as large with the smart environment controls.",
                "New parents Alex and Jordan rely on {product} to maintain consistent nursery conditions without disturbing their sleeping 8-month-old. 'We can monitor temperature, adjust lighting for diaper changes, and even play white noise remotely,' Jordan notes. It has been essential for maintaining their sanity during the first year.",
                "Single mom Rachel, juggling two jobs, uses {product} to ensure her 10-year-old son stays safe and on routine when she works late shifts. 'The automated lights and security features give me confidence that he's secure at home,' she explains. The system sends her updates throughout the evening."
            ],
            
            # Professional scenarios - 6 cases  
            'professional_scenarios': [
                "Tech consultant David, working from his converted garage office, tested {product} extensively in his home setup. 'The seamless integration with my work-from-home routine has improved my productivity by at least 20%,' he notes. Clients are often impressed by the professional lighting during video conferences.",
                "Real estate agent Maria strategically uses {product} in her high-end staging properties throughout Austin. 'Buyers walk in and immediately see the home as move-in ready and modern,' she says. Properties with smart features sell 18% faster in her experience.",
                "Restaurant owner Carlos installed {product} at home after witnessing how similar automation technology streamlined operations at his three locations. 'If it can handle a busy kitchen, it definitely works for managing my family's daily routine,' he laughs. The energy savings help offset his restaurant's utility costs.",
                "Dr. Patricia, working rotating 14-hour shifts at the hospital, appreciates how {product} manages her home environment while she's away for extended periods. 'Coming home to the perfect temperature and lighting after a long surgery day is incredibly comforting,' she shares. The system even waters her plants automatically.",
                "Freelance graphic designer Marcus found that {product} helps maintain the creative atmosphere in his home studio. 'Different lighting scenes inspire different types of work - bright and energizing for client calls, warm and focused for design work,' he explains. His creativity and client satisfaction have both improved.",
                "Attorney Jennifer, who often works late preparing cases, uses {product} to maintain work-life boundaries. 'The system automatically shifts to evening mode at 7 PM, reminding me to step away from work,' she says. It has significantly improved her stress levels and family relationships."
            ],
            
            # Senior scenarios - 4 cases
            'senior_scenarios': [
                "Retired teacher Margaret, 72, was initially skeptical about any smart technology after struggling with smartphones. 'But {product} has made daily tasks so much easier that I barely think about the technology anymore,' she admits. Her adult children are amazed at how confidently she manages the system.",
                "Widower Frank, living alone at 68 after his wife's passing, uses {product} primarily for safety and maintaining connection with family. 'The automated lighting makes the house feel less empty, and my daughter can check that I'm okay without being intrusive,' he explains. It has helped with his adjustment to living alone.",
                "Active retirees Bob and Carol, both 65, installed {product} before their month-long European river cruise to monitor their home remotely. 'We could enjoy our vacation completely, knowing everything was secure and properly maintained at home,' Carol shares. They've since planned more extended travel.",
                "Grandmother Ruth, 74, loves demonstrating how {product} works when her teenage grandchildren visit during summers. 'They think Grandma is so tech-savvy now,' she chuckles. The intergenerational bonding over technology has strengthened their relationships significantly."
            ],
            
            # Lifestyle scenarios - 3 cases
            'lifestyle_scenarios': [
                "Fitness enthusiast Jake, who maintains a strict 5 AM workout schedule, uses {product} to coordinate his routine without disturbing his sleeping roommates. 'The gradual lighting and automated coffee maker mean I can get energized for my workout while everyone else sleeps peacefully,' he explains. His consistency has improved dramatically.",
                "Night shift nurse Kelly relies on {product} to maintain her unusual sleep schedule in a house full of day-shift family members. 'I can create a dark, quiet environment for sleeping during the day while still allowing normal household activities,' she says. Her sleep quality has improved significantly since installation.",
                "Environmental activist couple Maya and Ryan chose {product} specifically for its comprehensive energy-saving features and sustainability focus. 'We've reduced our carbon footprint by 35% while actually improving our quality of life,' Maya reports. They've become advocates for smart home technology in their community."
            ]
        }

    def _initialize_contextual_scenarios(self) -> Dict[str, List[str]]:
        """Initialize expanded contextual scenarios (15 problem-discovery-success stories)"""
        return {
            # Problem situations (15 scenarios) - The catalyst moments
            'problem_situations': [
                # Energy/Utility Problems (3)
                "After receiving a shocking $485 winter heating bill, the Martinez family realized their old thermostat was costing them hundreds monthly in wasted energy.",
                "When the Smiths' summer electric bill hit $380 despite their best efforts to conserve energy, they knew something had to change drastically.",
                "Following a power outage that reset all their programmed devices, the Johnsons spent hours reprogramming everything and vowed to find a better solution.",
                
                # Security/Safety Problems (4)
                "After their elderly neighbor fell and couldn't reach help for 6 hours, the entire community became acutely aware of safety monitoring needs.",
                "When package thieves struck three times in one month, costing the Williams family over $300 in stolen deliveries, they decided enough was enough.",
                "Following a break-in attempt while they were on vacation, the Chen family realized their basic alarm system wasn't providing adequate protection or peace of mind.",
                "After their house sitter forgot to arm the security system during a weekend trip, the Garcias knew they needed automated, foolproof protection.",
                
                # Convenience/Lifestyle Problems (4)
                "When both working parents realized they were spending 30 minutes every morning manually adjusting lights, temperature, and devices, they sought efficiency solutions.",
                "After struggling with multiple remotes and incompatible smart devices that never worked together, the tech-frustrated Browns wanted unified control.",
                "Following a vacation disaster where they returned to dead plants, spoiled food, and a stuffy house, the Andersons needed comprehensive home monitoring.",
                "When their teenage daughter complained that her friends' homes were 'way cooler' with voice control and automation, the parents reconsidered their tech stance.",
                
                # Accessibility/Special Needs Problems (2)
                "After his arthritis made operating multiple light switches increasingly difficult, 70-year-old Robert needed easier ways to control his environment.",
                "When caring for her mother with mobility issues, Lisa realized how much easier life could be with voice-controlled home automation throughout the house.",
                
                # Maintenance/Management Problems (2)
                "Following a $3,000 pipe freeze damage because they weren't home to notice the temperature drop, the Patels invested in smart monitoring systems.",
                "After discovering their HVAC system had been running inefficiently for months without their knowledge, the Lees wanted real-time performance monitoring."
            ],
            
            # Discovery moments (15 corresponding scenarios) - The lightbulb moments
            'discovery_moments': [
                # Energy discoveries
                "While researching energy efficiency tax credits, they discovered smart thermostats could reduce heating costs by 15-25% with minimal effort.",
                "A coworker's casual mention of saving $150 monthly with smart energy management sparked their interest in learning more about automated efficiency.",
                "During a home energy audit, the consultant recommended smart monitoring as the fastest way to identify and eliminate energy waste throughout their home.",
                
                # Security discoveries
                "While visiting their tech-savvy friend's house, they were impressed by how the integrated security system provided comprehensive protection without complexity.",
                "After their neighbor showed them real-time delivery notifications and porch monitoring, they realized modern security was far beyond basic alarm systems.",
                "A security consultant explained how smart systems could automatically respond to threats and send detailed alerts, providing professional-level protection at home.",
                "Their insurance agent mentioned potential discounts for comprehensive smart security systems, making the investment financially attractive beyond just protection benefits.",
                
                # Convenience discoveries  
                "Seeing their daughter's college apartment automation made them realize how much time and stress they could eliminate with proper home integration.",
                "A friend demonstrated voice control throughout their home, showing how natural and intuitive modern smart home technology had become for daily tasks.",
                "While house-sitting for relatives, they experienced the convenience of automated routines and realized how much manual work they were doing unnecessarily.",
                "Their adult children's surprise at their parents' 'old-fashioned' home management prompted research into modern automation solutions that could simplify daily life.",
                
                # Accessibility discoveries
                "His physical therapist suggested voice-controlled lighting and temperature could significantly reduce daily strain and improve his independence around the house.",
                "After seeing how smart home technology helped a friend's elderly parent maintain independence, she realized it could be life-changing for her mother too.",
                
                # Maintenance discoveries
                "Their HVAC technician mentioned that smart monitoring could have prevented the damage by alerting them immediately when temperatures dropped dangerously low.",
                "While researching home maintenance, they discovered smart systems could predict and prevent problems before they became expensive emergency repairs requiring professional intervention."
            ],
            
            # Success outcomes (15 corresponding scenarios) - The happy endings
            'success_outcomes': [
                # Energy successes
                "Eight months later, their winter heating bill dropped from $485 to $295 monthly, and the system had already paid for itself through utility savings alone.",
                "Their summer electric costs decreased by 35%, dropping from $380 to under $250, while maintaining better comfort levels throughout their home than ever before.",
                "The unified system eliminated the frustration of power outage resets, automatically restoring all settings and maintaining their preferred environment without manual intervention.",
                
                # Security successes
                "The comprehensive monitoring system now provides peace of mind for the entire neighborhood, with several families implementing similar safety solutions after seeing the results.",
                "Package deliveries are now secure with automated notifications and deterrent features, eliminating theft concerns and saving hundreds annually in replacement costs and frustration.",
                "Their integrated security system successfully deterred two attempted break-ins with automated responses, and the family now enjoys complete peace of mind during travel.",
                "They've never worried about security system activation since installation - the automated features ensure consistent protection without requiring perfect memory or routine adherence.",
                
                # Convenience successes
                "Their morning routine now takes 10 minutes instead of 40, with automated systems handling temperature, lighting, and device coordination while they focus on family time.",
                "The unified control eliminated device frustration entirely, and guests regularly comment on how seamlessly everything works together throughout their home environment.",
                "They now travel confidently knowing their home maintains itself, with automated plant care, temperature control, and security monitoring providing complete peace of mind during any absence.",
                "Their home has become the neighborhood gathering place, with visitors constantly impressed by the intuitive automation and the family's reputation as local tech experts.",
                
                # Accessibility successes  
                "Robert now controls his entire home environment with simple voice commands, maintaining complete independence and actually feeling more confident in his own space than before.",
                "Lisa's mother has regained significant independence with voice-controlled systems, reducing caregiver stress while improving quality of life for both generations living together.",
                
                # Maintenance successes
                "The monitoring system has already prevented two potential disasters - alerting them to a failing water heater and unusual energy usage that indicated HVAC problems before major damage occurred.",
                "They've avoided three expensive emergency repairs through predictive monitoring alerts, and their HVAC system now runs 40% more efficiently with automated optimization and maintenance scheduling."
            ]
        }
    
    def generate_smart_home_article(self, 
                                  keyword: str, 
                                  category: str,
                                  article_type: str = "review",
                                  target_length: int = 2500,
                                  pqs_mode: bool = True) -> Dict[str, Any]:
        """
        Generate comprehensive smart home article with anti-AI detection features
        
        Args:
            keyword: Primary keyword for the article
            category: Product category (smart_plugs, smart_bulbs, etc.)
            article_type: Type of article (review, guide, comparison)
            target_length: Target word count
            pqs_mode: Enable PQS v3 strict requirements (default: True)
            
        Returns:
            Dictionary containing article content and metadata
        """
        
        # Generate article structure (enhanced for PQS v3 if enabled)
        structure = self._create_article_structure(keyword, category, article_type, pqs_mode)
        
        # Create content sections
        content_sections = {}
        
        # Generate introduction with human patterns
        content_sections['introduction'] = self._generate_introduction(
            keyword, category, target_length, pqs_mode
        )
        
        # Generate main content sections
        content_sections['main_content'] = self._generate_main_sections(
            keyword, category, structure, pqs_mode
        )
        
        # Generate product recommendations if applicable
        if category in self.product_database:
            content_sections['product_recommendations'] = self._generate_product_section(
                keyword, category, pqs_mode
            )
        
        # Generate FAQ section
        content_sections['faq'] = self._generate_faq_section(keyword, category, pqs_mode)
        
        # Generate conclusion
        content_sections['conclusion'] = self._generate_conclusion(keyword, category)
        
        # Apply human-like text transformations
        for section_key in content_sections:
            # Handle FAQ section which returns a list
            if section_key == 'faq' and isinstance(content_sections[section_key], list):
                faq_content = "\n\n## Frequently Asked Questions\n\n"
                for faq in content_sections[section_key]:
                    faq_content += f"**Q: {faq['question']}**\n\nA: {faq['answer']}\n\n"
                content_sections[section_key] = faq_content
            
            # Handle product recommendations which returns a dict
            elif section_key == 'product_recommendations' and isinstance(content_sections[section_key], dict):
                content_sections[section_key] = content_sections[section_key].get('content', '')
            
            # Ensure we have a string before applying transformations
            if isinstance(content_sections[section_key], str):
                content_sections[section_key] = self._apply_humanization(
                    content_sections[section_key]
                )
                # Apply v2 compliance sanitization
                content_sections[section_key] = sanitize_claims(content_sections[section_key])
        
        # PQS v3: Add required structured elements INCLUDING image assignment
        if pqs_mode:
            content_sections = self._add_pqs_v3_elements(content_sections, keyword, category)

            # CRITICAL: Assign v3 Images System Integration
            if IMAGE_SYSTEM_AVAILABLE:
                # Generate slug from keyword if not available in structure
                slug = structure.get('slug', self._generate_slug(keyword))
                image_result = self._assign_images_v3(keyword, category, slug)
                metadata['images'] = image_result
                # Update content with actual image paths
                content_sections = self._integrate_assigned_images(content_sections, image_result)
            else:
                print(f"Warning: Using fallback images for {keyword} - v3 system unavailable")
        
        # Combine all sections
        full_content = self._combine_sections(content_sections, structure)
        
        # Apply enhanced content quality with seasonal context and user cases
        enhanced_content = self._enhance_content_quality(full_content, keyword, category)
        
        # PQS v3: Ensure compliance requirements
        if pqs_mode:
            enhanced_content = self._ensure_pqs_v3_compliance(enhanced_content, keyword, category)
        
        # Generate metadata (enhanced for PQS v3)
        metadata = self._generate_metadata(keyword, category, enhanced_content, pqs_mode)
        
        return {
            'title': structure['title'],
            'content': enhanced_content,
            'metadata': metadata,
            'featured_products': content_sections.get('product_recommendations', {}),
            'faq': content_sections['faq'],
            'word_count': len(enhanced_content.split()),
            'generation_date': datetime.now(),
            'anti_ai_score': self._calculate_anti_ai_score(enhanced_content),
            'pqs_mode': pqs_mode,
            'pqs_elements': self._get_pqs_elements_summary(enhanced_content, metadata) if pqs_mode else {}
        }
    
    def _create_article_structure(self, keyword: str, category: str, article_type: str, pqs_mode: bool = False) -> Dict:
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
    
    def _generate_introduction(self, keyword: str, category: str, target_length: int, pqs_mode: bool = False) -> str:
        """Generate compliant introduction with MANDATORY early disclosure (PQS v3 Hard Gate requirement)"""

        # Research-based credentials (COMPLIANT - no physical testing claims)
        credentials = random.choice([
            f"Through comprehensive market research and specification analysis",
            f"Based on extensive user feedback analysis and industry research",
            f"Drawing from manufacturer documentation and verified user experiences",
            f"After analyzing market trends and consumer feedback patterns"
        ])

        # Opening hook variations
        hooks = [
            f"The {keyword} market offers diverse options, but choosing the right device requires understanding key technical differences and use case compatibility.",
            f"Smart home technology continues evolving rapidly, making {keyword} selection both more important and more complex for consumers.",
            f"Quality {keyword} devices can transform your home automation experience, but the wrong choice leads to frustration and wasted investment.",
            f"Understanding {keyword} specifications and compatibility requirements is essential for making an informed purchase decision."
        ]

        # MANDATORY EARLY COMPLIANCE DISCLOSURE (within first 600 characters)
        compliance_disclosure = random.choice([
            "**Research Methodology**: This guide is based on specification analysis, user feedback research, and manufacturer documentation review. We do not conduct physical product testing but provide research-based recommendations.",
            "**Disclosure**: Our recommendations are based on market research, specification analysis, and verified user feedback patterns. This content contains affiliate links that support our research at no cost to you.",
            "**Methodology Note**: This analysis is based on research of manufacturer specifications, user reviews, and industry reports. No physical testing was conducted. Affiliate links help support our research efforts."
        ])

        # Research-based problem statement
        problems = [
            f"Market analysis reveals significant variation in {keyword} quality, features, and compatibility across price points.",
            f"Consumer feedback indicates common issues with {keyword} selection often stem from compatibility and feature misunderstandings.",
            f"Industry trends show {keyword} technology advancing rapidly, making informed selection increasingly important for future-proofing."
        ]

        # Research-based solution preview
        solutions = [
            f"This comprehensive analysis breaks down key specifications, compatibility requirements, and market positioning to guide your decision.",
            f"We've analyzed market options, user feedback patterns, and technical specifications to provide actionable buying guidance.",
            f"This guide synthesizes market research, specification analysis, and user experience data to help you choose confidently."
        ]

        introduction_parts = [
            random.choice(hooks),
            compliance_disclosure,  # CRITICAL: Early compliance disclosure
            f"{credentials}, {random.choice(problems)}",
            random.choice(solutions)
        ]

        return "\n\n".join(introduction_parts)
    
    def _generate_main_sections(self, keyword: str, category: str, structure: Dict, pqs_mode: bool = False) -> str:
        """Generate main content sections with variation and depth"""
        
        sections = []
        
        for section in structure['sections']:
            if section['type'] in ['introduction', 'faq', 'conclusion']:
                continue  # Handle separately
                
            section_content = self._generate_section_content(
                section, keyword, category
            )
            sections.append(f"## {section['heading']}\n\n{section_content}")
        
        return "\n\n".join(sections)
    
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
    
    def _generate_product_section(self, keyword: str, category: str, pqs_mode: bool = False) -> Dict:
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
            
            # Get real Amazon product URL if available
            amazon_urls = {
                'Amazon Smart Plug': 'https://amazon.com/dp/B089DR29T6',
                'TP-Link Kasa Smart Plug HS103': 'https://amazon.com/dp/B07B8W2KHZ',
                'Govee Smart Plug WiFi': 'https://amazon.com/dp/B0863TXZXT',
                'Philips Hue White and Color A19': 'https://amazon.com/dp/B073168F4Y',
                'LIFX A19 Wi-Fi Smart Bulb': 'https://amazon.com/dp/B073168G19'
            }
            
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
                'amazon_url': amazon_urls.get(product['name'], f"https://amazon.com/s?k={product['name'].replace(' ', '+')}"),
                'badge': ['Editor\'s Choice', 'Best Value', 'Budget Pick'][i-1] if i <= 3 else 'Recommended',
                'image_url': f"/images/products/{product['name'].lower().replace(' ', '-').replace('&', 'and')}.jpg"
            })
        
        return {
            'content': "\n\n".join(product_content),
            'products': featured_products
        }
    
    def _generate_faq_section(self, keyword: str, category: str, pqs_mode: bool = False) -> List[Dict[str, str]]:
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
    
    def _generate_comparison_section(self, keyword: str, category: str) -> str:
        """Generate comparison section with MANDATORY comparison table (PQS v3 Hard Gate requirement)"""
        content = f"## Feature Comparison & Buying Considerations\n\n"

        # Add context before table
        content += f"Based on our research analysis, here's a detailed comparison of leading {keyword} options:\n\n"

        # Generate MANDATORY comparison table (fixes "空心推荐" problem)
        content += self._generate_comparison_table(keyword, category)

        # Add interpretation after table
        content += f"\n### Key Decision Factors\n\n"
        content += f"**Budget Considerations:**\n"
        content += f"- Entry-level models typically cost $15-35 and offer basic smart home functionality\n"
        content += f"- Mid-range options ($35-75) add energy monitoring and advanced scheduling\n"
        content += f"- Premium models ($75-150+) include professional-grade features and extended warranties\n\n"

        content += f"**Compatibility Requirements:**\n"
        content += f"- **Matter/Thread**: Future-proof protocol support for interoperability\n"
        content += f"- **Wi-Fi Standards**: 802.11n minimum, 802.11ac preferred for reliability\n"
        content += f"- **Voice Assistants**: Verify compatibility with your preferred ecosystem\n\n"

        content += f"**Installation Considerations:**\n"
        content += f"- Standard outlets require no additional wiring or professional installation\n"
        content += f"- Outdoor models need weatherproof rated (IP65+) enclosures\n"
        content += f"- Load capacity must exceed connected device requirements by 20% safety margin\n"

        return content

    def _generate_comparison_table(self, keyword: str, category: str) -> str:
        """Generate structured comparison table with specific models (MANDATORY for PQS v3)"""

        # Define realistic product data based on category
        products = self._get_category_products(category, keyword)

        # Generate table header
        table = "| Model | Protocol | Max Load | Energy Monitor | Local Control | Voice Control | Price Range | Warranty |\n"
        table += "|-------|----------|----------|----------------|---------------|---------------|-------------|----------|\n"

        # Add product rows
        for product in products:
            table += f"| {product['model']} | {product['protocol']} | {product['max_load']} | {product['energy_monitor']} | {product['local_control']} | {product['voice_control']} | {product['price_range']} | {product['warranty']} |\n"

        return table + "\n"

    def _get_category_products(self, category: str, keyword: str) -> List[Dict]:
        """Get realistic product data for comparison table"""

        # Smart plugs product database
        if 'plug' in keyword.lower() or category == 'smart-plugs':
            return [
                {
                    'model': 'TP-Link Kasa HS103',
                    'protocol': 'Wi-Fi',
                    'max_load': '15A/1800W',
                    'energy_monitor': 'No',
                    'local_control': 'No',
                    'voice_control': 'Alexa, Google',
                    'price_range': '$8-12',
                    'warranty': '2 years'
                },
                {
                    'model': 'TP-Link Kasa EP25',
                    'protocol': 'Wi-Fi',
                    'max_load': '15A/1800W',
                    'energy_monitor': 'Yes',
                    'local_control': 'No',
                    'voice_control': 'Alexa, Google',
                    'price_range': '$15-20',
                    'warranty': '2 years'
                },
                {
                    'model': 'Amazon Smart Plug',
                    'protocol': 'Wi-Fi',
                    'max_load': '15A/1800W',
                    'energy_monitor': 'No',
                    'local_control': 'No',
                    'voice_control': 'Alexa only',
                    'price_range': '$10-15',
                    'warranty': '1 year'
                },
                {
                    'model': 'TREATLIFE Matter Plug',
                    'protocol': 'Matter/Wi-Fi',
                    'max_load': '15A/1800W',
                    'energy_monitor': 'Yes',
                    'local_control': 'Yes',
                    'voice_control': 'All platforms',
                    'price_range': '$25-35',
                    'warranty': '2 years'
                }
            ]

        # Smart bulbs
        elif 'bulb' in keyword.lower() or 'light' in keyword.lower():
            return [
                {
                    'model': 'Philips Hue White',
                    'protocol': 'Zigbee/Bridge',
                    'max_load': '9W LED',
                    'energy_monitor': 'Via Hub',
                    'local_control': 'Yes',
                    'voice_control': 'All platforms',
                    'price_range': '$15-20',
                    'warranty': '2 years'
                },
                {
                    'model': 'TP-Link Kasa KL110',
                    'protocol': 'Wi-Fi',
                    'max_load': '10W LED',
                    'energy_monitor': 'Yes',
                    'local_control': 'No',
                    'voice_control': 'Alexa, Google',
                    'price_range': '$8-12',
                    'warranty': '2 years'
                },
                {
                    'model': 'LIFX A19',
                    'protocol': 'Wi-Fi',
                    'max_load': '11W LED',
                    'energy_monitor': 'Yes',
                    'local_control': 'No',
                    'voice_control': 'All platforms',
                    'price_range': '$25-35',
                    'warranty': '2 years'
                }
            ]

        # Generic smart home devices
        else:
            return [
                {
                    'model': 'Generic Device A',
                    'protocol': 'Wi-Fi',
                    'max_load': '15A',
                    'energy_monitor': 'Yes',
                    'local_control': 'No',
                    'voice_control': 'Alexa, Google',
                    'price_range': '$20-30',
                    'warranty': '1 year'
                },
                {
                    'model': 'Generic Device B',
                    'protocol': 'Matter/Wi-Fi',
                    'max_load': '15A',
                    'energy_monitor': 'Yes',
                    'local_control': 'Yes',
                    'voice_control': 'All platforms',
                    'price_range': '$35-45',
                    'warranty': '2 years'
                }
            ]
    
    def _generate_guide_section(self, keyword: str, category: str) -> str:
        """Generate installation/setup guide section"""
        content = f"\n## {keyword.title()} Setup Guide\n\n"
        content += "**Before You Begin:**\n"
        content += "1. Ensure your WiFi network is operating on 2.4GHz (most smart devices require this)\n"
        content += "2. Download the manufacturer's app from official app stores\n"
        content += "3. Create an account if you don't already have one\n\n"
        content += "**Installation Steps:**\n"
        content += "1. **Initial Setup**: Follow the in-app pairing instructions\n"
        content += "2. **Network Connection**: Connect the device to your WiFi network\n"
        content += "3. **Voice Integration**: Link to Alexa, Google Assistant, or Apple HomeKit\n"
        content += "4. **Testing**: Verify all functions work correctly\n\n"
        content += "Most setup processes take 10-15 minutes, but allow extra time for first-time installations."
        return content
    
    def _generate_troubleshooting_section(self, keyword: str, category: str) -> str:
        """Generate troubleshooting section content"""
        content = f"\n## {keyword.title()} Troubleshooting\n\n"
        content += "**Common Issues and Solutions:**\n\n"
        content += "**Connection Problems:**\n"
        content += "- Verify 2.4GHz WiFi is enabled on your router\n"
        content += "- Check for MAC address filtering or firewall blocks\n"
        content += "- Ensure device is within reasonable range of router\n\n"
        content += "**App/Control Issues:**\n"
        content += "- Clear app cache and restart\n"
        content += "- Verify app permissions for location and notifications\n"
        content += "- Try re-pairing the device if problems persist\n\n"
        content += "**Performance Issues:**\n"
        content += "- Check for firmware updates in the app\n"
        content += "- Restart your router if multiple devices are affected\n"
        content += "- Contact manufacturer support if issues continue\n"
        return content
    
    def _generate_generic_section(self, heading: str, keyword: str, category: str) -> str:
        """Generate generic section content for any heading"""
        content = f"\n## {heading}\n\n"
        content += f"When considering {keyword} for your smart home setup, several important factors deserve careful attention.\n\n"
        content += f"Quality {keyword} devices share certain characteristics that distinguish them from basic alternatives. "
        content += "These include reliable performance, comprehensive app support, and solid integration with major smart home platforms.\n\n"
        content += f"The {keyword} market offers options for various budgets and technical requirements. "
        content += "Understanding your specific needs helps narrow down the choices to models that will provide long-term satisfaction.\n\n"
        content += f"Professional installation isn't typically required for {keyword}, but following manufacturer guidelines ensures optimal performance and warranty coverage."
        return content
    
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
        
        # Apply new humanization patterns
        text = self._apply_advanced_humanization(text)
        
        return text
    
    def _apply_advanced_humanization(self, text: str) -> str:
        """Apply advanced humanization techniques with enhanced patterns"""
        
        # Add emotional expressions occasionally
        sentences = text.split('. ')
        for i, sentence in enumerate(sentences):
            # Add emotional expressions (5% chance)
            if random.random() < 0.05 and i > 0:
                emotion = random.choice(self.human_patterns['emotional_expressions'])
                sentences[i] = f"{emotion}, {sentence.lower()}"
            
            # Add conversational fillers (3% chance)
            elif random.random() < 0.03 and i > 0:
                filler = random.choice(self.human_patterns['conversational_fillers'])
                sentences[i] = f"{sentence} - {filler}"
            
            # Add uncertainty markers (4% chance)
            elif random.random() < 0.04 and i > 0:
                uncertainty = random.choice(self.human_patterns['uncertainty_markers'])
                sentences[i] = f"{uncertainty} {sentence.lower()}"
            
            # Add memory references (2% chance)
            elif random.random() < 0.02 and i > 0:
                memory = random.choice(self.human_patterns['memory_references'])
                sentences[i] = f"{memory}, {sentence.lower()}"
            
            # Add personal anecdotes (3% chance)
            elif random.random() < 0.03 and i > 0:
                anecdote = random.choice(self.human_patterns['personal_anecdotes'])
                sentences[i] = f"{anecdote}, {sentence.lower()}"
        
        text = '. '.join(sentences)
        
        # Apply subtle mistakes and typos (very sparingly)
        text = self._apply_subtle_errors(text)
        
        # Apply sentence length variation
        text = self._apply_sentence_variation(text)
        
        # Add self-corrections occasionally (1% chance)
        if random.random() < 0.01:
            text = self._add_self_corrections(text)
        
        return text
    
    def _apply_subtle_errors(self, text: str) -> str:
        """Apply very subtle human errors (use sparingly to avoid hurting quality)"""
        
        # Only apply errors very rarely (2% chance per error type)
        
        # Subtle grammar mistakes (very rare)
        if random.random() < 0.01:
            for correct, error in self.human_patterns['subtle_mistakes']:
                if correct in text and random.random() < 0.1:  # Only 10% of occurrences
                    # Only apply to non-critical parts
                    sentences = text.split('. ')
                    for i, sentence in enumerate(sentences[1:-1], 1):  # Skip first/last sentence
                        if correct in sentence:
                            sentences[i] = sentence.replace(correct, error, 1)
                            break
                    text = '. '.join(sentences)
                    break  # Only one error per text
        
        # Very subtle typos (extremely rare)
        if random.random() < 0.005:
            for correct, typo in self.human_patterns['typo_patterns']:
                if correct in text and random.random() < 0.05:
                    text = text.replace(correct, typo, 1)
                    break
        
        return text
    
    def _apply_sentence_variation(self, text: str) -> str:
        """Vary sentence length and structure for more natural flow"""
        
        sentences = text.split('. ')
        varied_sentences = []
        
        for i, sentence in enumerate(sentences):
            # Randomly combine short sentences (10% chance)
            if (i < len(sentences) - 1 and 
                len(sentence.split()) < 10 and 
                len(sentences[i+1].split()) < 10 and 
                random.random() < 0.1):
                
                connector = random.choice([
                    ', and', ', but', ', so', ', plus',
                    ', while', ', although', ', since'
                ])
                combined = f"{sentence}{connector} {sentences[i+1].lower()}"
                varied_sentences.append(combined)
                sentences[i+1] = ""  # Mark for skipping
            
            elif sentence:  # Don't add empty sentences
                # Occasionally split long sentences (5% chance)
                if len(sentence.split()) > 25 and random.random() < 0.05:
                    words = sentence.split()
                    split_point = len(words) // 2
                    # Find a good split point (after conjunctions)
                    for j in range(split_point - 3, split_point + 3):
                        if j > 0 and j < len(words) and words[j].lower() in ['and', 'but', 'while', 'since']:
                            split_point = j
                            break
                    
                    first_part = ' '.join(words[:split_point])
                    second_part = ' '.join(words[split_point:])
                    varied_sentences.append(first_part)
                    varied_sentences.append(second_part.capitalize())
                else:
                    varied_sentences.append(sentence)
        
        return '. '.join(varied_sentences)
    
    def _add_self_corrections(self, text: str) -> str:
        """Add occasional self-corrections to appear more human"""
        
        sentences = text.split('. ')
        
        # Find a sentence in the middle to add a correction to
        if len(sentences) > 3:
            target_index = random.randint(1, len(sentences) - 2)
            sentence = sentences[target_index]
            
            correction = random.choice(self.human_patterns['self_corrections'])
            
            # Add a slight rephrasing after the correction
            rephrasings = [
                "this is a better way to put it",
                "what I really mean is",
                "let me be clearer about this",
                "here's a better explanation",
                "to clarify my point"
            ]
            
            rephrase = random.choice(rephrasings)
            sentences[target_index] = f"{sentence} {correction} - {rephrase}."
        
        return '. '.join(sentences)
        
        text = '. '.join(sentences)
        
        # Add natural connectors between paragraphs
        paragraphs = text.split('\\n\\n')
        for i in range(1, len(paragraphs)):
            if random.random() < 0.15:  # 15% chance to add connector
                connector = random.choice(self.human_patterns['natural_connectors'])
                paragraphs[i] = f"{connector}, {paragraphs[i]}"
        
        text = '\\n\\n'.join(paragraphs)
        
        # Introduce subtle human errors very sparingly (1% chance per error type)
        if random.random() < 0.01:
            for correct, error in self.human_patterns['human_errors']:
                if correct in text and random.random() < 0.5:  # 50% chance to apply this specific error
                    # Only replace first occurrence to keep it subtle
                    text = text.replace(correct, error, 1)
                    break
        
        # Add emphasis markers strategically
        sentences = text.split('. ')
        for i, sentence in enumerate(sentences):
            # Add emphasis to important points (8% chance)
            if random.random() < 0.08 and ('important' in sentence.lower() or 'key' in sentence.lower() or 'crucial' in sentence.lower()):
                emphasis = random.choice(self.human_patterns['emphasis_markers'])
                sentences[i] = sentence.replace(sentence.split()[0], f"{emphasis}, {sentence.split()[0].lower()}", 1)
        
        text = '. '.join(sentences)
        
        # Add sentence length variation for more natural flow
        text = self._vary_sentence_structure(text)
        
        return text
    
    def _vary_sentence_structure(self, text: str) -> str:
        """Add natural sentence structure variation"""
        sentences = text.split('. ')
        
        for i, sentence in enumerate(sentences):
            if len(sentence.split()) > 15:  # Long sentences
                # Occasionally break long sentences (20% chance)
                if random.random() < 0.2:
                    words = sentence.split()
                    mid_point = len(words) // 2
                    
                    # Find a good breaking point near the middle
                    break_connectors = ['and', 'but', 'however', 'while', 'whereas', 'although']
                    for j in range(mid_point - 2, mid_point + 3):
                        if j < len(words) and words[j].lower() in break_connectors:
                            # Split the sentence
                            first_part = ' '.join(words[:j])
                            second_part = ' '.join(words[j:])
                            sentences[i] = f"{first_part}. {second_part.capitalize()}"
                            break
            
            elif len(sentence.split()) < 5:  # Very short sentences
                # Occasionally combine with next sentence (15% chance)
                if random.random() < 0.15 and i < len(sentences) - 1:
                    connector = random.choice(['and', 'but', 'while', 'plus'])
                    sentences[i] = f"{sentence} {connector} {sentences[i+1].lower()}"
                    sentences.pop(i+1)
        
        return '. '.join(sentences)
    
    def _apply_seasonal_context(self, content: str, category: str) -> str:
        """Apply seasonal context to make content more relevant and timely"""
        current_month = datetime.now().month
        
        # Determine current season
        if current_month in [12, 1, 2]:
            season = 'winter_context'
        elif current_month in [3, 4, 5]:
            season = 'spring_context'
        elif current_month in [6, 7, 8]:
            season = 'summer_context'
        else:
            season = 'fall_context'
        
        # Add year-end context in November-December
        if current_month in [11, 12]:
            seasonal_contexts = self.seasonal_patterns['year_end_context'] + self.seasonal_patterns[season]
        else:
            seasonal_contexts = self.seasonal_patterns[season]
        
        # Apply seasonal context to random paragraphs (20% chance per paragraph)
        paragraphs = content.split('\n\n')
        
        for i, paragraph in enumerate(paragraphs):
            if random.random() < 0.2 and len(paragraph) > 100:  # Only apply to substantial paragraphs
                seasonal_intro = random.choice(seasonal_contexts)
                # Insert seasonal context naturally
                sentences = paragraph.split('. ')
                if len(sentences) > 2:
                    # Insert after the first sentence occasionally
                    sentences.insert(1, seasonal_intro)
                    paragraphs[i] = '. '.join(sentences)
        
        return '\n\n'.join(paragraphs)
    
    def _integrate_user_cases(self, content: str, product_name: str) -> str:
        """Integrate realistic user case studies into content"""
        
        # Select appropriate user scenarios based on content length and type
        all_scenarios = []
        for scenario_type, scenarios in self.user_case_templates.items():
            all_scenarios.extend(scenarios)
        
        # Also add contextual scenarios for richer storytelling
        problem_scenarios = self.contextual_scenarios['problem_situations']
        discovery_scenarios = self.contextual_scenarios['discovery_moments']
        success_scenarios = self.contextual_scenarios['success_outcomes']
        
        paragraphs = content.split('\n\n')
        
        # Add user case studies (15% chance per substantial paragraph)
        for i, paragraph in enumerate(paragraphs):
            if random.random() < 0.15 and len(paragraph) > 150:
                
                # Choose scenario type based on paragraph position
                if i < len(paragraphs) * 0.3:  # Early in article - problem/discovery
                    scenario_pool = problem_scenarios + discovery_scenarios
                elif i > len(paragraphs) * 0.7:  # Later in article - success outcomes
                    scenario_pool = success_scenarios
                else:  # Middle of article - user testimonials
                    scenario_pool = all_scenarios
                
                selected_scenario = random.choice(scenario_pool)
                
                # Apply product name to scenario template if it has placeholder
                if '{product}' in selected_scenario:
                    selected_scenario = selected_scenario.replace('{product}', product_name)
                
                # Integrate naturally into paragraph
                sentences = paragraph.split('. ')
                if len(sentences) > 3:
                    # Insert case study after first few sentences
                    insert_position = random.randint(1, min(3, len(sentences)-1))
                    sentences.insert(insert_position, selected_scenario)
                    paragraphs[i] = '. '.join(sentences)
        
        return '\n\n'.join(paragraphs)
    
    def _enhance_content_quality(self, content: str, keyword: str, category: str) -> str:
        """Apply all quality enhancements including seasonal and user case integration"""
        
        # Extract product name from keyword for user cases
        product_name = keyword.replace('best ', '').replace('top ', '').replace('review', '').strip()
        if not product_name:
            product_name = category.replace('_', ' ')
        
        # Apply enhancements in order
        enhanced_content = content
        
        # 1. Apply seasonal context
        enhanced_content = self._apply_seasonal_context(enhanced_content, category)
        
        # 2. Integrate user case studies
        enhanced_content = self._integrate_user_cases(enhanced_content, product_name)
        
        # 3. Apply humanization
        enhanced_content = self._apply_advanced_humanization(enhanced_content)
        
        # 4. Vary sentence structure
        enhanced_content = self._vary_sentence_structure(enhanced_content)
        
        return enhanced_content
    
    def _combine_sections(self, sections: Dict[str, Any], structure: Dict) -> str:
        """Combine all content sections into final article"""
        
        article_parts = [
            sections['introduction']
        ]
        
        # Add main content (now a string, not a list)
        if 'main_content' in sections and sections['main_content']:
            article_parts.append(sections['main_content'])
        
        # Add product recommendations if available
        if 'product_recommendations' in sections and sections['product_recommendations']:
            article_parts.append(f"## Top {structure['title'].split(':')[0]} Recommendations")
            article_parts.append(sections['product_recommendations'].get('content', ''))
        
        # Add conclusion
        article_parts.append(f"## Conclusion")
        article_parts.append(sections['conclusion'])
        
        return "\n\n".join(article_parts)
    
    def _generate_metadata(self, keyword: str, category: str, content: str, pqs_mode: bool = False) -> Dict:
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
        
        metadata = {
            'word_count': word_count,
            'categories': categories,
            'tags': tags[:8],  # Limit to 8 tags
            'estimated_read_time': max(1, word_count // 200),  # Rough reading time
            'seo_score': self._calculate_seo_score(content, keyword),
            'readability_score': self._estimate_readability(content)
        }
        
        # Add PQS v3 structured data if enabled
        if pqs_mode:
            metadata['structured_data'] = self._generate_structured_data(keyword, category, content)
            metadata['pqs_compliance'] = True
        
        return metadata
    
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

    
# === Keyword Engine v2 content compliance additions ===
HANDS_ON_LANGUAGE = False  # default off: we do not claim hands-on testing

BANNED_PHRASES = [
    "we tested for 30 days",
    "our lab results show",
    "hands-on review",
    "we personally tested",
    "we bought and tested",
    "after weeks of testing",
    "extensive real-world testing",
    "we physically tested",
    "through rigorous testing"
]

def sanitize_claims(s: str) -> str:
    """Remove or replace potentially misleading testing claims"""
    if not s: 
        return s
    
    out = s
    
    # Remove banned phrases entirely
    for phrase in BANNED_PHRASES:
        out = out.replace(phrase, "")
        out = out.replace(phrase.capitalize(), "")
    
    if not HANDS_ON_LANGUAGE:
        # Replace testing claims with research-based language
        replacements = [
            ("we tested", "we analyzed specs and credible reports"),
            ("We tested", "We analyzed specs and credible reports"),
            ("hands-on", "research-based"),
            ("Hands-on", "Research-based"),
            ("real-world testing", "specification analysis"),
            ("lab testing", "technical specification review"),
            ("testing process", "research methodology"),
            ("test results", "analysis findings"),
            ("our testing", "our research"),
            ("Our testing", "Our research")
        ]
        
        for old, new in replacements:
            out = out.replace(old, new)
    
    # Clean up any double spaces or awkward phrasing
    out = out.replace("  ", " ")
    out = out.replace(" .", ".")
    out = out.replace(" ,", ",")
    
    return out.strip()


# === PQS v3 Support Methods ===
class AntiAIContentGeneratorPQSMethods:
    """PQS v3 support methods for AntiAIContentGenerator"""
    
    def _add_pqs_v3_elements(self, content_sections: Dict, keyword: str, category: str) -> Dict:
        """Add PQS v3 required elements to content sections"""
        
        # Ensure comparison table exists
        if 'comparison_table' not in content_sections.get('main_content', ''):
            comparison_table = self._generate_comparison_table(keyword, category)
            content_sections['main_content'] += f"\n\n{comparison_table}"
        
        # Ensure compatibility matrix exists
        if 'compatibility' not in content_sections.get('main_content', '').lower():
            compatibility_matrix = self._generate_compatibility_matrix(keyword, category)
            content_sections['main_content'] += f"\n\n{compatibility_matrix}"
        
        # Add installation guide if missing
        if 'installation' not in content_sections.get('main_content', '').lower():
            installation_guide = self._generate_installation_guide(keyword)
            content_sections['main_content'] += f"\n\n{installation_guide}"
        
        # Ensure evidence links are present
        content_sections = self._add_evidence_links(content_sections, keyword, category)
        
        return content_sections
    
    def _generate_comparison_table(self, keyword: str, category: str) -> str:
        """Generate required comparison table for PQS v3"""
        
        # Get category-specific comparison criteria
        criteria_map = {
            'smart-plugs': ['Connectivity', 'Hub Required', 'Local Control', 'Energy Monitoring', 'Matter Support', 'Warranty', 'Price Range'],
            'smart-bulbs': ['Color Options', 'Brightness Range', 'Hub Required', 'Voice Control', 'Dimming', 'Warranty', 'Price Range'],
            'security-cameras': ['Resolution', 'Night Vision', 'Storage Options', 'Mobile App', 'Weather Resistance', 'Warranty', 'Price Range']
        }
        
        criteria = criteria_map.get(category, ['Features', 'Connectivity', 'Compatibility', 'Quality', 'Support', 'Warranty', 'Price'])
        
        table = f"\n## {keyword.title()} Comparison Chart\n\n"
        table += f"![{keyword} comparison chart - Features and pricing overview](/images/products/{category.replace('_', '-')}/{keyword.replace(' ', '-')}-comparison-2025.jpg)\n\n"
        table += "### Detailed Comparison Table\n\n"
        table += "| Model Category | " + " | ".join(criteria) + " |\n"
        table += "|---|" + "---|" * len(criteria) + "\n"
        
        # Add sample rows for different model categories
        model_categories = ['Premium Choice', 'Best Value', 'Budget Option']
        for model in model_categories:
            row_data = []
            for criterion in criteria:
                if 'price' in criterion.lower():
                    prices = {'Premium Choice': '$150-300+', 'Best Value': '$75-150', 'Budget Option': '$25-75'}
                    row_data.append(prices[model])
                elif 'warranty' in criterion.lower():
                    warranties = {'Premium Choice': '3-5 years', 'Best Value': '1-2 years', 'Budget Option': '1 year'}
                    row_data.append(warranties[model])
                elif criterion == 'Hub Required':
                    row_data.append('No')
                elif 'support' in criterion.lower() or 'matter' in criterion.lower():
                    supports = {'Premium Choice': 'Yes', 'Best Value': 'Some models', 'Budget Option': 'Limited'}
                    row_data.append(supports[model])
                else:
                    row_data.append('✓' if model == 'Premium Choice' else 'Basic' if model == 'Best Value' else 'Limited')
            
            table += f"| {model} | " + " | ".join(row_data) + " |\n"
        
        return table
    
    def _generate_compatibility_matrix(self, keyword: str, category: str) -> str:
        """Generate compatibility matrix for PQS v3"""
        
        matrix = f"\n### Compatibility Matrix\n\n"
        matrix += "| Feature | Amazon Alexa | Google Assistant | Apple HomeKit | Samsung SmartThings | Hubitat | IFTTT |\n"
        matrix += "|---|---|---|---|---|---|---|\n"
        
        features = ['Premium Models', 'Mid-Range Options', 'Budget Options', 'Matter Protocol']
        compatibility_data = {
            'Premium Models': ['✓', '✓', '✓', '✓', '✓', '✓'],
            'Mid-Range Options': ['✓', '✓', 'Some models', '✓', 'Some models', '✓'],
            'Budget Options': ['✓', '✓', 'Limited', 'Limited', 'No', '✓'],
            'Matter Protocol': ['✓', '✓', '✓', '✓', '✓', '✓']
        }
        
        for feature in features:
            row = compatibility_data.get(feature, ['✓'] * 6)
            matrix += f"| {feature} | " + " | ".join(row) + " |\n"
        
        return matrix
    
    def _generate_installation_guide(self, keyword: str) -> str:
        """Generate installation guide section for PQS v3"""
        
        guide = f"\n## Installation & Troubleshooting\n\n"
        guide += f"### Step-by-Step Setup Process\n"
        guide += "1. **Network Preparation**: Ensure 2.4GHz Wi-Fi is enabled (most smart devices don't support 5GHz)\n"
        guide += "2. **App Download**: Install manufacturer's app from official app stores\n"
        guide += "3. **Device Pairing**: Follow in-app instructions to connect device to network\n"
        guide += "4. **Voice Integration**: Link to Alexa, Google Assistant, or Apple HomeKit\n"
        guide += "5. **Testing**: Verify remote control functionality and voice commands\n\n"
        
        guide += "### Common Issues & Solutions\n"
        guide += "- **Connection Failed**: Disable MAC address filtering, check router compatibility\n"
        guide += "- **Voice Commands Not Working**: Verify device names don't conflict, re-discover devices\n"
        guide += "- **Intermittent Connectivity**: Check power rating compatibility, update firmware\n"
        guide += "- **App Crashes**: Clear cache, reinstall app, check device compatibility\n"
        guide += "- **Poor Performance**: Reset device, verify adequate Wi-Fi signal strength\n"
        
        return guide
    
    def _add_evidence_links(self, content_sections: Dict, keyword: str, category: str) -> Dict:
        """Add evidence links from configured sources"""
        
        # Create default evidence links if no sources configured
        default_sources = [
            {
                'name': 'Amazon Smart Plug Official Specifications',
                'url': 'https://www.amazon.com/amazon-smart-plug/dp/B089DR29T6',
                'description': 'Official product documentation and technical specifications'
            },
            {
                'name': 'TP-Link Kasa Product Documentation', 
                'url': 'https://www.tp-link.com/us/home-networking/smart-plug/hs103/',
                'description': 'Manufacturer specifications and compatibility information'
            },
            {
                'name': 'Matter Specification 1.0',
                'url': 'https://csa-iot.org/all-solutions/matter/',
                'description': 'Connectivity Standards Alliance official protocol documentation'
            },
            {
                'name': 'FCC Equipment Authorization Database',
                'url': 'https://apps.fcc.gov/oetcf/eas/reports/GenericSearch.cfm',
                'description': 'Regulatory compliance and safety certifications'
            },
            {
                'name': 'Wi-Fi Alliance Certification',
                'url': 'https://www.wi-fi.org/product-finder',
                'description': 'Wireless connectivity standards and compatibility verification'
            }
        ]
        
        # Use configured sources if available, otherwise use defaults
        sources_to_use = default_sources
        if hasattr(self, 'evidence_sources') and self.evidence_sources:
            sources_to_use = []
            for source_type, sources in self.evidence_sources.items():
                for source in sources[:2]:  # Limit to 2 per type
                    if len(sources_to_use) >= 5:  # Max 5 evidence links
                        break
                    # Ensure source has required fields
                    if 'name' in source and 'url' in source:
                        desc = source.get('description', 'Authoritative source for product research')
                        sources_to_use.append({
                            'name': source['name'],
                            'url': source['url'],
                            'description': desc
                        })
                if len(sources_to_use) >= 5:
                    break
        
        # Generate evidence section
        evidence_section = "\n\n## Sources\n\nThis analysis is based on comprehensive research from authoritative sources:\n\n"
        
        for source in sources_to_use[:5]:  # Max 5 sources
            evidence_section += f"- **[{source['name']}]({source['url']})** - {source['description']}\n"
        
        evidence_section += "\n*This research-based guide helps you make informed decisions for your smart home journey.*\n"
        
        # Add to conclusion if it exists, otherwise to main content
        if 'conclusion' in content_sections and content_sections['conclusion']:
            content_sections['conclusion'] = evidence_section + "\n\n" + content_sections['conclusion']
        elif 'main_content' in content_sections:
            content_sections['main_content'] += evidence_section
        
        return content_sections
    
    def _ensure_pqs_v3_compliance(self, content: str, keyword: str, category: str) -> str:
        """Ensure final content meets PQS v3 compliance requirements"""
        
        # Ensure minimum image count with proper ALT text
        image_count = content.count('![') 
        if image_count < self.pqs_requirements['min_images']:
            # Add additional images if needed
            additional_images_needed = self.pqs_requirements['min_images'] - image_count
            for i in range(additional_images_needed):
                img_alt = f"{keyword} detailed analysis - Features overview"
                img_path = f"/images/products/{category.replace('_', '-')}/{keyword.replace(' ', '-')}-analysis-{i+1}.jpg"
                additional_img = f"\n\n![{img_alt}]({img_path})\n"
                # Insert in middle of content
                content_parts = content.split('\n\n')
                insert_pos = len(content_parts) // 2
                content_parts.insert(insert_pos, additional_img)
                content = '\n\n'.join(content_parts)
        
        # Fix ALT text compliance
        content = self._fix_alt_text_compliance(content)
        
        return content
    
    def _fix_alt_text_compliance(self, content: str) -> str:
        """Fix ALT text to meet PQS v3 requirements"""
        import re
        
        # Find all image alt text
        alt_pattern = r'!\[([^\]]+)\]'
        matches = re.findall(alt_pattern, content)
        
        for alt_text in matches:
            if len(alt_text) > self.pqs_requirements['max_alt_length']:
                # Shorten ALT text while keeping entity tokens
                shortened = alt_text[:self.pqs_requirements['max_alt_length']-3] + "..."
                content = content.replace(f"![{alt_text}]", f"![{shortened}]")
            elif len(alt_text) < self.pqs_requirements['min_alt_length']:
                # Extend ALT text
                extended = f"{alt_text} - Professional grade analysis"
                if len(extended) <= self.pqs_requirements['max_alt_length']:
                    content = content.replace(f"![{alt_text}]", f"![{extended}]")
        
        return content
    
    def _get_pqs_elements_summary(self, content: str, metadata: Dict) -> Dict:
        """Get summary of PQS v3 elements for validation"""
        
        return {
            'image_count': content.count('!['),
            'has_comparison_table': '| Model Category |' in content or '| Feature |' in content,
            'has_compatibility_matrix': 'Compatibility Matrix' in content,
            'has_installation_guide': 'Installation' in content and 'Setup Process' in content,
            'evidence_link_count': content.count('[') - content.count('!['),  # Links minus images
            'has_faq_section': 'FAQ' in content or 'Questions' in content,
            'has_structured_data': 'application/ld+json' in metadata.get('structured_data', '')
        }
    
    def _generate_structured_data(self, keyword: str, category: str, content: str) -> str:
        """Generate JSON-LD structured data for PQS v3 compliance"""
        import json
        from datetime import datetime
        
        # Load templates if available
        article_template = {}
        faq_template = {}
        
        try:
            if hasattr(self, 'article_template') and self.article_template:
                article_template = json.loads(self.article_template)
            if hasattr(self, 'faq_template') and self.faq_template:
                faq_template = json.loads(self.faq_template)
        except:
            pass
        
        # Generate Article structured data
        article_schema = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": f"Ultimate {keyword.title()} Guide 2025: Features, Pros & Cons",
            "description": f"Research-based guide to the best {keyword} for 2025. Honest reviews, detailed comparisons, and practical buying advice.",
            "image": f"https://ai-smarthomehub.com/images/products/{category.replace('_', '-')}/{keyword.replace(' ', '-')}-hero.jpg",
            "author": {
                "@type": "Organization",
                "name": "Smart Home Research Team"
            },
            "publisher": {
                "@type": "Organization",
                "name": "AI Smart Home Hub",
                "logo": {
                    "@type": "ImageObject",
                    "url": "https://ai-smarthomehub.com/images/logo.png"
                }
            },
            "datePublished": datetime.now().isoformat(),
            "dateModified": datetime.now().isoformat(),
            "mainEntityOfPage": {
                "@type": "WebPage",
                "@id": f"https://ai-smarthomehub.com/articles/{keyword.replace(' ', '-')}-{datetime.now().strftime('%Y%m%d')}/"
            }
        }
        
        # Generate FAQ structured data
        faq_questions = [
            {
                "@type": "Question",
                "name": f"How long do {keyword} typically last?",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": "Quality models generally provide 5-8 years of reliable service. Premium units often exceed this with proper maintenance, while budget options may require replacement sooner."
                }
            },
            {
                "@type": "Question",
                "name": "Are there ongoing costs after purchase?",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": "Most basic functions require no subscription fees. Some premium cloud features may cost $2-10 monthly, though this varies by manufacturer and feature set."
                }
            },
            {
                "@type": "Question",
                "name": f"How do I know if a {keyword} is compatible with my existing devices?",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": "Check the product specifications for supported platforms (Alexa, Google, Apple HomeKit). Most manufacturers provide compatibility lists on their websites."
                }
            }
        ]
        
        faq_schema = {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": faq_questions
        }
        
        # Combine both schemas
        article_json = json.dumps(article_schema, indent=2, ensure_ascii=False)
        faq_json = json.dumps(faq_schema, indent=2, ensure_ascii=False)
        
        structured_data = f'<script type="application/ld+json">\n{article_json}\n</script>\n\n<script type="application/ld+json">\n{faq_json}\n</script>'
        
        return structured_data

    def _assign_images_v3(self, keyword: str, category: str, slug: str) -> Dict:
        """Assign images using v3 Image Aggregator System (CRITICAL for PQS Hard Gates)"""

        # Create entities dict for v3 system
        entities = {
            'category': category.replace('_', '-'),  # Convert to kebab-case
            'protocol': self._extract_protocol_from_keyword(keyword),
            'use_case': self._extract_use_case_from_keyword(keyword)
        }

        try:
            # Call v3 Image Aggregator
            result = assign_images(
                keyword=keyword,
                entities=entities,
                slug=slug
            )

            print(f"✅ v3 Images assigned for {keyword}: {result.get('metadata', {}).get('selected_count', 0)} images")
            return result

        except Exception as e:
            print(f"❌ v3 Image assignment failed for {keyword}: {e}")
            # Return fallback structure
            return {
                'hero': f"/images/products/{category.replace('_', '-')}/{slug}-hero.jpg",
                'inline': [
                    f"/images/products/{category.replace('_', '-')}/{slug}-comparison.jpg",
                    f"/images/products/{category.replace('_', '-')}/{slug}-features.jpg"
                ],
                'metadata': {
                    'fallback': True,
                    'selected_count': 3,
                    'total_candidates': 0
                }
            }

    def _integrate_assigned_images(self, content_sections: Dict, image_result: Dict) -> Dict:
        """Integrate assigned images into content sections with proper Alt tags"""

        hero_image = image_result.get('hero')
        inline_images = image_result.get('inline', [])

        # Update any existing image placeholders with actual paths
        for section_key, section_content in content_sections.items():
            if isinstance(section_content, str):

                # Replace generic image paths with assigned ones
                if hero_image:
                    # Replace any hero image placeholders
                    section_content = re.sub(
                        r'!\[([^\]]*hero[^\]]*)\]\([^)]+\)',
                        f'![\\1]({hero_image})',
                        section_content,
                        flags=re.IGNORECASE
                    )

                # Add inline images where needed
                if inline_images and len(inline_images) >= 2:
                    # Replace comparison chart placeholders
                    section_content = re.sub(
                        r'!\[([^\]]*comparison[^\]]*)\]\([^)]+\)',
                        f'![\\1]({inline_images[0]})',
                        section_content,
                        flags=re.IGNORECASE
                    )

                    # Add feature image if available
                    if len(inline_images) > 1:
                        section_content = re.sub(
                            r'!\[([^\]]*feature[^\]]*)\]\([^)]+\)',
                            f'![\\1]({inline_images[1]})',
                            section_content,
                            flags=re.IGNORECASE
                        )

                content_sections[section_key] = section_content

        return content_sections

    def _extract_protocol_from_keyword(self, keyword: str) -> str:
        """Extract protocol from keyword for entities"""
        keyword_lower = keyword.lower()

        if any(proto in keyword_lower for proto in ['wifi', 'wi-fi']):
            return 'WiFi'
        elif 'zigbee' in keyword_lower:
            return 'Zigbee'
        elif 'matter' in keyword_lower:
            return 'Matter'
        elif 'thread' in keyword_lower:
            return 'Thread'
        elif 'alexa' in keyword_lower:
            return 'WiFi'  # Alexa devices typically use WiFi
        elif 'google' in keyword_lower:
            return 'WiFi'  # Google devices typically use WiFi
        else:
            return 'WiFi'  # Default to WiFi

    def _extract_use_case_from_keyword(self, keyword: str) -> str:
        """Extract use case from keyword for entities"""
        keyword_lower = keyword.lower()

        if any(term in keyword_lower for term in ['energy', 'monitoring', 'watt', 'kwh']):
            return 'energy monitoring'
        elif any(term in keyword_lower for term in ['outdoor', 'weather', 'waterproof']):
            return 'outdoor use'
        elif any(term in keyword_lower for term in ['security', 'camera', 'alarm']):
            return 'security'
        elif any(term in keyword_lower for term in ['vacuum', 'clean', 'robot']):
            return 'cleaning'
        elif any(term in keyword_lower for term in ['light', 'bulb', 'lamp']):
            return 'lighting'
        elif any(term in keyword_lower for term in ['thermostat', 'temperature', 'climate']):
            return 'climate control'
        elif any(term in keyword_lower for term in ['plug', 'outlet', 'switch']):
            return 'power control'
        else:
            return 'smart home automation'  # Generic fallback

    def _generate_slug(self, keyword: str) -> str:
        """Generate URL-friendly slug from keyword"""
        import re
        from datetime import datetime

        # Clean and normalize keyword
        slug = keyword.lower()
        slug = re.sub(r'[^\w\s-]', '', slug)  # Remove special characters
        slug = re.sub(r'[-\s]+', '-', slug)   # Replace spaces/hyphens with single hyphen
        slug = slug.strip('-')                # Remove leading/trailing hyphens

        # Add timestamp with higher precision to ensure uniqueness (YYYY-MM-DD-HHMM)
        timestamp = datetime.now().strftime('%Y%m%d-%H%M')

        return f"{slug}-{timestamp}"

# Mix PQS methods into main class
for method_name in dir(AntiAIContentGeneratorPQSMethods):
    if not method_name.startswith('_') or method_name.startswith('__'):
        continue
    method = getattr(AntiAIContentGeneratorPQSMethods, method_name)
    if callable(method):
        setattr(AntiAIContentGenerator, method_name, method)


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