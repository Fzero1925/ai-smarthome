#!/usr/bin/env python3
"""
实时文章生成触发器 - Realtime Content Generation Trigger
当检测到高价值热点话题时，立即触发文章生成，不受定时限制

核心功能：
1. 实时监控热点关键词变化
2. 智能判断是否需要立即生成文章
3. 自动触发文章生成流程
4. 即时Telegram通知
5. 防止重复生成和内容冲突
"""

import os
import json
import asyncio
import subprocess
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any
from pathlib import Path
import pytz
import requests

# 导入实时分析器
from modules.trending.realtime_analyzer import RealtimeTrendingAnalyzer, TrendingTopic, analyze_current_trends


class RealtimeContentTrigger:
    """实时内容生成触发器"""
    
    def __init__(self):
        self.logger = self._setup_logging()
        self.data_dir = "data/realtime_triggers"
        self.generation_history = "data/generation_history"
        self.monitoring_active = False
        
        # 创建必要目录
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.generation_history, exist_ok=True)
        
        # 触发条件配置
        self.trigger_thresholds = {
            'min_trend_score': 0.75,        # 最低趋势评分
            'min_commercial_value': 0.70,    # 最低商业价值
            'min_urgency_score': 0.80,       # 最低紧急度
            'min_search_volume': 10000,      # 最低搜索量
            'max_competition_level': 'Medium-High'  # 最高竞争度
        }
        
        # 防重复生成配置
        self.cooldown_hours = 6  # 同一关键词6小时内不重复生成
        self.max_daily_generations = 4  # 每日最大生成数
        
        # Telegram配置
        self.telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')
        
    def _setup_logging(self) -> logging.Logger:
        """设置日志系统"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('data/realtime_trigger.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)
    
    async def start_monitoring(self, check_interval_minutes: int = 30):
        """启动实时监控"""
        self.monitoring_active = True
        self.logger.info(f"🚀 实时监控启动 - 检查间隔: {check_interval_minutes} 分钟")
        
        while self.monitoring_active:
            try:
                await self.check_and_trigger()
                await asyncio.sleep(check_interval_minutes * 60)  # 转换为秒
                
            except KeyboardInterrupt:
                self.logger.info("⏹️ 收到停止信号，正在关闭监控...")
                self.monitoring_active = False
                break
            except Exception as e:
                self.logger.error(f"❌ 监控循环出错: {e}")
                await asyncio.sleep(60)  # 出错后等待1分钟再继续
    
    async def check_and_trigger(self) -> Dict[str, Any]:
        """检查热点并触发生成"""
        self.logger.info("🔍 开始检查热点话题...")
        
        # 获取当前趋势分析
        try:
            trends_data = await analyze_current_trends(force_analysis=False)
            trending_topics = [
                TrendingTopic(**topic) for topic in trends_data['trending_topics']
            ]
            
            if not trending_topics:
                self.logger.info("📊 未发现新的热点话题")
                return {'status': 'no_trends', 'action': 'none'}
                
        except Exception as e:
            self.logger.error(f"❌ 趋势分析失败: {e}")
            return {'status': 'error', 'message': str(e)}
        
        # 评估是否需要立即触发
        trigger_candidates = self._evaluate_trigger_candidates(trending_topics)
        
        if not trigger_candidates:
            self.logger.info("⏳ 暂无符合触发条件的热点话题")
            return {'status': 'no_triggers', 'topics_count': len(trending_topics)}
        
        # 执行触发
        trigger_results = []
        for candidate in trigger_candidates:
            result = await self._execute_content_generation(candidate)
            trigger_results.append(result)
        
        # 汇总报告
        summary = self._generate_trigger_summary(trigger_results, trending_topics)
        
        # 发送Telegram通知
        if trigger_results:
            await self._send_trigger_notification(summary)
        
        return summary
    
    def _evaluate_trigger_candidates(self, topics: List[TrendingTopic]) -> List[TrendingTopic]:
        """评估触发候选话题"""
        candidates = []
        
        for topic in topics:
            # 基本条件检查
            if not self._meets_basic_criteria(topic):
                continue
            
            # 检查是否最近已生成过相似内容
            if self._check_recent_generation(topic.keyword):
                self.logger.info(f"⏭️ 跳过 '{topic.keyword}' - 最近已生成相似内容")
                continue
            
            # 检查每日生成限额
            if self._check_daily_limit():
                self.logger.info("📊 已达到每日最大生成限额")
                break
            
            # 通过所有检查，加入候选列表
            candidates.append(topic)
            self.logger.info(f"✅ '{topic.keyword}' 符合立即生成条件")
        
        # 按优先级排序，取前2个
        candidates.sort(key=lambda t: (
            t.urgency_score * 0.4 + 
            t.commercial_value * 0.3 + 
            t.trend_score * 0.3
        ), reverse=True)
        
        return candidates[:2]  # 最多同时生成2篇文章
    
    def _meets_basic_criteria(self, topic: TrendingTopic) -> bool:
        """检查话题是否满足基本触发条件"""
        criteria_checks = {
            'trend_score': topic.trend_score >= self.trigger_thresholds['min_trend_score'],
            'commercial_value': topic.commercial_value >= self.trigger_thresholds['min_commercial_value'],
            'urgency_score': topic.urgency_score >= self.trigger_thresholds['min_urgency_score'],
            'search_volume': topic.search_volume_est >= self.trigger_thresholds['min_search_volume'],
            'competition_ok': self._check_competition_level(topic.competition_level)
        }
        
        passed_checks = sum(criteria_checks.values())
        required_checks = 4  # 至少通过4项检查
        
        if passed_checks >= required_checks:
            self.logger.info(f"🎯 '{topic.keyword}' 通过 {passed_checks}/5 项基本检查")
            return True
        else:
            self.logger.debug(f"❌ '{topic.keyword}' 仅通过 {passed_checks}/5 项检查: {criteria_checks}")
            return False
    
    def _check_competition_level(self, competition: str) -> bool:
        """检查竞争度是否可接受"""
        competition_levels = {
            'Low': 1, 'Low-Medium': 2, 'Medium': 3, 
            'Medium-High': 4, 'High': 5
        }
        
        current_level = competition_levels.get(competition, 3)
        max_level = competition_levels.get(self.trigger_thresholds['max_competition_level'], 4)
        
        return current_level <= max_level
    
    def _check_recent_generation(self, keyword: str) -> bool:
        """检查是否最近已生成过相似内容"""
        history_file = f"{self.generation_history}/generation_log.json"
        
        if not os.path.exists(history_file):
            return False
        
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
            
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=self.cooldown_hours)
            
            for record in history[-20:]:  # 检查最近20条记录
                if record['keyword'].lower() == keyword.lower():
                    gen_time = datetime.fromisoformat(record['timestamp'].replace('Z', '+00:00'))
                    if gen_time > cutoff_time:
                        return True
            
        except Exception as e:
            self.logger.error(f"⚠️ 检查生成历史失败: {e}")
        
        return False
    
    def _check_daily_limit(self) -> bool:
        """检查是否达到每日生成限额"""
        history_file = f"{self.generation_history}/generation_log.json"
        
        if not os.path.exists(history_file):
            return False
        
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
            
            today = datetime.now(timezone.utc).date()
            today_count = 0
            
            for record in history[-50:]:  # 检查最近50条记录
                gen_date = datetime.fromisoformat(record['timestamp'].replace('Z', '+00:00')).date()
                if gen_date == today:
                    today_count += 1
            
            return today_count >= self.max_daily_generations
            
        except Exception as e:
            self.logger.error(f"⚠️ 检查每日限额失败: {e}")
            return False
    
    async def _execute_content_generation(self, topic: TrendingTopic) -> Dict[str, Any]:
        """执行内容生成"""
        self.logger.info(f"🚀 开始为 '{topic.keyword}' 生成文章...")
        
        start_time = datetime.now(timezone.utc)
        
        try:
            # 调用文章生成脚本
            result = subprocess.run([
                'python', 'scripts/generate_daily_content.py',
                '--count', '1',
                '--keyword', topic.keyword,
                '--category', topic.category,
                '--priority', 'urgent'
            ], capture_output=True, text=True, timeout=300)  # 5分钟超时
            
            if result.returncode == 0:
                # 生成成功
                generation_result = {
                    'status': 'success',
                    'keyword': topic.keyword,
                    'category': topic.category,
                    'start_time': start_time.isoformat(),
                    'end_time': datetime.now(timezone.utc).isoformat(),
                    'trigger_reason': topic.business_reasoning,
                    'estimated_revenue': topic.estimated_revenue,
                    'urgency_score': topic.urgency_score,
                    'stdout': result.stdout,
                    'stderr': result.stderr if result.stderr else None
                }
                
                # 记录到历史
                self._log_generation(generation_result, topic)
                
                self.logger.info(f"✅ '{topic.keyword}' 文章生成成功")
                
            else:
                # 生成失败
                generation_result = {
                    'status': 'failed',
                    'keyword': topic.keyword,
                    'error': result.stderr or 'Unknown error',
                    'return_code': result.returncode,
                    'start_time': start_time.isoformat(),
                    'end_time': datetime.now(timezone.utc).isoformat()
                }
                
                self.logger.error(f"❌ '{topic.keyword}' 文章生成失败: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            generation_result = {
                'status': 'timeout',
                'keyword': topic.keyword,
                'error': 'Generation process timed out after 5 minutes',
                'start_time': start_time.isoformat(),
                'end_time': datetime.now(timezone.utc).isoformat()
            }
            self.logger.error(f"⏰ '{topic.keyword}' 文章生成超时")
            
        except Exception as e:
            generation_result = {
                'status': 'error',
                'keyword': topic.keyword,
                'error': str(e),
                'start_time': start_time.isoformat(),
                'end_time': datetime.now(timezone.utc).isoformat()
            }
            self.logger.error(f"💥 '{topic.keyword}' 生成过程异常: {e}")
        
        return generation_result
    
    def _log_generation(self, result: Dict, topic: TrendingTopic):
        """记录生成历史"""
        history_file = f"{self.generation_history}/generation_log.json"
        
        log_entry = {
            'timestamp': result['end_time'],
            'keyword': topic.keyword,
            'category': topic.category,
            'status': result['status'],
            'trigger_type': 'realtime',
            'trend_score': topic.trend_score,
            'commercial_value': topic.commercial_value,
            'urgency_score': topic.urgency_score,
            'estimated_revenue': topic.estimated_revenue,
            'sources': topic.sources
        }
        
        # 读取现有历史
        history = []
        if os.path.exists(history_file):
            try:
                with open(history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            except Exception as e:
                self.logger.error(f"读取历史记录失败: {e}")
        
        # 添加新记录
        history.append(log_entry)
        
        # 保持最近100条记录
        if len(history) > 100:
            history = history[-100:]
        
        # 保存更新的历史
        try:
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"保存历史记录失败: {e}")
    
    def _generate_trigger_summary(self, results: List[Dict], all_topics: List[TrendingTopic]) -> Dict[str, Any]:
        """生成触发汇总报告"""
        successful_generations = [r for r in results if r['status'] == 'success']
        failed_generations = [r for r in results if r['status'] != 'success']
        
        summary = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'analysis_summary': {
                'total_topics_analyzed': len(all_topics),
                'triggers_attempted': len(results),
                'successful_generations': len(successful_generations),
                'failed_generations': len(failed_generations)
            },
            'generated_articles': successful_generations,
            'failed_attempts': failed_generations,
            'top_topics_not_triggered': [
                {
                    'keyword': topic.keyword,
                    'trend_score': topic.trend_score,
                    'reason_not_triggered': self._analyze_why_not_triggered(topic)
                }
                for topic in all_topics[:5] 
                if topic.keyword not in [r['keyword'] for r in results]
            ],
            'next_monitoring_cycle': (
                datetime.now(timezone.utc) + timedelta(minutes=30)
            ).isoformat()
        }
        
        return summary
    
    def _analyze_why_not_triggered(self, topic: TrendingTopic) -> str:
        """分析为什么话题未被触发"""
        reasons = []
        
        if topic.trend_score < self.trigger_thresholds['min_trend_score']:
            reasons.append(f"趋势评分过低 ({topic.trend_score:.2f})")
        
        if topic.commercial_value < self.trigger_thresholds['min_commercial_value']:
            reasons.append(f"商业价值不足 ({topic.commercial_value:.2f})")
        
        if topic.urgency_score < self.trigger_thresholds['min_urgency_score']:
            reasons.append(f"紧急度不够 ({topic.urgency_score:.2f})")
        
        if topic.search_volume_est < self.trigger_thresholds['min_search_volume']:
            reasons.append(f"搜索量偏低 ({topic.search_volume_est:,})")
        
        if not self._check_competition_level(topic.competition_level):
            reasons.append(f"竞争过于激烈 ({topic.competition_level})")
        
        if self._check_recent_generation(topic.keyword):
            reasons.append("最近已生成相似内容")
        
        return "; ".join(reasons) if reasons else "未知原因"
    
    async def _send_trigger_notification(self, summary: Dict):
        """发送Telegram触发通知"""
        if not self.telegram_token or not self.telegram_chat_id:
            self.logger.warning("⚠️ Telegram配置不完整，跳过通知")
            return
        
        try:
            # 构建通知消息
            message = self._build_notification_message(summary)
            
            # 发送消息
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            payload = {
                'chat_id': self.telegram_chat_id,
                'text': message,
                'parse_mode': 'HTML',
                'disable_web_page_preview': True
            }
            
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                self.logger.info("📱 Telegram触发通知发送成功")
            else:
                self.logger.error(f"📱 Telegram通知发送失败: {response.status_code}")
                
        except Exception as e:
            self.logger.error(f"📱 发送Telegram通知异常: {e}")
    
    def _build_notification_message(self, summary: Dict) -> str:
        """构建通知消息"""
        analysis = summary['analysis_summary']
        generated = summary['generated_articles']
        
        # 基础信息
        message = f"""🔥 <b>实时热点触发报告</b>
        
