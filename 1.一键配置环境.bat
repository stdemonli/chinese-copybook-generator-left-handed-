@echo off
chcp 65001
echo =======================================================
echo 正在为您配置字帖生成器运行环境...
echo 智能检测系统中的Python环境（支持官方Python、Anaconda等）
echo =======================================================

set "PYTHON_CMD="
set "PYTHON_VERSION="

echo.
echo [1/4] 正在智能检测Python环境...

REM 检测python命令
python --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do set "PYTHON_VERSION=%%i"
    set "PYTHON_CMD=python"
    echo ✓ 检测到官方Python: %PYTHON_VERSION%
    goto :python_found
)

REM 检测python3命令
python3 --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=2" %%i in ('python3 --version 2^>^&1') do set "PYTHON_VERSION=%%i"
    set "PYTHON_CMD=python3"
    echo ✓ 检测到Python3: %PYTHON_VERSION%
    goto :python_found
)

REM 检测conda环境
conda --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ 检测到Anaconda/Conda环境
    set "PYTHON_CMD=python"
    echo 将使用conda环境中的Python
    goto :python_found
)

REM 检查Anaconda安装
where anaconda >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ 检测到Anaconda安装
    set "PYTHON_CMD=anaconda"
    goto :python_found
)

REM 检查是否有其他Python相关命令
dir /b "%SystemRoot%\py.exe" >nul 2>&1
if exist "%SystemRoot%\py.exe" (
    %SystemRoot%\py --version >nul 2>&1
    if !errorlevel! equ 0 (
        for /f "tokens=2" %%i in ('%SystemRoot%\py --version 2^>^&1') do set "PYTHON_VERSION=%%i"
        set "PYTHON_CMD=%SystemRoot%\py"
        echo ✓ 检测到Windows Python Launcher: %PYTHON_VERSION%
        goto :python_found
    )
)

echo.
echo [错误] 未检测到可用的Python环境！
echo.
echo 请确保以下任一方式已安装Python：
echo 1. 官方Python (python.org) - 建议勾选"Add Python to PATH"
echo 2. Anaconda - 从 anaconda.com 下载安装
echo 3. 其他Python发行版
echo 4. 确保Python命令已在系统PATH中
echo.
echo 常见解决方案：
echo - 重新安装Python并勾选"Add Python to PATH"
echo - 重启命令行窗口
echo - 检查环境变量PATH设置
echo.
pause
exit /b 1

:python_found
echo.
echo [2/4] 正在创建独立的虚拟环境 (venv)...
if not exist "venv" (
    if "%PYTHON_CMD%"=="anaconda" (
        anaconda -m venv venv
    ) else (
        %PYTHON_CMD% -m venv venv
    )
    if !errorlevel! equ 0 (
        echo 虚拟环境创建成功。
    ) else (
        echo [警告] 使用现有Python环境继续...
    )
) else (
    echo 虚拟环境已存在，跳过创建。
)

echo.
echo [3/4] 正在激活虚拟环境...
call venv\Scripts\activate.bat >nul 2>&1
if !errorlevel! neq 0 (
    echo [警告] 虚拟环境激活失败，将尝试直接安装...
)

echo.
echo [4/4] 正在通过国内镜像源安装依赖库...
echo 正在连接清华大学镜像源...
if "%PYTHON_CMD%"=="anaconda" (
    anaconda -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
) else (
    %PYTHON_CMD% -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
)

echo.
echo ======================================================
if %errorlevel% equ 0 (
    echo [成功] 环境配置完成！
    echo 检测到的Python版本: %PYTHON_VERSION%
    echo 以后请直接点击 "2.启动字帖生成器.bat" 使用。
) else (
    echo [警告] 依赖安装可能有问题，但配置流程已完成
    echo 请检查网络连接或尝试手动安装依赖
    echo 运行命令: venv\Scripts\pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
)
echo ======================================================
pause