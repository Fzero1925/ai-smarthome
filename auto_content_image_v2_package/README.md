# 一、核心问题（直指现状）

1. **内容生成与关键词引擎“脱节”**
    你的文章生成脚本还没有吃到“关键词引擎 v2”的机会分和“为什么选它”的解释，导致选题优先级、文案结构、CTA 不够针对成交。（待挂接 `opportunity_score / est_value_usd / why_selected`）
2. **图片匹配偏静态 + 不足量**
    多处用**字典映射/占位图**替代真实“语义匹配 + 质量评分”的选图逻辑，实际文章常常无图或图不符；且**重复图冲突**没有严格治理。（虽然已有去重雏形，但仍以 `/images/products/` 前缀判断，覆盖不足）deduplicate_and_enhance_images
3. **图片合规与 SEO 细节有风险**
   - **ALT 模板“Best 2025”式**过度商业化，易被判“过度优化”。generate_daily_content generate_quality_content_enhanc…
   - image sitemap 的 **base_url** 硬编码为 `https://ai-smarthomehub.com`，与你站实际（含 www）不一致，影响索引一致性。generate_image_sitemap
4. **质量闸门过宽**
    目前质量检查仅看字数/章节/Front-matter/Intro/Conclusion，**未覆盖**：图片数量/ALT 必填/披露/结构化数据（Schema）/内部链接/原创度去重等关键指标。quality_check
5. **目录/分类命名不统一**
    类目名在不同脚本间有**hyphen/underscore 混用**（如 `smart-plugs` vs `smart_plugs`），容易导致匹配失败，尤其是你靠字符串包含判断的地方（图片/类目默认图/写入 front-matter）。



# 二、目标蓝图：**完全自动化生产线**

**关键词引擎 v2 →（Top Picks）→ 内容生成 → 选图（封面+插图）→ 去重/替换 → 质量闸门 → 发布 → Image Sitemap 更新**

- 触发条件：`opportunity_score ≥ 70` 且 `est_value_usd` 为正
- 每篇文章**至少 1 张封面 + 2 张正文插图**；全部具备 `alt/title/caption/credit/license`；front-matter 写入 `featured_image` / `images[]` / `image_meta[]`
- 产出后自动：更新 `sitemap-images.xml`（合并入 sitemap index）并在 `robots.txt` 引用。



# 三、逐脚本改造建议（要点 + 原因 + 如何做）

## 1) `generate_quality_content_enhanced.py`（主内容生成）

**问题**：已声明“诚实/合规”框架，但尚未接入机会分与收益估计，未强制生成**对比表/兼容矩阵/FAQ**等结构化增值块；ALT 与图片模块未强绑定。generate_quality_content_enhanc…

**改造**

- **输入扩展**：接受 `opportunity_score / est_value_usd / why_selected / alt_keywords`；把“选题理由”写进文末 “Methodology & Why this topic”。
- **强制结构**：在正文自动插入
  - **Top Picks**（3 选 1 理由，源于 `why_selected` 的意图/场景）
  - **对比表**（协议/功率/是否要网关/本地控制/价格档位）
  - **兼容性矩阵**（Matter/Thread/Zigbee/HomeKit/Alexa/GA）
  - **安装与排错清单**（高价值常青）
  - **FAQ**（5 条基于 `alt_keywords`）
- **合规模块**：文首 Disclosure、文末 Sources（品牌规格/认证/固件说明）与 “Last updated”。
- **Schema**：注入 `Article + ItemList + FAQPage`（JSON-LD）字段。
- **图片钩子**：暴露 `image_needs = {hero, inline:2}` 给图片管理器回填（见第 3 点）。

## 2) `generate_daily_content.py`（另一条内容链）

**问题**：图片映射是**静态字典** + ALT 模板“Best 2025…”，存在**不匹配和过度优化**风险；类别默认图与真实关键词语义关联不足。generate_daily_content

**改造**

