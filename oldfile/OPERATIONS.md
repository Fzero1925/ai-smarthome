# AI Smart Home Hub - 运维操作手册

> **⚠️ 文档已过时**: 此运维手册内容已整合到新的中文文档系统  
> **请使用新文档**:  
> - `dev-docs/使用说明.md` - 日常使用和维护指南  
> - `dev-docs/问题解决方案.md` - 故障排除和问题处理  
> - `项目状态总览.md` - 系统当前状态查看  

---

## 📋 概览

本文档提供AI Smart Home Hub的日常运维指南，包括监控、故障排除、维护和紧急响应程序。

**系统架构**: Hugo + Python + GitHub Actions + Vercel + Telegram  
**运维负责人**: Fzero  
**紧急联系**: Telegram Bot通知 + 手机号 +86 17803877935

---

## 📊 系统健康监控

### 自动化监控清单

#### 每日检查 (11:00 AM 中国时间)
- ✅ **内容生成执行状态**
  - 检查Telegram通知是否收到"新内容发布"消息
  - 预期: 1-3篇文章自动生成
  - 异常: 连续2天无内容生成需要人工介入

- ✅ **网站可访问性**
  - 访问 https://ai-smarthome.vercel.app
  - 检查首页加载速度 (<3秒)
  - 验证最新文章是否显示

- ✅ **GitHub Actions状态**
  - 检查 daily-content.yml 工作流执行状态
  - 确认无构建失败或部署错误
  - 查看commit历史确保自动提交正常

#### 每周检查 (周一上午)
- 📈 **SEO和流量数据**
  - Google Analytics流量趋势
  - 搜索排名变化
  - 新增关键词覆盖

- 🔗 **链接和内容质量**
  - 随机检查5篇文章的Amazon链接有效性
  - 验证图片显示正常
  - 确认无404错误页面

- 💰 **收益数据**
  - Google AdSense收益(如果已启用)
  - Amazon Associates点击量
  - 转化率分析

---

## 🚨 故障排除指南

### 常见问题诊断

#### 1. 内容生成失败

**症状**: 预定时间(11:00)没有收到"新内容发布"通知

**诊断步骤**:
```bash
# 检查最近的workflow执行
gh run list --repo fzero1925/ai-smarthome --limit 5

# 查看失败的运行日志
gh run view [run-id] --repo fzero1925/ai-smarthome --log
```

**常见原因和解决方案**:
- **API限制**: Google Trends API达到限制
  - 解决: 等待24小时后自动恢复
  - 临时: 手动触发 `--force-generation`
  
- **Python依赖问题**: requirements.txt缺少包
  - 解决: 检查错误日志，更新dependencies
  
- **GitHub权限问题**: 无法提交新文章
  - 解决: 检查GITHUB_TOKEN权限设置

#### 2. Telegram通知中断

**症状**: 停止接收Telegram消息

**诊断步骤**:
```python
# 测试Bot连接
import requests
bot_token = "8494031502:AAHrT6csi5COqeUgG-wk_SiaYNjiXOFB-m4"
url = f"https://api.telegram.org/bot{bot_token}/getMe"
response = requests.get(url)
print(response.json())
```

**解决方案**:
- Bot Token过期: 联系@BotFather重新生成
- Chat ID变更: 发送消息给bot，获取新的chat_id
- 网络问题: 检查GitHub Actions网络访问

#### 3. 网站访问异常

**症状**: https://ai-smarthome.vercel.app 无法访问或加载缓慢

**诊断步骤**:
- 检查Vercel部署状态
- 验证DNS解析
- 查看Hugo构建日志

**解决方案**:
```bash
# 本地测试Hugo构建
hugo --minify

# 检查Vercel部署
vercel --prod

# 强制重新部署
git commit --allow-empty -m "force redeploy"
git push
```

#### 4. GitHub Actions工作流异常

**症状**: 工作流执行失败或卡住

**常见错误代码**:
- Exit Code 1: Python脚本执行错误
- Exit Code 128: Git操作失败
- Timeout: 工作流执行超时(10分钟限制)

