/**
 * 导航组件JavaScript模块
 * 包含移动端菜单、搜索功能、键盘导航等
 */

class NavigationManager {
  constructor() {
    this.navToggle = document.querySelector('.nav-toggle');
    this.mobileMenu = document.querySelector('.mobile-menu');
    this.searchInputs = document.querySelectorAll('.search-input');
    this.navLinks = document.querySelectorAll('.nav-link');

    this.init();
  }

  init() {
    this.setupMobileMenu();
    this.setupSearch();
    this.setupKeyboardNavigation();
    this.setupAnalytics();
    this.setupPerformanceOptimizations();
  }

  // 移动端菜单功能
  setupMobileMenu() {
    if (!this.navToggle || !this.mobileMenu) return;

    // 菜单切换
    this.navToggle.addEventListener('click', () => {
      const isExpanded = this.navToggle.getAttribute('aria-expanded') === 'true';

      this.navToggle.setAttribute('aria-expanded', String(!isExpanded));
      this.mobileMenu.hidden = isExpanded;

      // 焦点管理
      if (!isExpanded) {
        const firstLink = this.mobileMenu.querySelector('a');
        if (firstLink) {
          setTimeout(() => firstLink.focus(), 100);
        }
      }
    });

    // 点击外部关闭菜单
    document.addEventListener('click', (e) => {
      if (!this.navToggle.contains(e.target) && !this.mobileMenu.contains(e.target)) {
        this.closeMobileMenu();
      }
    });

    // Escape键关闭菜单
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && this.navToggle.getAttribute('aria-expanded') === 'true') {
        this.closeMobileMenu();
        this.navToggle.focus();
      }
    });

    // 响应式关闭菜单
    window.addEventListener('resize', () => {
      if (window.innerWidth > 992) {
        this.closeMobileMenu();
      }
    });
  }

  closeMobileMenu() {
    this.navToggle.setAttribute('aria-expanded', 'false');
    this.mobileMenu.hidden = true;
  }

  // 搜索功能
  setupSearch() {
    this.searchInputs.forEach(input => {
      // Escape键清空搜索
      input.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && input.value) {
          input.value = '';
          input.blur();
        }
      });

      // 分析跟踪
      const form = input.closest('.search-form');
      if (form) {
        form.addEventListener('submit', (e) => {
          const query = input.value.trim();
          if (query && typeof gtag !== 'undefined') {
            gtag('event', 'search', {
              'search_term': query,
              'source': input.id.includes('mobile') ? 'mobile_header' : 'desktop_header'
            });
          }
        });
      }
    });
  }

  // 键盘导航增强
  setupKeyboardNavigation() {
    this.navLinks.forEach((link, index) => {
      link.addEventListener('keydown', (e) => {
        let targetIndex = index;

        switch (e.key) {
          case 'ArrowLeft':
            e.preventDefault();
            targetIndex = index > 0 ? index - 1 : this.navLinks.length - 1;
            break;
          case 'ArrowRight':
            e.preventDefault();
            targetIndex = index < this.navLinks.length - 1 ? index + 1 : 0;
            break;
          case 'Home':
            e.preventDefault();
            targetIndex = 0;
            break;
          case 'End':
            e.preventDefault();
            targetIndex = this.navLinks.length - 1;
            break;
          default:
            return;
        }

        this.navLinks[targetIndex].focus();
      });
    });
  }

  // 分析跟踪
  setupAnalytics() {
    document.addEventListener('click', (e) => {
      const navLink = e.target.closest('.nav-link, .mobile-nav-link');
      if (navLink && typeof gtag !== 'undefined') {
        const linkText = navLink.textContent.trim();
        const isMobile = navLink.classList.contains('mobile-nav-link');

        gtag('event', 'navigation_click', {
          'link_text': linkText,
          'source': isMobile ? 'mobile_nav' : 'desktop_nav'
        });
      }
    });
  }

  // 性能优化
  setupPerformanceOptimizations() {
    // 链接预加载
    this.navLinks.forEach(link => {
      link.addEventListener('mouseenter', function() {
        const url = this.href;
        if (url && !document.querySelector(`link[rel="prefetch"][href="${url}"]`)) {
          const prefetchLink = document.createElement('link');
          prefetchLink.rel = 'prefetch';
          prefetchLink.href = url;
          document.head.appendChild(prefetchLink);
        }
      }, { once: true });
    });
  }
}

// 辅助功能优化
class AccessibilityManager {
  static init() {
    // 减少动画偏好检测
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      const style = document.createElement('style');
      style.textContent = `
        .hamburger-line,
        .mobile-menu {
          transition: none !important;
          animation: none !important;
        }
      `;
      document.head.appendChild(style);
    }

    // 高对比度模式检测
    if (window.matchMedia('(prefers-contrast: high)').matches) {
      document.documentElement.classList.add('high-contrast');
    }
  }
}

// 初始化
document.addEventListener('DOMContentLoaded', () => {
  new NavigationManager();
  AccessibilityManager.init();
});

// 导出供其他模块使用
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { NavigationManager, AccessibilityManager };
}