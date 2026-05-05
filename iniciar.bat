@echo off
cd /d "%~dp0"
echo.
echo   Iniciando Facturador RJCH...
start /b python server.py
timeout /t 2 /nobreak >nul
start http://localhost:3000
echo.
echo   Facturador abierto en http://localhost:3000
echo   Cierra esta ventana para detener el servidor.
echo.
pause
