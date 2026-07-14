@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo   PAI 排课系统 - 一键启动
echo ========================================
echo.

:: 获取脚本所在目录
set "ROOT_DIR=%~dp0"
set "BACKEND_DIR=%ROOT_DIR%backend\paiclass"
set "FRONTEND_DIR=%ROOT_DIR%frontend"

:: 检查 Python 虚拟环境
if not exist "%BACKEND_DIR%\venv\Scripts\python.exe" (
    echo [错误] 未找到 Python 虚拟环境
    echo 请先创建虚拟环境: cd backend\paiclass ^&^& python -m venv venv
    pause
    exit /b 1
)

:: 检查 node_modules
if not exist "%FRONTEND_DIR%\node_modules" (
    echo [提示] 首次运行，正在安装前端依赖...
    cd /d "%FRONTEND_DIR%"
    call pnpm install
    if errorlevel 1 (
        echo [错误] 前端依赖安装失败
        pause
        exit /b 1
    )
    echo.
)

echo [1/2] 启动后端服务器...
start "PAI 后端" cmd /k "cd /d "%BACKEND_DIR%" && call venv\Scripts\activate && python manage.py runserver"

:: 等待后端启动
timeout /t 2 /nobreak >nul

echo [2/2] 启动前端服务器...
start "PAI 前端" cmd /k "cd /d "%FRONTEND_DIR%" && pnpm dev"

echo.
echo ========================================
echo   启动完成！
echo ========================================
echo.
echo   后端: http://localhost:8000
echo   前端: http://localhost:5173
echo.
echo   关闭此窗口不会影响服务运行
echo   如需停止服务，请关闭对应的终端窗口
echo ========================================
echo.

pause