**解决流程**:
1. 查看详细日志确定错误原因
2. 本地复现问题(如果可能)
3. 修复代码并推送
4. 必要时手动触发重新运行

---

## 📱 通知系统管理

### Telegram Bot配置

#### 当前配置
- **Bot用户名**: @ai_smarthome_monitor_bot (示例)
- **Bot Token**: `8494031502:AAHrT6csi5COqeUgG-wk_SiaYNjiXOFB-m4`
- **Chat ID**: `6041888803`
- **静默时间**: 22:00-08:00 (中国时间)

#### 通知类型和处理

**🚨 ERROR级别** (立即处理)
- 系统故障和构建失败
- API访问错误
- 数据损坏或安全问题
- **处理时限**: 2小时内响应

**✅ SUCCESS级别** (日常监控)
- 内容生成成功
- 网站部署完成
- 定期维护任务完成
- **处理**: 确认接收即可

**ℹ️ INFO级别** (记录备案)
- 系统状态更新
- 性能指标报告
- 定期健康检查结果
- **处理**: 周度汇总分析

#### 自定义通知测试

```python
# 发送测试消息
python scripts/notify_telegram.py \
  --type build \
  --status success \
  --site-url https://ai-smarthome.vercel.app \
  --commit-message "Test notification"

# 发送错误警报测试
python scripts/notify_telegram.py \
  --type error \
  --error-type "Manual Test" \
  --error-message "This is a manual test alert"
```

---

## 🔧 维护任务

### 每月维护清单

#### 第一周
- [ ] **依赖更新**
  ```bash
  # 更新Python包
  pip list --outdated
  pip install -r requirements.txt --upgrade
  
  # 更新Hugo
  hugo version
  # 如需更新，访问 https://github.com/gohugoio/hugo/releases
  ```

- [ ] **安全检查**
  ```bash
  # 检查依赖安全漏洞
  pip audit
  
  # 检查GitHub token权限
  gh auth status
  ```

#### 第二周
- [ ] **内容质量审计**
  - 随机审查10篇最新文章
  - 检查SEO分数和可读性
  - 验证affiliate链接有效性
  - 确认图片加载和alt文本

- [ ] **性能优化**
  ```bash
  # 检查网站性能
  lighthouse https://ai-smarthome.vercel.app --output html
  
  # 分析Hugo构建时间
  hugo --minify --verbose
  ```

#### 第三周
- [ ] **数据备份验证**
  ```bash
  # 备份关键配置
  cp .github/workflows/daily-content.yml backups/
  cp CLAUDE.md backups/
  cp config.toml backups/
  
  # 验证Git历史完整性
  git fsck
  ```

- [ ] **监控系统调优**
  - 分析通知频率和质量
  - 调整静默时间设置(如需)
  - 优化错误阈值和警报规则

#### 第四周
- [ ] **业务指标回顾**
  - 文章生成数量和质量统计
  - 网站流量增长分析
  - 收益数据汇总(如有)
  - 竞争对手分析更新

### 季度维护任务

- [ ] **全面安全审计**
- [ ] **系统架构评估**
- [ ] **业务目标校准**
- [ ] **技术路线图更新**

---

## 🆘 紧急响应程序

### 紧急情况分级

#### P0 - 严重影响 (2小时内响应)
- 网站完全无法访问
- 数据丢失或损坏
- 安全漏洞或攻击
- 关键自动化完全失效

#### P1 - 重要影响 (24小时内响应)
- 内容生成系统故障
- 部分功能异常
- 性能严重下降
- 收益系统异常

#### P2 - 一般影响 (72小时内响应)
- 单个文章问题
- 样式显示异常
- 次要功能故障
- 监控告警调优

### 紧急联系流程

1. **自动告警** (ERROR级Telegram通知)
2. **手动确认** (检查问题严重程度)
3. **快速修复** (优先恢复服务可用性)
4. **根本原因分析** (防止问题重复发生)
5. **文档更新** (更新操作手册和预防措施)

### 紧急修复工具箱

