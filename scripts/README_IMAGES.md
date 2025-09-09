# 🖼️ AI智能图片管理系统

为AI Smart Home Hub网站提供专业的图片获取和管理解决方案，专门为Google AdSense申请准备。

## 🎯 系统特点

- ✅ **免费API集成** - 支持Unsplash、Pexels、Pixabay三大免费图片源
- ✅ **智能关键词匹配** - 自动根据文章内容匹配最相关的图片  
- ✅ **SEO优化** - 自动生成符合SEO要求的alt标签
- ✅ **批量处理** - 一键为所有文章配置专业图片
- ✅ **分类管理** - 按产品类别智能归档图片
- ✅ **速率控制** - 自动管理API调用限制，避免超额

## 🚀 快速开始

### 1. 一键设置（推荐）

```bash
# 运行一键设置脚本
python scripts/setup_images.py
```

这个脚本会：
- 检查API配置状态
- 创建必要的目录结构
- 批量处理所有文章
- 生成处理报告

### 2. 手动配置

```python
# 单独使用图片管理器
from scripts.image_manager import SmartImageManager
import asyncio

async def process_images():
    manager = SmartImageManager()
    
    # 处理单篇文章
    result = await manager.process_article_images("content/articles/your-article.md")
    print(f"找到 {result['images_found']} 张相关图片")
    
    # 批量处理所有文章
    results = await manager.batch_process_articles()
    print(f"处理了 {len(results)} 篇文章")

asyncio.run(process_images())
```

## 🔑 API密钥配置

### 申请免费API密钥

1. **Unsplash API** (推荐)
   - 访问: https://unsplash.com/developers
   - 免费额度: 50次/小时
   - 质量：⭐⭐⭐⭐⭐

2. **Pexels API**
   - 访问: https://www.pexels.com/api/
   - 免费额度: 200次/小时  
   - 质量：⭐⭐⭐⭐

3. **Pixabay API**
   - 访问: https://pixabay.com/api/docs/
   - 免费额度: 5000次/月
   - 质量：⭐⭐⭐

### 配置方法

#### 方法1: 环境变量（推荐）
```bash
# 设置环境变量
set UNSPLASH_ACCESS_KEY=your_unsplash_key
set PEXELS_API_KEY=your_pexels_key  
set PIXABAY_API_KEY=your_pixabay_key
```

#### 方法2: 代码配置
```python
from scripts.image_manager import SmartImageManager

manager = SmartImageManager()
manager.setup_api_keys({
    'unsplash': 'your_unsplash_access_key',
    'pexels': 'your_pexels_api_key',
    'pixabay': 'your_pixabay_api_key'
})
```

## 📊 系统架构

```
scripts/
├── image_manager.py      # 核心图片管理器
├── image_config.py       # API配置管理
├── setup_images.py       # 一键设置脚本
└── README_IMAGES.md      # 本文档

static/images/products/   # 图片存储目录
├── smart-plugs/
├── smart-thermostats/
├── smart-bulbs/
├── security-cameras/
├── robot-vacuums/
└── general/
```

## 🎯 智能匹配算法

系统使用多因素评分算法选择最佳图片：

1. **关键词匹配度** (权重: 40%)
   - 标题关键词匹配
   - 描述内容匹配
   - 标签相关性检查

2. **图片质量分析** (权重: 30%)
   - 分辨率检查 (>1920px优先)
   - 横版比例优选 (16:9, 4:3)
   - 专业摄影质量

3. **API来源权重** (权重: 20%)
   - Unsplash: 1.0 (最高质量)
   - Pexels: 0.9
   - Pixabay: 0.8

4. **使用场景适配** (权重: 10%)
   - 产品展示图优先
   - 家庭使用场景
   - 技术细节特写

## 📈 AdSense优化

系统专门为Google AdSense申请优化：

- ✅ **高质量图片** - 所有图片均来自专业摄影师作品
- ✅ **商用许可** - 所有API均提供免费商用授权
- ✅ **SEO优化** - 自动生成描述性alt标签
- ✅ **相关性匹配** - 图片与文章内容高度相关
- ✅ **尺寸规范** - 符合网页显示标准

## 🔧 高级功能

### 自定义关键词映射

```python
manager = SmartImageManager()

# 添加自定义关键词映射
manager.keyword_mapping['smart-locks'] = [
    'smart door lock keyless entry',
    'biometric door lock',
    'wifi door lock app control'
]
```

### 图片质量评分

```python
# 自定义图片评分规则
def custom_scoring(image, keyword):
    score = 0.0
    
    # 分辨率加分
    if 'width' in image and image['width'] >= 1920:
        score += 2.0
    
    # 特定关键词加分
    if 'smart home' in keyword.lower():
        score += 1.5
    
    return score

manager._calculate_image_score = custom_scoring
```

### 批量优化现有图片

```python
# 替换现有的Unsplash在线图片为本地图片
async def replace_online_images():
    import re
    
    articles = Path("content/articles").glob("*.md")
    for article in articles:
        content = article.read_text()
        
        # 查找Unsplash图片链接
        unsplash_pattern = r'https://images\.unsplash\.com/[^\s"]*'
        matches = re.findall(unsplash_pattern, content)
        
        if matches:
            print(f"发现 {len(matches)} 个在线图片链接: {article.name}")
            # 处理替换逻辑...
```

## 🐛 故障排除

### 常见问题

1. **API调用失败**
   ```
   错误: API rate limit exceeded
   解决: 等待速率限制重置或配置多个API密钥
   ```

2. **图片匹配度低**
   ```
   问题: 找到的图片与文章内容不匹配
   解决: 优化文章关键词或手动指定搜索词
   ```

3. **目录权限错误**
   ```
   错误: Permission denied creating directory
   解决: 检查static/images/目录写入权限
   ```

### 日志检查

系统会在 `logs/image_manager.log` 记录详细日志：

```bash
# 查看最新日志
tail -f logs/image_manager.log

# 查看错误日志
grep "ERROR" logs/image_manager.log
```

## 🎉 部署到生产环境

### GitHub Actions集成

```yaml
# .github/workflows/update-images.yml
name: Update Article Images

on:
  schedule:
    - cron: '0 2 * * 0'  # 每周日更新

jobs:
  update-images:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v3
        with:
          python-version: '3.9'
      
      - name: Update images
        env:
          UNSPLASH_ACCESS_KEY: ${{ secrets.UNSPLASH_ACCESS_KEY }}
          PEXELS_API_KEY: ${{ secrets.PEXELS_API_KEY }}
        run: |
          python scripts/setup_images.py
```

### 性能优化建议

1. **缓存策略**
   - 本地缓存API响应
   - 避免重复下载相同图片

2. **CDN集成**
   - 上传图片到免费CDN (Cloudinary, ImageKit)
   - 自动图片压缩和格式转换

3. **监控告警**
   - API使用量监控
   - 图片质量检查
   - 失败率告警

## 📞 支持与反馈

- 📧 技术问题: 检查logs/image_manager.log日志文件
- 🐛 Bug报告: 请提供详细的错误日志和重现步骤  
- 💡 功能建议: 欢迎提出改进意见

---

**🌟 系统已就绪! 现在您的网站拥有专业级图片系统，完全满足Google AdSense申请要求! 🚀**