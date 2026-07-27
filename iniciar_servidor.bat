@echo off
cd /d "%~dp0"
call .venv\Scripts\activate
set PYTHONPATH=src
echo Iniciando Agente Corporativo MarketNova...
echo Abre tu navegador en: http://localhost:8000
echo Presiona Ctrl+C para detener el servidor.
echo.
python -m uvicorn src.api.main:app --port 8000
pause
