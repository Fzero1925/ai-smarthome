# 图片获取与匹配机制方案（AI Smart Home Hub）

更新时间：2025-09-11

## 目标

- 为每篇文章可靠地选出“主题高度相关、质量达标、可复用受控”的封面图与内文配图。
- 在不依赖外部 API 的情况下，优先使用本地图库；在具备密钥时可扩展到外部来源。
- 输出稳定的 `featured_image`、`featured_image_alt`、`featured_image_title` 等前言字段，满足 AdSense 与 SEO 要求。

## 数据来源

1) 本地图库（首选）
- 路径：`static/images/products/<category>/...`、`static/images/scenes/`、`static/images/products/general/`
- 命名建议：包含品牌/型号/品类关键词（例如 `roborock-s7-maxv-ultra.jpg`）

2) 外部 API（可选）
- 在 `image_config.yml` 中配置 `unsplash/pexels/pixabay`，默认禁用；通过 `development.disable_api_calls` 控制。

## 匹配输入（来自文章 front matter）
- `title`、`categories`、`tags`
- 可选：`product_review.{name,brand,model,description}`
- 文章文件名与 slug（作为补充 token）

## 匹配流程（打分选择）

- 规范化 token：对标题/标签/品牌/型号/文件名进行小写、符号移除、分词归一。
- 候选集合：
  - 优先扫描 `static/images/products/<category>`；无结果时回退 `products/general`、`scenes`；最后回退 `static/images/default-article.jpg`。
- 打分维度（由 `image_config.yml` 的 `scoring` 控制）：
  - 关键词匹配（basename 与 token 的交集比例）
  - 类别匹配（候选图片所在目录与文章主类一致加权）
  - 场景匹配（文件名包含 installation/compatibility/comparison 等场景词）
  - 质量加分（Pillow 获取宽高；满足 `quality.min_width/height` 加分）
  - 复用惩罚（`data/image_usage.json` 记录使用次数；超过上限加罚）
- 最终选择：得分最高且 ≥ `quality_rules.min_image_relevance_score` 的图片；否则按回退顺序选择。

## ALT 与标题生成

- 基于 `image_config.yml.seo.alt_templates` 与文章上下文生成：
  - `hero` 模板用于封面：`{category} overview and compatibility guide for smart home automation`
  - `inline` 模板用于内文：`{keyword} key features and installation guide`
- ALT 限制：长度 15–125 字符，剔除禁用词（`banned_alt_words`）。

## 质量与合规

- 检查：分辨率/文件大小/格式（`quality.*` 与 `quality_rules.*`）
- 复用：`quality.max_usage_count` 与 `quality_rules.max_duplicate_usage`；超限自动降级到下一候选。
- 法务：可在 `compliance.*` 开启许可与署名要求（本地图库默认通过）

## 回退策略

- 品牌/型号命中 > 品类命中 > 场景图 > 通用图 > 默认图（`static/images/default-article.jpg`）
- 若仍无合适图片：按 `fallback.*` 生成信息图占位（可选）

## 输出与写回

- 更新 front matter：`featured_image`、`featured_image_alt`、`featured_image_title`
- 记录使用：`data/image_usage.json`
- 可选生成：`static/sitemap-images.xml`（由 `scripts/generate_image_sitemap.py` 负责）

## 运行方式

- 单次：`python scripts/image_selector.py --target content/articles/foo.md`
- 批量：`python scripts/image_selector.py --articles-dir content/articles`
- 仅模拟：`--dry-run`

## 配置文件

- `image_config.yml`：全局质量、打分、回退、API、缓存等
- `config/image_mappings.yml`：品牌/别名/同义词映射，提升命中率

## 与现有脚本的关系

- `scripts/update_article_images.py`：旧版静态映射方案（可继续保留）；新脚本提供“通用打分 + 受控复用 + QA 校验”。
- `scripts/fix_featured_images.py`：批量修复入口，后续可切换到调用 `image_selector.py`。
- `scripts/generate_image_sitemap.py`：生成图片站点地图。

## 后续计划

- 加入 EXIF 与感知哈希（pHash）以避免近重复图片
- 图片裁剪与多尺寸 `srcset` 生成（由 Hugo/管道或预处理完成）
- 与生成器联动：按段落主题插入内文图（setup/troubleshooting/comparison 等）

