@echo off
setlocal
echo Building GravPulse Standalone Executable...
python -m PyInstaller GravPulse.spec
if %ERRORLEVEL% EQU 0 (
    echo.
    echo ===================================================
    echo Build successful! Executable is at dist\GravPulse.exe
    echo ===================================================
) else (
    echo.
    echo Build failed with error code %ERRORLEVEL%.
)
endlocal
