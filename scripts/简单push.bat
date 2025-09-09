@echo off
echo ===========================================
echo AI Smart Home Hub 一键Push脚本
echo ===========================================
echo.

REM 获取用户输入的提交消息
set /p commit_msg="请输入提交消息: "

echo.
echo 正在添加文件...
git add .

echo 正在创建提交...
git commit -m "%commit_msg%"

echo 正在推送到GitHub...
git push origin main

echo.
echo 推送完成！
echo.
pause