- 将 `get_product_images()` 改为**优先调用** `SmartImageManager.search_and_assign(keyword, category, needs={'hero':1,'inline':2})`，失败再落回本地映射/默认图。image_manager
- ALT 模板**去“Best/2025”统一口径**，改为**语义型描述**（“{设备}在{场景/特性}下的示例图”），避免关键词堆砌。

## 3) `image_manager.py`（智能图片管理器）

**问题**：有 API 客户端/质量评分/下载&缓存的框架，但**匹配与合规元数据**还不完整；Pexels/Pixabay 还在“模拟”阶段；图重复治理与文章上下文绑定不足。image_manager

**改造**

- **匹配层**：`rank_images()` 综合评分 = 语义相似（关键词+类目+why_selected 关键词）× 质量分 × 场景标签（如 “installation/energy/voice-control”）。
- **合规元数据**：保存 `source/provider/author/license/url/retrieved_at`；front-matter 写 `image_meta[]`。
- **去重策略**：站点级“**全局使用计数**”，同一张图片**最多用于 N=3 篇**；超限时强制替换。
- **命名与缓存**：下载到 `static/images/{category}/{content_hash}_{w}x{h}.webp`；生成 `srcset`（640/960/1280/1920），并回写到文章。
- **降级路径**：无 API → 品牌媒体包本地库 → 自制信息图（Pillow）→ 最后才用“通用图”。

> 你已有品质评分维度（分辨率/likes/描述/颜色），把**语义匹配**与**使用频次**加入即可。image_manager

## 4) `deduplicate_and_enhance_images.py`（跨文图去重）

**问题**：当前只针对 `/images/products/` 路径，且“最佳匹配保留、其他替换”的逻辑未强制**每篇至少两张插图**，也未更新 ALT/credit。deduplicate_and_enhance_images

**改造**

- **范围扩展**：扫描整站 `static/images/**`；以**内容哈希**去重（不是仅看路径）。
- **恢复动作**：对“失败替换”的文章，**回退到 SmartImageManager 的第二候选**；同时**补齐插图数**（不足 2 张则新配图）。
- **同步元数据**：替换时一并更新 `alt/title/caption/credit` 与 front-matter 的 `images[]`。

## 5) `update_article_images.py`（Front-matter 写回器）

**问题**：目前靠**本地 image_database** 选图；建议改为“**写回器**”，只负责把图片管理器的结果**落盘**到 front-matter（featured/og/inline）。update_article_images

**改造**

- 接口：`apply_images(article.md, assignment)`，其中 `assignment` 来自 `SmartImageManager`，含 hero/inline/alt/meta。
- 统一类目命名：`smart-plugs / smart-bulbs / security-cameras / robot-vacuums / smart-thermostats / smart-speakers`（**全部用 hyphen**）。

## 6) `generate_image_sitemap.py`（图片站点地图）

**问题**：`base_url` 与实际站点域名不一致（少了 `www.`）；建议纳入**压缩与索引合并**流程。generate_image_sitemap

**改造**

- `base_url = "https://www.ai-smarthomehub.com"`；生成后写入 `static/sitemap-images.xml` 并**追加到主 sitemap index**；robots.txt 中暴露路径。
- 过滤占位图/低分图：只收录 `quality_score ≥ 0.6` 或被文章引用的图片（从 front-matter 逆向读取）。

## 7) `quality_check.py`（质量闸门）

**问题**：未检测**图片数量/ALT/Schema/披露/内部链接**等关键项。quality_check

**改造（新增校验）**

- **图片**：`featured_image` 必填；正文插图 ≥2；全部 `alt` 非空且**不含“best/2025/cheap/lowest price”**字样。
- **披露**：文首/文末存在联盟披露段；
- **Schema**：`Article + ItemList + FAQPage` 存在；
- **链接**：内部链接 ≥3、外链 ≥2（含源文档/品牌规格）；
- **原创度**：基于 3-gram 覆盖率与站内近 30 天新文重合度阈值；
- **E-E-A-T**：作者/编辑/审校字段与更新时间必填。
- **打回策略**：任何一项红线不合格 → 不发布。

## 8) `image_config.py` / `setup_images.py` / `setup_product_images.py`

