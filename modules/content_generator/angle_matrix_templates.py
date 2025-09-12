#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Content Angle Matrix Templates
Four comprehensive content angles for smart home product coverage

Based on Growth Kit v3 specifications:
- Buyers Guide: Purchase decision support
- Compatibility: Technical integration focus  
- Comparison: Side-by-side product analysis
- Installation: Setup and configuration guide
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
import json


@dataclass
class ContentTemplate:
    """Template structure for content generation"""
    angle: str
    sections: List[str]
    required_entities: List[str]
    word_count_target: int
    seo_focus: List[str]
    call_to_action: str


class AngleMatrixTemplates:
    """Four content angle templates for comprehensive coverage"""
    
    def __init__(self):
        """Initialize with predefined angle templates"""
        self.templates = {
            'buyers_guide': self._create_buyers_guide_template(),
            'compatibility': self._create_compatibility_template(),
            'comparison': self._create_comparison_template(), 
            'installation': self._create_installation_template()
        }
    
    def _create_buyers_guide_template(self) -> ContentTemplate:
        """Buyers Guide: Purchase decision support"""
        return ContentTemplate(
            angle='buyers_guide',
            sections=[
                'introduction',
                'what_to_look_for',
                'top_recommendations',
                'price_analysis',
                'where_to_buy',
                'buying_checklist',
                'faq',
                'conclusion'
            ],
            required_entities=[
                'category', 'product_type', 'price_range',
                'key_features', 'brand_options', 'use_case'
            ],
            word_count_target=2800,
            seo_focus=[
                'best [product] 2025',
                '[product] buying guide',
                'how to choose [product]',
                '[product] reviews',
                'top [product] recommendations'
            ],
            call_to_action='Check Current Prices and Reviews'
        )
    
    def _create_compatibility_template(self) -> ContentTemplate:
        """Compatibility: Technical integration focus"""
        return ContentTemplate(
            angle='compatibility',
            sections=[
                'introduction',
                'protocol_overview',
                'ecosystem_integration',
                'device_requirements',
                'setup_process',
                'troubleshooting',
                'compatibility_matrix',
                'faq',
                'conclusion'
            ],
            required_entities=[
                'category', 'product_type', 'protocol',
                'ecosystem', 'requirements', 'compatibility'
            ],
            word_count_target=2600,
            seo_focus=[
                '[product] compatibility',
                '[product] works with [ecosystem]',
                '[product] setup guide',
                '[protocol] [product]',
                '[product] integration'
            ],
            call_to_action='View Compatible Products'
        )
    
    def _create_comparison_template(self) -> ContentTemplate:
        """Comparison: Side-by-side product analysis"""
        return ContentTemplate(
            angle='comparison',
            sections=[
                'introduction',
                'comparison_overview',
                'feature_matrix',
                'performance_analysis',
                'pros_and_cons',
                'value_assessment',
                'use_case_recommendations',
                'faq',
                'conclusion'
            ],
            required_entities=[
                'category', 'product_type', 'competing_products',
                'key_features', 'price_comparison', 'performance_metrics'
            ],
            word_count_target=3000,
            seo_focus=[
                '[product A] vs [product B]',
                '[product] comparison',
                'best [product] comparison',
                '[product] differences',
                '[product] which is better'
            ],
            call_to_action='Compare Products and Prices'
        )
    
    def _create_installation_template(self) -> ContentTemplate:
        """Installation: Setup and configuration guide"""
        return ContentTemplate(
            angle='installation',
            sections=[
                'introduction',
                'prerequisites',
                'unboxing_checklist',
                'step_by_step_installation',
                'configuration_guide',
                'testing_verification',
                'troubleshooting',
                'safety_considerations',
                'faq',
                'conclusion'
            ],
            required_entities=[
                'category', 'product_type', 'installation_type',
                'requirements', 'tools_needed', 'difficulty_level'
            ],
            word_count_target=2700,
            seo_focus=[
                'how to install [product]',
                '[product] installation guide',
                '[product] setup',
                '[product] configuration',
                '[product] installation steps'
            ],
            call_to_action='Get Installation Support'
        )
    
    def get_template(self, angle: str) -> Optional[ContentTemplate]:
        """Get specific content angle template"""
        return self.templates.get(angle)
    
    def get_all_templates(self) -> Dict[str, ContentTemplate]:
        """Get all available templates"""
        return self.templates.copy()
    
    def generate_content_outline(self, angle: str, entities: Dict) -> Dict:
        """
        Generate detailed content outline for specific angle
        
        Args:
            angle: Content angle (buyers_guide, compatibility, etc.)
            entities: Product/content entities
            
        Returns:
            Detailed content outline with sections and requirements
        """
        template = self.get_template(angle)
        if not template:
            raise ValueError(f"Unknown content angle: {angle}")
            
        # Check entity coverage
        missing_entities = []
        for required_entity in template.required_entities:
            if required_entity not in entities or not entities[required_entity]:
                missing_entities.append(required_entity)
        
        # Generate section outlines
        section_outlines = self._generate_section_outlines(template, entities)
        
        # Create SEO-optimized title suggestions
        title_suggestions = self._generate_title_suggestions(template, entities)
        
        return {
            'angle': angle,
            'template': template,
            'entities_coverage': {
                'required': template.required_entities,
                'provided': list(entities.keys()),
                'missing': missing_entities,
                'coverage_ratio': (len(template.required_entities) - len(missing_entities)) / len(template.required_entities)
            },
            'content_outline': {
                'sections': section_outlines,
                'estimated_word_count': template.word_count_target,
                'target_sections': len(template.sections)
            },
            'seo_optimization': {
                'focus_keywords': template.seo_focus,
                'title_suggestions': title_suggestions,
                'call_to_action': template.call_to_action
            },
            'quality_requirements': {
                'min_sections': len(template.sections),
                'target_words': template.word_count_target,
                'required_entities': template.required_entities
            }
        }
    
    def _generate_section_outlines(self, template: ContentTemplate, entities: Dict) -> List[Dict]:
        """Generate detailed outlines for each section"""
        section_outlines = []
        
        for section in template.sections:
            outline = self._create_section_outline(section, template.angle, entities)
            section_outlines.append(outline)
            
        return section_outlines
    
    def _create_section_outline(self, section: str, angle: str, entities: Dict) -> Dict:
        """Create detailed outline for a specific section"""
        product_type = entities.get('product_type', 'smart device')
        category = entities.get('category', 'smart home')
        
        # Section-specific outline templates
        outlines = {
            'introduction': {
                'heading': f"# {product_type.title()} {angle.replace('_', ' ').title()}",
                'key_points': [
                    f"Overview of {product_type} market and trends",
                    f"Why this {angle.replace('_', ' ')} matters for consumers",
                    f"What you'll learn from this comprehensive analysis"
                ],
                'word_target': 200
            },
            'what_to_look_for': {
                'heading': "## Key Features to Consider",
                'key_points': [
                    "Essential technical specifications",
                    "Performance and reliability factors",
                    "Value-added features that matter"
                ],
                'word_target': 350
            },
            'top_recommendations': {
                'heading': f"## Best {product_type.title()}s in 2025",
                'key_points': [
                    "Premium choice with justification",
                    "Best value option analysis",
                    "Budget-friendly alternative"
                ],
                'word_target': 500
            },
            'compatibility_matrix': {
                'heading': "## Compatibility Overview",
                'key_points': [
                    "Smart home ecosystem support",
                    "Protocol compatibility chart",
                    "Integration requirements"
                ],
                'word_target': 400
            },
            'feature_matrix': {
                'heading': "## Feature Comparison Chart",
                'key_points': [
                    "Side-by-side feature comparison",
                    "Performance metrics analysis",
                    "Value proposition assessment"
                ],
                'word_target': 450
            },
            'step_by_step_installation': {
                'heading': f"## How to Install {product_type.title()}",
                'key_points': [
                    "Pre-installation preparation",
                    "Detailed installation steps",
                    "Post-installation verification"
                ],
                'word_target': 600
            },
            'faq': {
                'heading': "## Frequently Asked Questions",
                'key_points': [
                    "Common technical questions",
                    "Troubleshooting guidance",
                    "Best practice recommendations"
                ],
                'word_target': 300
            },
            'conclusion': {
                'heading': "## Final Recommendations",
                'key_points': [
                    "Summary of key insights",
                    "Final product recommendations",
                    "Next steps for readers"
                ],
                'word_target': 250
            }
        }
        
        # Return section outline or generic template
        return outlines.get(section, {
            'heading': f"## {section.replace('_', ' ').title()}",
            'key_points': [f"{section.replace('_', ' ').title()} content"],
            'word_target': 300
        })
    
    def _generate_title_suggestions(self, template: ContentTemplate, entities: Dict) -> List[str]:
        """Generate SEO-optimized title suggestions"""
        product_type = entities.get('product_type', 'Smart Device')
        category = entities.get('category', 'Smart Home')
        year = "2025"
        
        angle_titles = {
            'buyers_guide': [
                f"Best {product_type} {year}: Complete Buying Guide & Reviews",
                f"{product_type} Buying Guide: Top Picks for {year}",
                f"How to Choose the Perfect {product_type} in {year}",
                f"{year} {product_type} Guide: Features, Prices & Reviews"
            ],
            'compatibility': [
                f"{product_type} Compatibility: Works With Which Systems?",
                f"Complete {product_type} Compatibility Guide {year}",
                f"{product_type} Integration: Ecosystems & Setup Guide",
                f"Which {product_type} Works With Your Smart Home?"
            ],
            'comparison': [
                f"{product_type} Comparison: Top Models Analyzed {year}",
                f"Best {product_type} Comparison: Features vs Price",
                f"{product_type} Showdown: Which Model Wins in {year}?",
                f"{year} {product_type} Comparison: Performance & Value"
            ],
            'installation': [
                f"How to Install {product_type}: Complete Setup Guide",
                f"{product_type} Installation: Step-by-Step Tutorial",
                f"DIY {product_type} Installation Guide for {year}",
                f"{product_type} Setup: Installation & Configuration"
            ]
        }
        
        return angle_titles.get(template.angle, [f"{product_type} Guide {year}"])
    
    def suggest_next_angle(self, completed_angles: List[str], entities: Dict) -> Optional[str]:
        """Suggest next content angle to create for comprehensive coverage"""
        all_angles = list(self.templates.keys())
        remaining_angles = [angle for angle in all_angles if angle not in completed_angles]
        
        if not remaining_angles:
            return None
            
        # Priority order based on content strategy
        priority_order = ['buyers_guide', 'comparison', 'compatibility', 'installation']
        
        for angle in priority_order:
            if angle in remaining_angles:
                return angle
                
        return remaining_angles[0]  # Fallback to first remaining
    
    def validate_angle_coverage(self, entities: Dict, target_angles: List[str] = None) -> Dict:
        """Validate entity coverage for target content angles"""
        target_angles = target_angles or list(self.templates.keys())
        
        coverage_report = {}
        overall_readiness = {}
        
        for angle in target_angles:
            template = self.templates[angle]
            
            # Check entity coverage
            missing_entities = []
            for required_entity in template.required_entities:
                if required_entity not in entities or not entities[required_entity]:
                    missing_entities.append(required_entity)
            
            coverage_ratio = (len(template.required_entities) - len(missing_entities)) / len(template.required_entities)
            
            coverage_report[angle] = {
                'required_entities': template.required_entities,
                'missing_entities': missing_entities,
                'coverage_ratio': coverage_ratio,
                'ready': coverage_ratio >= 0.8  # 80% entity coverage required
            }
            
            overall_readiness[angle] = coverage_ratio >= 0.8
        
        return {
            'angle_coverage': coverage_report,
            'overall_readiness': overall_readiness,
            'ready_angles': [angle for angle, ready in overall_readiness.items() if ready],
            'missing_data_angles': [angle for angle, ready in overall_readiness.items() if not ready]
        }


