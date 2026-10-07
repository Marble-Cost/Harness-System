@echo off
REM Cerebro de IA - enciende el cerebro (servidor solo local, 127.0.0.1).
REM Para apagarlo, cierre esta ventana.
cd /d "%~dp0"
echo Actualizando las neuronas del proyecto...
python cerebro.py
echo.
start "" "http://127.0.0.1:8765/visor.html"
python servidor_cerebro.py
