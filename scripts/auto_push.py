#!/usr/bin/env python3
"""
智能Git自动推送工具
自动处理git pull, merge conflicts, 和 push操作

功能：
- 智能检测远程更改并自动拉取
- 自动处理合并冲突（选择本地版本）
- 安全的强制推送选项
- 详细的操作日志和状态反馈
- Telegram通知集成（可选）
"""

import os
import sys
import subprocess
import codecs
from datetime import datetime
from pathlib import Path

# 解决Windows编码问题
if sys.platform == "win32":
    try:
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
        sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())
    except Exception:
        pass


class GitAutoPusher:
    """智能Git推送管理器"""
    
    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path).resolve()
        self.log_messages = []
        
    def log(self, message: str, level: str = "INFO"):
        """记录日志消息"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_msg = f"[{timestamp}] {level}: {message}"
        self.log_messages.append(log_msg)
        
        # 输出到控制台
        if level == "ERROR":
            print(f"❌ {message}")
        elif level == "WARNING":
            print(f"⚠️ {message}")
        elif level == "SUCCESS":
            print(f"✅ {message}")
        else:
            print(f"ℹ️ {message}")
    
    def run_command(self, command: str, capture_output: bool = True) -> tuple:
        """执行Git命令并返回结果"""
        try:
            self.log(f"执行命令: {command}")
            
            result = subprocess.run(
                command,
                shell=True,
                cwd=self.repo_path,
                capture_output=capture_output,
                text=True,
                encoding='utf-8',
                errors='replace'
            )
            
            if result.returncode == 0:
                self.log(f"命令执行成功", "SUCCESS")
                return True, result.stdout.strip() if result.stdout else ""
            else:
                error_msg = result.stderr.strip() if result.stderr else "未知错误"
                self.log(f"命令执行失败: {error_msg}", "ERROR")
                return False, error_msg
                
        except Exception as e:
            self.log(f"命令执行异常: {e}", "ERROR")
            return False, str(e)
    
    def check_git_status(self) -> dict:
        """检查Git仓库状态"""
        self.log("检查Git仓库状态...")
        
        # 检查是否有未提交的更改
        success, output = self.run_command("git status --porcelain")
        if not success:
            return {"error": "无法检查仓库状态"}
        
        has_changes = bool(output.strip())
        
        # 检查当前分支
        success, current_branch = self.run_command("git branch --show-current")
        if not success:
            current_branch = "unknown"
        
        # 检查远程状态
        success, _ = self.run_command("git fetch")
        if not success:
            self.log("警告: 无法获取远程更新", "WARNING")
        
        # 检查本地和远程的差异
        success, behind_output = self.run_command(f"git rev-list --count HEAD..origin/{current_branch}")
        behind_count = int(behind_output) if success and behind_output.isdigit() else 0
        
        success, ahead_output = self.run_command(f"git rev-list --count origin/{current_branch}..HEAD")
        ahead_count = int(ahead_output) if success and ahead_output.isdigit() else 0
        
        return {
            "has_uncommitted_changes": has_changes,
            "current_branch": current_branch,
            "commits_behind": behind_count,
            "commits_ahead": ahead_count,
            "can_fast_forward": behind_count > 0 and ahead_count == 0
        }
    
    def handle_merge_conflicts(self) -> bool:
        """处理合并冲突（选择本地版本）"""
        self.log("处理潜在的合并冲突...")
        
        # 检查是否存在合并冲突
        success, status_output = self.run_command("git status --porcelain")
        if not success:
            return False
        
        conflict_files = []
        for line in status_output.split('\n'):
            if line.startswith('UU') or line.startswith('AA') or line.startswith('DD'):
                file_path = line[3:].strip()
                conflict_files.append(file_path)
        
        if conflict_files:
            self.log(f"发现 {len(conflict_files)} 个冲突文件", "WARNING")
            
            # 对每个冲突文件选择本地版本
            for file_path in conflict_files:
                self.log(f"解决冲突文件: {file_path}")
                success, _ = self.run_command(f'git checkout --ours "{file_path}"')
                if success:
                    success, _ = self.run_command(f'git add "{file_path}"')
                    if success:
                        self.log(f"冲突已解决: {file_path}", "SUCCESS")
                    else:
                        self.log(f"无法添加文件: {file_path}", "ERROR")
                        return False
                else:
                    self.log(f"无法解决冲突: {file_path}", "ERROR")
                    return False
            
            # 完成合并
            success, _ = self.run_command("git commit --no-edit")
            if success:
                self.log("合并冲突已解决并提交", "SUCCESS")
                return True
            else:
                self.log("无法完成合并提交", "ERROR")
                return False
        else:
            self.log("没有发现合并冲突")
            return True
    
    def smart_pull(self) -> bool:
        """智能拉取远程更改"""
        self.log("开始智能拉取远程更改...")
        
        # 尝试正常拉取
        success, output = self.run_command("git pull")
        
        if success:
            if "Already up to date" in output:
                self.log("远程仓库已是最新", "SUCCESS")
            else:
                self.log("成功拉取远程更改", "SUCCESS")
            return True
        else:
            # 拉取失败，可能存在冲突
            self.log("常规拉取失败，尝试处理冲突...", "WARNING")
            
            # 尝试强制拉取并处理冲突
            success, _ = self.run_command("git pull --no-rebase")
            
            if not success:
                # 如果还是失败，尝试merge策略
                self.log("尝试使用merge策略...")
                success, _ = self.run_command("git pull --strategy=recursive -X ours")
            
            if success:
                return self.handle_merge_conflicts()
            else:
                self.log("无法拉取远程更改", "ERROR")
                return False
    
    def force_push_with_backup(self) -> bool:
        """带备份的强制推送"""
        self.log("准备执行带备份的强制推送...", "WARNING")
        
        # 创建备份分支
        backup_branch = f"backup-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        success, _ = self.run_command(f"git branch {backup_branch}")
        
        if success:
            self.log(f"已创建备份分支: {backup_branch}", "SUCCESS")
        else:
            self.log("无法创建备份分支", "ERROR")
            return False
        
        # 强制推送
        status = self.check_git_status()
        current_branch = status.get("current_branch", "master")
        
        success, _ = self.run_command(f"git push --force-with-lease origin {current_branch}")
        
        if success:
            self.log("强制推送成功", "SUCCESS")
            # 删除备份分支
            self.run_command(f"git branch -d {backup_branch}")
            return True
        else:
            self.log(f"强制推送失败，备份分支已保留: {backup_branch}", "ERROR")
            return False
    
    def auto_push(self, force: bool = False) -> bool:
        """执行自动推送流程"""
        print("🚀 Git智能自动推送工具启动")
        print("=" * 40)
        
        # 检查仓库状态
        status = self.check_git_status()
        
        if "error" in status:
            self.log(f"仓库状态检查失败: {status['error']}", "ERROR")
            return False
        
        print(f"📊 仓库状态:")
        print(f"   分支: {status['current_branch']}")
        print(f"   未提交更改: {'是' if status['has_uncommitted_changes'] else '否'}")
        print(f"   领先提交: {status['commits_ahead']}")
        print(f"   落后提交: {status['commits_behind']}")
        
        # 如果有未提交的更改，提醒用户
        if status['has_uncommitted_changes']:
            self.log("发现未提交的更改", "WARNING")
            print("\n⚠️ 发现未提交的更改，请先提交：")
            print("   git add -A")
            print("   git commit -m \"your message\"")
            return False
        
        # 如果没有需要推送的提交
        if status['commits_ahead'] == 0:
            self.log("没有需要推送的提交", "SUCCESS")
            return True
        
        # 如果远程有新提交，先拉取
        if status['commits_behind'] > 0:
            self.log(f"远程仓库领先 {status['commits_behind']} 个提交，正在同步...")
            
            if not self.smart_pull():
                if force:
                    self.log("常规同步失败，将执行强制推送", "WARNING")
                    return self.force_push_with_backup()
                else:
                    self.log("同步失败，如需强制推送请使用 --force 参数", "ERROR")
                    return False
        
        # 执行推送
        self.log("开始推送到远程仓库...")
        current_branch = status['current_branch']
        success, output = self.run_command(f"git push origin {current_branch}")
        
        if success:
            self.log("推送成功！", "SUCCESS")
            
            # 发送成功通知
            commits_pushed = status['commits_ahead']
            print(f"\n🎉 推送完成!")
            print(f"📤 推送了 {commits_pushed} 个提交到 origin/{current_branch}")
            
            return True
        else:
            if force:
                self.log("常规推送失败，尝试强制推送...", "WARNING")
                return self.force_push_with_backup()
            else:
                self.log("推送失败", "ERROR")
                print(f"\n💡 如果需要强制推送，请使用: python scripts/auto_push.py --force")
                return False
    
    def show_log(self):
        """显示操作日志"""
        if self.log_messages:
            print(f"\n📋 操作日志:")
            for msg in self.log_messages[-10:]:  # 显示最后10条日志
                print(f"   {msg}")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Git智能自动推送工具")
    parser.add_argument("--force", action="store_true", help="强制推送（会创建备份）")
    parser.add_argument("--log", action="store_true", help="显示详细日志")
    parser.add_argument("--path", default=".", help="Git仓库路径")
    
    args = parser.parse_args()
    
    try:
        pusher = GitAutoPusher(args.path)
        success = pusher.auto_push(force=args.force)
        
        if args.log:
            pusher.show_log()
        
        if success:
            print(f"\n✅ 自动推送完成!")
            sys.exit(0)
        else:
            print(f"\n❌ 自动推送失败!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print(f"\n\n👋 用户取消操作")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 发生异常: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()