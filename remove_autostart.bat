@echo off
setlocal
powershell -NoProfile -ExecutionPolicy Bypass -Command "$shortcutPath = Join-Path $env:APPDATA 'Microsoft\Windows\Start Menu\Programs\Startup\Payment Monitor.lnk'; if (Test-Path -LiteralPath $shortcutPath) { Remove-Item -LiteralPath $shortcutPath -Force }; if (Test-Path -LiteralPath $shortcutPath) { exit 1 }"
if errorlevel 1 (
    echo Could not remove the Payment Monitor startup shortcut.
    pause
    exit /b 1
)
echo Automatic startup is removed. Your .env, Telegram session, and payment database are unchanged.
pause
exit /b 0
