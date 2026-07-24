@echo off
REM Doble-clic aqui para reiniciar EasyPro en local (backend 8001 + frontend 5179).
REM Llama al script PowerShell que mata puertos ocupados y arranca todo con codigo fresco.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0dev-restart.ps1" %*
pause
