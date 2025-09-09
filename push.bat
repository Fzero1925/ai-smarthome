@echo off
chcp 65001 >nul
title Git Auto Push Tool

echo.
echo 🚀 Git自动推送工具
echo ==================

REM 检查是否提供了提交消息
if "%~1"=="" (
    echo ❌ 请提供提交消息
    echo.
    echo 用法:
    echo   push "你的提交消息"
    echo   push "fix: 修复bug" --force
    echo.
    pause
    exit /b 1
)

REM 执行Python脚本
python scripts\quick_commit_push.py %*

REM 检查执行结果
if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ 操作完成!
) else (
    echo.
    echo ❌ 操作失败!
)

echo.
pause