**问题**：当前流程鼓励占位图上生产；建议**仅在开发模式允许占位图**，生产发布强制由 `SmartImageManager` 配齐后放行。image_config setup_images setup_product_images

**改造**

- `ENV=prod` 时：占位图**直接 fail**；
- `ENV=dev`：占位允许，但 `noindex` + 不入 image-sitemap；
- `ImageAPIConfig` 提示：申请 API 的引导继续保留（分流到 Unsplash/Pexels/Pixabay），并在 `SmartImageManager` 里做速率轮询与缓存。image_config

------

# 四、把“关键词引擎 v2”接进来（关键联动）

在你内容主入口（例如 `generate_daily_content.py` 或站内调度器）：

1. 读取 `top_picks.json`（含 `keyword/category/opportunity_score/est_value_usd/why_selected/alt_keywords`）。
2. 对每个 Top Pick：
   - 调 `generate_quality_content_enhanced.py` 产出**结构化文章**；generate_quality_content_enhanc…
   - 调 `SmartImageManager.search_and_assign()` 产出**hero + 2×inline**；写回 front-matter；image_manager update_article_images
   - 调 `deduplicate_and_enhance_images.py` 做**全站去重与替换**；deduplicate_and_enhance_images
   - 调 `quality_check.py` 过闸门，失败则回滚或降级补救；quality_check
   - 成功后触发 `generate_image_sitemap.py` 更新 **image-sitemap**（修正 base_url）。generate_image_sitemap

------

# 五、PR 级落地清单（你可直接分工给 Claude）

**PR#1 · 统一命名 & 配置**

- 统一类目 slug（全部用连字符）；环境变量 `ENV` 引入生产/开发分支；`image_manager` 的输出目录采用内容哈希 + WebP。

**PR#2 · 内容引擎联动**

- `generate_quality_content_enhanced.py`：新增入参（机会分/收益/解释/备选词），强制插入对比表/FAQ/兼容矩阵/披露/Schema。generate_quality_content_enhanc…
- `generate_daily_content.py`：图片改为经 `SmartImageManager` 动态获取，去掉“Best 2025”式 ALT。generate_daily_content image_manager

**PR#3 · 智能配图闭环**

- `image_manager.py`：实现 `search_and_assign(keyword, category, needs)`、`rank_images()`、`usage_quota`、`image_meta`；写回 front-matter。image_manager
- `update_article_images.py`：改造成“写回器”。update_article_images
- `deduplicate_and_enhance_images.py`：改为**内容哈希去重** + 自动补图；更新 alt/credit。deduplicate_and_enhance_images

**PR#4 · 质量闸门升级**

- `quality_check.py`：加入图片/ALT/披露/Schema/链接/原创度/作者与更新时间等校验项；`ENV=prod` 未过闸即**不发布**。quality_check

**PR#5 · SEO 收尾**

- `generate_image_sitemap.py`：改 `base_url=https://www.ai-smarthomehub.com`，仅收录被引用或质量分 ≥0.6 的图片；生成后合并到 sitemap index。generate_image_sitemap

------

# 六、自动化运行手册（无人工）

- **定时**（GitHub Actions/Cron）：
  1. 跑关键词引擎 v2 → 产出 `top_picks.json`
  2. 循环生成内容→选图→去重→质检→发布
  3. 更新 image-sitemap → ping 搜索引擎
- **监控面板**（每日）：
  - 新文合格率 ≥ 90%
  - 每文图片数（≥3）与**重复率**（< 10%）
  - 关键词到上线中位用时 < 24h
  - RPM/CTR 回标校准参数每两周更新

------

# 七、你会立刻看到的改善

- 每篇文**都有**“合规且相关”的**封面 + 2 张插图**；
- ALT/credit/license/og:image/Schema **一键齐活**；
- 站内图**不再一图多用**；站点级 image-sitemap 与页面引用**一致**；
- 选题**紧跟机会分**，文内结构对准**成交路径**（对比表 + 兼容矩阵 + 安装/排错）；
- 完整无人值守流水线，合格才发，**不合格自动打回**。