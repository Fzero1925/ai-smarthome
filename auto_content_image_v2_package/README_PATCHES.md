
# README — 应用补丁与样例
- 本目录 `patches/*.patch` 为 **统一 diff**，只在文件末尾追加 v2 区块（不影响现有逻辑）。
- 应用方式：项目根执行
```bash
patch -p0 < patches/generate_daily_content.py.patch
patch -p0 < patches/image_manager.py.patch
patch -p0 < patches/deduplicate_and_enhance_images.py.patch
patch -p0 < patches/generate_image_sitemap.py.patch
patch -p0 < patches/quality_check.py.patch
patch -p0 < patches/setup_images.py.patch
patch -p0 < patches/setup_product_images.py.patch
patch -p0 < patches/image_config.py.patch
patch -p0 < patches/update_article_images.py.patch
```
- 可选：把 `smart_image_manager.py` 放到项目根（或 PYTHONPATH 内）以启用 `search_and_assign()`。
- 运行 `python samples/run_pipeline_example.py` 查看自动配图分配的示例输出。