```bash
# 快速回滚到上一个工作版本
git revert HEAD
git push

# 禁用自动化任务(紧急情况)
# 在GitHub仓库设置中禁用Actions

# 强制重新部署
vercel --prod --force

# 清理缓存
rm -rf public/
rm -rf resources/
hugo --cleanDestinationDir
```

---

## 📈 性能监控

### 关键指标 (KPIs)

#### 系统稳定性
- **自动化成功率**: >95%
- **网站可用性**: >99.5%
- **平均响应时间**: <2秒
- **构建成功率**: >98%

#### 内容质量
- **每日文章生成**: 1-3篇
- **SEO分数**: >0.8
- **可读性分数**: >65
- **图片匹配率**: >90%(待改进)

#### 业务指标
- **有机流量增长**: 月度趋势
- **页面停留时间**: >2分钟
- **跳出率**: <70%
- **转化率**: 待建立基线

### 监控工具和仪表板

#### 系统监控
- **GitHub Actions**: 自动化任务执行状态
- **Vercel Analytics**: 网站性能和可用性
- **Telegram Bot**: 实时状态通知

#### 业务监控
- **Google Analytics**: 流量和用户行为
- **Google Search Console**: SEO表现
- **Amazon Associates**: 联盟营销数据

#### 自定义监控脚本
```bash
# 每日健康检查脚本
./scripts/health_check.py

# 内容质量审计
./scripts/content_audit.py --days 7

# 性能基准测试
./scripts/performance_benchmark.py
```

---

## 🔄 备份和恢复

### 备份策略

#### 自动备份 (每日)
- **Git仓库**: GitHub自动保存所有代码和内容
- **配置文件**: 通过Git版本控制
- **密钥和secrets**: GitHub Secrets自动加密存储

#### 手动备份 (每周)
```bash
# 创建完整项目快照
git archive --format=tar.gz --output=backup-$(date +%Y%m%d).tar.gz HEAD

# 备份关键配置文件
mkdir -p backups/$(date +%Y%m%d)
cp CLAUDE.md backups/$(date +%Y%m%d)/
cp PROGRESS.md backups/$(date +%Y%m%d)/
cp config.toml backups/$(date +%Y%m%d)/
```

### 恢复程序

#### 快速恢复 (服务中断)
```bash
# 回滚到最后一个工作版本
git revert HEAD~1
git push

# 强制重新部署
git commit --allow-empty -m "force redeploy"
git push
```

#### 完整恢复 (数据丢失)
1. 从GitHub克隆完整仓库
2. 恢复密钥和配置到GitHub Secrets
3. 验证所有自动化任务正常
4. 重新部署网站到Vercel

---

## 📚 常用命令参考

### 日常操作命令

```bash
# 查看系统状态
gh run list --repo fzero1925/ai-smarthome --limit 10
hugo version
git status

# 手动触发内容生成
python scripts/generate_articles.py --batch-size=2 --force

# 测试Telegram通知
python scripts/notify_telegram.py --type build --status success

# 本地开发和测试
hugo server -D
hugo --minify

# 检查网站健康
curl -I https://ai-smarthome.vercel.app
```

### 故障诊断命令

```bash
# GitHub Actions调试
gh run view [run-id] --log
gh workflow list --repo fzero1925/ai-smarthome

# Git历史和状态
git log --oneline -10
git diff HEAD~1

# 网站和服务检查
ping ai-smarthome.vercel.app
nslookup ai-smarthome.vercel.app
```

---

## 📞 支持和联系

### 技术支持
- **GitHub Issues**: https://github.com/fzero1925/ai-smarthome/issues
- **文档**: 本文档和CLAUDE.md
- **Claude Code**: 技术开发和故障排除

### 业务联系
- **项目负责人**: Fzero
- **紧急联系**: +86 17803877935
- **Telegram**: 通过配置的Bot接收通知

### 外部服务支持
- **Vercel支持**: https://vercel.com/support
- **GitHub支持**: https://support.github.com
- **Telegram Bot**: @BotFather

---

**最后更新**: 2025-08-31  
**文档版本**: v1.0  
**下次审查**: 2025-09-07