# Factory functions for easy import
def create_angle_templates() -> AngleMatrixTemplates:
    """Create angle matrix templates instance"""
    return AngleMatrixTemplates()


def get_content_outline(angle: str, entities: Dict) -> Dict:
    """Quick access to content outline generation"""
    templates = AngleMatrixTemplates()
    return templates.generate_content_outline(angle, entities)


if __name__ == "__main__":
    # Test the angle matrix templates
    templates = AngleMatrixTemplates()
    
    # Sample entities
    test_entities = {
        'category': 'smart_plugs',
        'product_type': 'WiFi smart plug',
        'protocol': 'WiFi',
        'price_range': '$15-50',
        'key_features': 'energy monitoring, voice control',
        'use_case': 'home automation',
        'brand_options': 'TP-Link, Amazon, Wyze'
    }
    
    print("=== Angle Matrix Templates Test ===")
    
    # Test each angle
    for angle in templates.get_all_templates().keys():
        print(f"\\n--- {angle.upper().replace('_', ' ')} ---")
        
        try:
            outline = templates.generate_content_outline(angle, test_entities)
            print(f"Coverage: {outline['entities_coverage']['coverage_ratio']:.2f}")
            print(f"Sections: {len(outline['content_outline']['sections'])}")
            print(f"Target words: {outline['content_outline']['estimated_word_count']}")
            print(f"Title example: {outline['seo_optimization']['title_suggestions'][0]}")
        except Exception as e:
            print(f"Error: {e}")
    
    # Test validation
    print("\\n=== Coverage Validation ===")
    validation = templates.validate_angle_coverage(test_entities)
    print(f"Ready angles: {validation['ready_angles']}")
    print(f"Missing data: {validation['missing_data_angles']}")