📊 <b>分析概况</b>
• 分析话题: {analysis['total_topics_analyzed']} 个
• 触发生成: {analysis['triggers_attempted']} 个
• 成功生成: {analysis['successful_generations']} 个
• 失败生成: {analysis['failed_generations']} 个

"""
        
        # 成功生成的文章
        if generated:
            message += "✅ <b>成功生成文章</b>\n"
            for article in generated:
                message += f"• <code>{article['keyword']}</code>\n"
                message += f"  💰 预估收益: {article.get('estimated_revenue', 'N/A')}\n"
                message += f"  🎯 紧急度: {article.get('urgency_score', 0):.2f}\n\n"
        
        # 未触发的热门话题
        not_triggered = summary.get('top_topics_not_triggered', [])
        if not_triggered:
            message += "⏳ <b>监控中话题</b>\n"
            for topic in not_triggered[:3]:
                message += f"• <code>{topic['keyword']}</code> (评分: {topic['trend_score']:.2f})\n"
        
        # 下次检查时间
        next_check = datetime.fromisoformat(summary['next_monitoring_cycle'].replace('Z', '+00:00'))
        beijing_time = next_check.astimezone(pytz.timezone('Asia/Shanghai'))
        message += f"\n⏰ 下次检查: {beijing_time.strftime('%H:%M')}"
        
        return message
    
    def stop_monitoring(self):
        """停止监控"""
        self.monitoring_active = False
        self.logger.info("⏹️ 实时监控已停止")


# 手动触发接口
async def manual_trigger_check(force: bool = True) -> Dict[str, Any]:
    """手动触发检查（用于测试或紧急情况）"""
    trigger = RealtimeContentTrigger()
    return await trigger.check_and_trigger()


# 主要运行接口
async def start_realtime_monitoring(check_interval: int = 30):
    """启动实时监控（主要接口）"""
    trigger = RealtimeContentTrigger()
    await trigger.start_monitoring(check_interval)


# 测试和演示
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='实时内容生成触发器')
    parser.add_argument('--mode', choices=['monitor', 'check'], default='check',
                      help='运行模式: monitor=持续监控, check=单次检查')
    parser.add_argument('--interval', type=int, default=30,
                      help='监控间隔（分钟）')
    
    args = parser.parse_args()
    
    if args.mode == 'monitor':
        print(f"🚀 启动实时监控模式 - 间隔: {args.interval} 分钟")
        print("按 Ctrl+C 停止监控")
        asyncio.run(start_realtime_monitoring(args.interval))
    else:
        print("🔍 执行单次检查...")
        result = asyncio.run(manual_trigger_check())
        print(f"📊 检查完成: {result['analysis_summary']['successful_generations']} 篇文章已生成")