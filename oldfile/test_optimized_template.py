#!/usr/bin/env python3
"""
Test script for optimized article generation template
"""
import sys
import os

# Add the scripts directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))

from generate_daily_content import generate_article_content, create_hugo_article

def test_optimized_generation():
    """Test the optimized article generation template"""
    
    # Test with a sample keyword
    keyword = "smart thermostat wifi"
    category = "smart_climate"
    
    print(f"🧪 Testing optimized template with keyword: '{keyword}'")
    print(f"📂 Category: {category}")
    
    try:
        # Generate article content
        article_data = generate_article_content(keyword, category)
        
        # Calculate word count
        word_count = len(article_data['content'].split())
        
        print(f"📊 Generated article statistics:")
        print(f"   - Title: {article_data['title']}")
        print(f"   - Word count: {word_count} words")
        print(f"   - Target: 2500+ words")
        print(f"   - Status: {'✅ PASSED' if word_count >= 2500 else '❌ FAILED'}")
        
        # Check content structure
        content = article_data['content']
        sections = content.count('##')
        paragraphs = content.count('\n\n')
        
        print(f"   - Sections: {sections}")
        print(f"   - Paragraphs: {paragraphs}")
        
        # Save test article
        test_output_dir = "content/test"
        os.makedirs(test_output_dir, exist_ok=True)
        
        test_filename = create_hugo_article(article_data, test_output_dir)
        print(f"✅ Test article saved: {test_filename}")
        
        return word_count >= 2500
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False

if __name__ == "__main__":
    success = test_optimized_generation()
    sys.exit(0 if success else 1)