#!/usr/bin/env python3
"""
快速提交推送工具
一键完成 git add + commit + push 流程

用法：
python scripts/quick_commit_push.py "你的提交消息"
python scripts/quick_commit_push.py "fix: 修复bug" --force
"""

import os
import sys
import subprocess
import codecs
from datetime import datetime

# 解决Windows编码问题
if sys.platform == "win32":
    try:
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
        sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())
    except Exception:
        pass

from auto_push import GitAutoPusher


def run_git_command(command: str) -> tuple:
    """执行Git命令"""
    try:
        # Windows下设置正确的编码环境
        env = os.environ.copy()
        if sys.platform == "win32":
            env['PYTHONIOENCODING'] = 'utf-8'
            env['LC_ALL'] = 'C.UTF-8'
        
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            env=env
        )
        
        if result.returncode == 0:
            return True, result.stdout.strip()
        else:
            return False, result.stderr.strip()
    except Exception as e:
        return False, str(e)


def quick_commit_push(commit_message: str, force: bool = False):
    """快速提交并推送"""
    print("⚡ 快速提交推送工具")
    print("=" * 30)
    
    # 1. 检查是否有更改
    print("📊 检查文件更改...")
    success, status_output = run_git_command("git status --porcelain")
    
    if not success:
        print("❌ 无法检查Git状态")
        return False
    
    if not status_output.strip():
        print("ℹ️ 没有需要提交的更改")
        return True
    
    # 显示要提交的文件
    changes = status_output.strip().split('\n')
    print(f"📝 发现 {len(changes)} 个文件更改:")
    for change in changes[:10]:  # 最多显示10个
        status_code = change[:2]
        file_name = change[3:]
        
        if status_code == "M ":
            print(f"   📄 修改: {file_name}")
        elif status_code == "A ":
            print(f"   ➕ 新增: {file_name}")
        elif status_code == "D ":
            print(f"   🗑️ 删除: {file_name}")
        elif status_code == "??":
            print(f"   ❓ 未跟踪: {file_name}")
        else:
            print(f"   📝 {status_code.strip()}: {file_name}")
    
    if len(changes) > 10:
        print(f"   ... 还有 {len(changes) - 10} 个文件")
    
    # 2. 添加所有更改
    print(f"\n📤 添加所有更改到暂存区...")
    success, output = run_git_command("git add -A")
    
    if not success:
        print(f"❌ 添加文件失败: {output}")
        return False
    
    print("✅ 文件添加成功")
    
    # 3. 提交更改
    print(f"\n💾 提交更改...")
    
    # 构建提交消息，自动添加标准后缀
    full_commit_message = f"""{commit_message}

🤖 Generated with Claude Code AI Assistant
Co-Authored-By: Claude <noreply@anthropic.com>"""
    
    # 避免f-string中的反斜杠问题
    escaped_message = full_commit_message.replace('"', '\\"')
    commit_command = f'git commit -m "{escaped_message}"'
    success, output = run_git_command(commit_command)
    
    if not success:
        if "nothing to commit" in output.lower():
            print("ℹ️ 没有需要提交的更改")
            return True
        else:
            print(f"❌ 提交失败: {output}")
            return False
    
    print("✅ 提交成功")
    
    # 4. 自动推送
    print(f"\n🚀 开始自动推送...")
    pusher = GitAutoPusher()
    success = pusher.auto_push(force=force)
    
    if success:
        print(f"\n🎉 完整流程成功!")
        print(f"   📝 提交消息: {commit_message}")
        print(f"   📤 已推送到远程仓库")
        return True
    else:
        print(f"\n⚠️ 提交成功，但推送失败")
        print(f"   💡 可以稍后手动推送: git push")
        return False


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="快速Git提交推送工具")
    parser.add_argument("message", help="提交消息")
    parser.add_argument("--force", action="store_true", help="强制推送")
    parser.add_argument("--dry-run", action="store_true", help="仅预览，不执行")
    
    args = parser.parse_args()
    
    if not args.message.strip():
        print("❌ 请提供提交消息")
        print("用法: python scripts/quick_commit_push.py \"你的提交消息\"")
        sys.exit(1)
    
    if args.dry_run:
        print("🔍 预览模式 - 不会实际执行操作")
        print(f"提交消息: {args.message}")
        print(f"强制推送: {args.force}")
        return
    
    try:
        success = quick_commit_push(args.message, args.force)
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n👋 用户取消操作")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 发生异常: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()