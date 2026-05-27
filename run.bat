@echo off
cd /d "%~dp0"
if exist .env (
    for /f "tokens=1,* delims==" %%a in (.env) do (
        if "%%a"=="DEEPSEEK_API_KEY" set DEEPSEEK_API_KEY=%%b
    )
)
python main.py
pause
