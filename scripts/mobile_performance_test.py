#!/usr/bin/env python3
"""
Mobile Performance Testing and Core Web Vitals Analysis
Tests mobile page performance and generates optimization recommendations
"""

import requests
import time
import json
from urllib.parse import urljoin
from typing import Dict, List

class MobilePerformanceTest:
    """Mobile performance testing and analysis"""
    
    def __init__(self, base_url: str = "https://ai-smarthomehub.com"):
        self.base_url = base_url
        self.results = {}
        
    def test_page_load_time(self, page_path: str = "/") -> Dict:
        """Test page load time and basic metrics"""
        url = urljoin(self.base_url, page_path)
        
        # Simulate mobile user agent
        headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1'
        }
        
        try:
            start_time = time.time()
            response = requests.get(url, headers=headers, timeout=10)
            end_time = time.time()
            
            load_time = (end_time - start_time) * 1000  # Convert to milliseconds
            
            return {
                'url': url,
                'status_code': response.status_code,
                'load_time_ms': round(load_time, 2),
                'content_length': len(response.content),
                'has_mobile_viewport': 'viewport' in response.text.lower(),
                'has_webp_images': '.webp' in response.text,
                'has_lazy_loading': 'loading="lazy"' in response.text,
                'response_size_kb': round(len(response.content) / 1024, 2)
            }
            
        except Exception as e:
            return {
                'url': url,
                'error': str(e),
                'load_time_ms': None
            }
    
    def analyze_mobile_optimization(self, content: str) -> Dict:
        """Analyze mobile optimization features"""
        optimizations = {
            'viewport_meta': 'viewport' in content and 'width=device-width' in content,
            'mobile_css': '@media' in content and 'max-width' in content,
            'webp_support': '.webp' in content,
            'lazy_loading': 'loading="lazy"' in content,
            'dns_prefetch': 'dns-prefetch' in content,
            'preconnect': 'preconnect' in content,
            'minified_css': content.count('\n') < content.count(';'),  # Rough check
            'touch_friendly': 'touch-action' in content or 'pointer-events' in content,
        }
        
        score = sum(optimizations.values()) / len(optimizations) * 100
        
        return {
            'optimization_score': round(score, 1),
            'optimizations': optimizations,
            'recommendations': self._generate_mobile_recommendations(optimizations)
        }
    
    def _generate_mobile_recommendations(self, optimizations: Dict) -> List[str]:
        """Generate mobile optimization recommendations"""
        recommendations = []
        
        if not optimizations['viewport_meta']:
            recommendations.append("Add proper viewport meta tag for mobile responsiveness")
            
        if not optimizations['mobile_css']:
            recommendations.append("Implement responsive CSS with media queries")
            
        if not optimizations['webp_support']:
            recommendations.append("Use WebP image format for better compression")
            
        if not optimizations['lazy_loading']:
            recommendations.append("Implement lazy loading for images")
            
        if not optimizations['dns_prefetch']:
            recommendations.append("Add DNS prefetch for external resources")
            
        if not optimizations['preconnect']:
            recommendations.append("Use preconnect for critical third-party resources")
            
        if not optimizations['touch_friendly']:
            recommendations.append("Optimize touch interactions and tap targets")
            
        return recommendations
    
    def test_core_web_vitals_simulation(self, page_path: str = "/") -> Dict:
        """Simulate Core Web Vitals testing"""
        load_result = self.test_page_load_time(page_path)
        
        if 'error' in load_result:
            return load_result
            
        # Simulate Core Web Vitals metrics based on load time and content
        load_time = load_result['load_time_ms']
        content_size = load_result['response_size_kb']
        
        # Estimate LCP (Largest Contentful Paint)
        estimated_lcp = load_time + (content_size * 0.5)  # Rough estimation
        
        # Estimate CLS (Cumulative Layout Shift) - based on optimization features  
        cls_score = 0.1 if load_result['has_mobile_viewport'] else 0.3
        
        # Estimate FID (First Input Delay) - based on content size
        estimated_fid = min(100, content_size * 0.2)
        
        # Grade the metrics
        lcp_grade = 'Good' if estimated_lcp <= 2500 else 'Needs Improvement' if estimated_lcp <= 4000 else 'Poor'
        fid_grade = 'Good' if estimated_fid <= 100 else 'Needs Improvement' if estimated_fid <= 300 else 'Poor'
        cls_grade = 'Good' if cls_score <= 0.1 else 'Needs Improvement' if cls_score <= 0.25 else 'Poor'
        
        return {
            'core_web_vitals': {
                'lcp': {
                    'value_ms': round(estimated_lcp, 1),
                    'grade': lcp_grade,
                    'threshold_good': 2500
                },
                'fid': {
                    'value_ms': round(estimated_fid, 1),
                    'grade': fid_grade,
                    'threshold_good': 100
                },
                'cls': {
                    'value': round(cls_score, 3),
                    'grade': cls_grade,
                    'threshold_good': 0.1
                }
            },
            'overall_grade': self._calculate_overall_grade([lcp_grade, fid_grade, cls_grade])
        }
    
    def _calculate_overall_grade(self, grades: List[str]) -> str:
        """Calculate overall grade from individual metrics"""
        good_count = grades.count('Good')
        if good_count == 3:
            return 'Good'
        elif good_count >= 2:
            return 'Needs Improvement'
        else:
            return 'Poor'
    
    def run_comprehensive_test(self, pages: List[str] = None) -> Dict:
        """Run comprehensive mobile performance test"""
        if pages is None:
            pages = ['/', '/articles/', '/guides/']
            
        results = {
            'test_timestamp': time.time(),
            'base_url': self.base_url,
            'pages_tested': [],
            'overall_summary': {}
        }
        
        total_load_time = 0
        total_optimization_score = 0
        all_grades = []
        
        for page in pages:
            print(f"Testing page: {page}")
            
            # Basic load test
            load_result = self.test_page_load_time(page)
            
            # Core Web Vitals simulation
            cwv_result = self.test_core_web_vitals_simulation(page)
            
            # Mobile optimization analysis
            if 'error' not in load_result:
                # Get page content for analysis
                headers = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X)'}
                try:
                    response = requests.get(urljoin(self.base_url, page), headers=headers)
                    mobile_analysis = self.analyze_mobile_optimization(response.text)
                except:
                    mobile_analysis = {'optimization_score': 0, 'optimizations': {}, 'recommendations': []}
            else:
                mobile_analysis = {'optimization_score': 0, 'optimizations': {}, 'recommendations': []}
            
            page_result = {
                'page': page,
                'load_performance': load_result,
                'core_web_vitals': cwv_result,
                'mobile_optimization': mobile_analysis
            }
            
            results['pages_tested'].append(page_result)
            
            # Accumulate for summary
            if 'error' not in load_result:
                total_load_time += load_result['load_time_ms']
                total_optimization_score += mobile_analysis['optimization_score']
                if 'overall_grade' in cwv_result:
                    all_grades.append(cwv_result['overall_grade'])
        
        # Calculate overall summary
        tested_pages = len([r for r in results['pages_tested'] if 'error' not in r['load_performance']])
        if tested_pages > 0:
            results['overall_summary'] = {
                'average_load_time_ms': round(total_load_time / tested_pages, 1),
                'average_optimization_score': round(total_optimization_score / tested_pages, 1),
                'overall_cwv_grade': self._calculate_overall_grade(all_grades),
                'pages_tested_successfully': tested_pages,
                'pages_with_errors': len(pages) - tested_pages
            }
        
        return results

