@echo off
setlocal
cd /d "%~dp0"

where py >nul 2>nul
if errorlevel 1 (
    echo Python 3.11 or 3.12 with the Windows Python launcher is required.
    echo Install it from https://www.python.org/downloads/windows/ and select "Add Python to PATH".
    pause
    exit /b 1
)

if exist ".venv\Scripts\python.exe" goto install_dependencies
py -3.12 --version >nul 2>nul
if not errorlevel 1 (
    py -3.12 -m venv .venv
    if errorlevel 1 goto failed
    goto install_dependencies
)
py -3.11 --version >nul 2>nul
if not errorlevel 1 (
    py -3.11 -m venv .venv
    if errorlevel 1 goto failed
    goto install_dependencies
)
echo Install Python 3.11 or 3.12, then run this installer again.
pause
exit /b 1

:install_dependencies
echo Installing free Python packages...
".venv\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 goto failed
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto failed

if not exist ".env" (
    copy /y ".env.example" ".env" >nul
    if errorlevel 1 goto failed
    powershell -NoProfile -ExecutionPolicy Bypass -Command "$p='.env'; $r=New-Object byte[] 48; $g=[Security.Cryptography.RandomNumberGenerator]::Create(); $g.GetBytes($r); $g.Dispose(); $t=[Convert]::ToBase64String($r).TrimEnd('=').Replace('+','-').Replace('/','_'); (Get-Content $p -Raw).Replace('replace-this-with-a-private-random-token',$t) | Set-Content $p -Encoding ascii"
    if errorlevel 1 goto failed
)
echo.
echo Installation complete. Edit .env with your Telegram API credentials and group ID.
echo Read README.md before connecting a phone or enabling remote access.
pause
exit /b 0

:failed
echo Installation failed. Check the error above and your Python or internet installation.
pause
exit /b 1
