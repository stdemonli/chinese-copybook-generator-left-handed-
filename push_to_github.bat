@echo off
chcp 65001
echo =======================================================
echo 正在推送代码到GitHub...
echo =======================================================

REM 添加远程仓库（请替换为您的实际仓库地址）
git remote add origin https://github.com/您的用户名/chinese-copybook-generator.git

REM 切换到main分支
git branch -M main

REM 推送到GitHub
git push -u origin main

echo =======================================================
if %errorlevel% equ 0 (
    echo [成功] 代码已成功推送到GitHub！
    echo 请访问您的GitHub仓库查看结果
) else (
    echo [错误] 推送失败，请检查网络连接或仓库地址
)
echo =======================================================
pause