@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo DeepSeek TUI 启动中...
python main.py
if errorlevel 1 (
    echo.
    echo 启动失败，按任意键查看详情...
    pause >nul
    cd /d "%~dp0"
    python main.py --help
    echo.
    pause
)