def main():
    """Run mobile performance test"""
    print("[MOBILE TEST] Starting Mobile Performance Test for AI Smart Home Hub")
    print("=" * 60)
    
    tester = MobilePerformanceTest()
    results = tester.run_comprehensive_test()
    
    print("\n[RESULTS] Test Results Summary:")
    print("-" * 40)
    
    summary = results['overall_summary']
    print(f"Average Load Time: {summary['average_load_time_ms']}ms")
    print(f"Mobile Optimization Score: {summary['average_optimization_score']}/100")
    print(f"Core Web Vitals Grade: {summary['overall_cwv_grade']}")
    print(f"Pages Tested Successfully: {summary['pages_tested_successfully']}")
    
    print("\n[PAGES] Page-by-Page Results:")
    print("-" * 40)
    
    for page_result in results['pages_tested']:
        page = page_result['page']
        load_perf = page_result['load_performance']
        mobile_opt = page_result['mobile_optimization']
        
        print(f"\nPage: {page}")
        if 'error' not in load_perf:
            print(f"  Load Time: {load_perf['load_time_ms']}ms")
            print(f"  Optimization Score: {mobile_opt['optimization_score']}/100")
            if page_result['core_web_vitals'].get('overall_grade'):
                print(f"  CWV Grade: {page_result['core_web_vitals']['overall_grade']}")
        else:
            print(f"  Error: {load_perf['error']}")
    
    print("\n[RECOMMENDATIONS] Optimization Recommendations:")
    print("-" * 40)
    all_recommendations = set()
    for page_result in results['pages_tested']:
        recs = page_result['mobile_optimization'].get('recommendations', [])
        all_recommendations.update(recs)
    
    for i, rec in enumerate(sorted(all_recommendations), 1):
        print(f"{i}. {rec}")
    
    # Save detailed results
    try:
        with open('mobile_performance_results.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\n[SAVED] Detailed results saved to: mobile_performance_results.json")
    except Exception as e:
        print(f"\n[ERROR] Could not save results: {e}")
    
    print("=" * 60)

if __name__ == "__main__":
    main()