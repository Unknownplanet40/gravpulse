@echo off
cd /d "%~dp0"
if exist "run.vbs" (
    wscript //nologo "run.vbs"
    exit /b 0
)
if exist "C:\Python312\pythonw.exe" (
    start "" "C:\Python312\pythonw.exe" main.pyw
    exit /b 0
)
start "" pythonw main.pyw
exit /b 0
