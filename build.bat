@echo off
setlocal
echo Stopping running GravPulse instances if any...
taskkill /F /IM GravPulse.exe >nul 2>&1
echo Building GravPulse Standalone Executable...
python -m PyInstaller GravPulse.spec
if %ERRORLEVEL% EQU 0 (
    copy /y dist\GravPulse.exe .
    echo.
    echo ===================================================
    echo Build successful! Executable is at dist\GravPulse.exe and GravPulse.exe
    echo ===================================================
) else (
    echo.
    echo Build failed with error code %ERRORLEVEL%.
)
endlocal
