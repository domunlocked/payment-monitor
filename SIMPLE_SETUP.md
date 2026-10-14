# Payment Monitor — Windows startup and phone dashboard

Your Windows PC runs the existing FastAPI dashboard, Telethon listener, parser, and SQLite database. The scheduled task runs `start_payment_monitor.bat`, which uses this project's `.venv\Scripts\python.exe` and keeps the service process attached to Task Scheduler so it can retry failures. A process lock prevents a second local service from starting.

The current application intentionally hosts the API and Telegram listener in one Python process. Telegram reconnects automatically when its network connection drops, and Task Scheduler restarts the complete app if that process exits. A process-level crash therefore restarts both; they are not isolated as separate processes.

The phone website stays on GitHub Pages. For access from mobile data, configure the existing Cloudflare Tunnel and remote key as described below; GitHub Pages cannot reach `localhost` directly. Telegram credentials, the Telegram session file, `API_TOKEN`, and the SQLite database stay on the PC. Never put these values in website files or Git.

## First-time startup installation

1. Finish the local setup in the existing `.env`: Telegram app ID/hash, authorized session, group ID, and valid private `API_TOKEN`. To authorize once from the PC terminal:

   ```powershell
   .\.venv\Scripts\python.exe listener.py --login
   .\.venv\Scripts\python.exe listener.py --list-groups
   ```

   The `payment-monitor.session` file remains on this PC. Set the correct `TELEGRAM_CHAT_ID` in `.env`.
2. From File Explorer, **double-click `setup_startup.bat` first**. It creates or replaces one current-user Task Scheduler task named `PaymentMonitorListener`, with a 30-second logon delay, no administrator permission, and restart-on-failure settings. It gracefully stops an already-running copy before starting the managed task. Re-running the installer updates the same named task; it does not create duplicates.
3. If Windows asks whether to allow the action, approve it as your current user. The batch file uses only `.venv\Scripts\python.exe`; it does not install global packages.
4. The dashboard opens in the default browser after sign-in. Double-click `check_listener.bat` to verify the service. Expected output includes `Listener process: running` and `Telegram connection: connected`. If Telegram is still reconnecting, the process should remain running and retry.

## Start immediately, check, and stop

- **Start the dashboard and Telegram listener now without changing startup settings:** double-click `start_payment_monitor.bat`. It reuses an existing service and requests Telegram start rather than opening a duplicate. To also install Windows startup and start it now, double-click `setup_startup.bat`.
- **Check status:** double-click `check_listener.bat`. It asks the existing loopback API for listener state and connection status. It does not print credentials.
- **Stop the complete service safely:** double-click `stop_payment_monitor.bat`. This asks the API to stop Telegram and shut down gracefully. The startup task remains installed and runs again at your next sign-in. To stop only Telegram while keeping the API dashboard open, use `stop_listener.bat`.
- Closing the dashboard browser does not stop the listener. Closing the Task Scheduler task or shutting down Windows does.

## Disable automatic startup

Open PowerShell as the same Windows user and run:

```powershell
Disable-ScheduledTask -TaskName PaymentMonitorListener
```

The task stays installed but will not run on sign-in until enabled again.

To re-enable later, double-click `setup_startup.bat` again. To remove the task entirely instead:

```powershell
Unregister-ScheduledTask -TaskName PaymentMonitorListener -Confirm:$false
```

These commands do not delete the database, `.env`, Telegram session, logs, or backups.

## Phone dashboard and speech

The remote phone view is optional and requires the existing Cloudflare Tunnel:

1. In Cloudflare, configure the tunnel hostname to route to `http://127.0.0.1:8765`. The tunnel uses outbound connections; do not open router ports. A stable custom hostname needs a domain, which may cost money. Cloudflare's free plan and limits can change.
2. Keep `API_HOST=127.0.0.1` and `API_PORT=8765` in `.env`. Configure:

   ```dotenv
   REMOTE_API_ORIGIN=https://payments.YOUR-DOMAIN
   REMOTE_ACCESS_TOKEN=YOUR_SEPARATE_LONG_RANDOM_PHONE_KEY
   ```

   Generate a key locally with:

   ```powershell
   .\.venv\Scripts\python.exe -c "import secrets; print(secrets.token_urlsafe(48))"
   ```

   Keep it only in `.env`; it is separate from `API_TOKEN`. Anyone with this read-only key can see the minimized remote payment details.
3. Set the public HTTPS hostname (not a secret) as `apiBaseUrl` in `remote-config.js`. Publish that website configuration through the existing reviewed GitHub workflow. Do not put either token, tunnel credential, or Telegram credential in public files.
4. Open [https://domunlocked.github.io/payment-monitor/](https://domunlocked.github.io/payment-monitor/) on the phone, enter `REMOTE_ACCESS_TOKEN`, press **Connect**, turn **Speaker On**, then tap **Start Listening**. New transactions are polled; existing history is loaded silently. A Khmer browser speech voice (`km`) is required; without one, the dashboard shows payments but does not speak. Speech cannot be guaranteed when the phone tab is suspended or closed.

When the PC or tunnel is offline, the phone reports disconnected and retries. Local payment records remain in the PC's existing SQLite database; there is no cloud database or history upload.

## Troubleshooting

- **Task installed but listener not running:** double-click `check_listener.bat`; open Task Scheduler → Task Scheduler Library → `PaymentMonitorListener` and check Last Run Result. Check `logs\listener.log` and `logs\console.log`. Logs should contain error types/status only, not tokens.
- **Telegram says setup required:** check the named variables in local `.env`. Do not paste `.env` or logs in chat.
- **Needs one-time login:** run `.\.venv\Scripts\python.exe listener.py --login` in a normal local terminal. Login codes are entered on the PC only.
- **Task cannot be created:** confirm you are signed in as the Windows user that should run the app, then retry `setup_startup.bat`. It is a current-user task and normally needs no administrator permission.
- **Task reports running but Telegram disconnected:** the listener is retrying. Check internet access, Telegram availability, the group ID, and the private listener log.
- **Task will not start another copy:** the project lock is intentional. Check the existing dashboard at `http://127.0.0.1:8765/`; it may already be running. Use `check_listener.bat`.
- **Phone cannot connect:** confirm the Cloudflare service is running and that `.env` `REMOTE_API_ORIGIN` matches public `remote-config.js`. Keep the local API bound to loopback.
- Keep `.env`, `payment-monitor.session`, SQLite files, logs, Cloudflare tunnel credentials, and backups out of GitHub. The repository `.gitignore` excludes local private data.

## Automated checks

From PowerShell in the project folder:

```powershell
.\.venv\Scripts\python.exe -m pytest -v
node --check app.js
node --test tests\test_payment_notifications.test.js tests\test_phone_speech.test.js
```

The tests use synthetic payment fixtures; they do not sign in to Telegram or register a Windows scheduled task.
