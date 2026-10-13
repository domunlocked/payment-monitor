# Simple Windows Setup

This guide runs the Payment Monitor dashboard and Telegram listener on this Windows computer only. The service uses `127.0.0.1:8765`; it does not open router ports or expose payment data to GitHub Pages.

## 1. Install the project

1. Install Python 3.12 (or 3.11) from [python.org](https://www.python.org/downloads/windows/). Enable the Python Launcher during installation.
2. Open this project folder in File Explorer and double-click `install.bat`. Wait for it to finish.
3. `install.bat` creates `.venv` and creates `.env` only if `.env` does not already exist. It never replaces an existing `.env`.
4. Open `.env` in VS Code. Do not paste its contents into chat, screenshots, logs, or GitHub.

## 2. Set a private API key

Generate a strong private API key locally:

```powershell
.\.venv\Scripts\python.exe -c "import secrets; print(secrets.token_urlsafe(48))"
```

Copy the generated value directly into the `API_TOKEN=` line in `.env`. Keep it private. The website does not ask for this value; the Python service uses it to sign a short-lived, `HttpOnly`, same-origin browser session.

## 3. Add Telegram settings

1. Go to [my.telegram.org](https://my.telegram.org/) and sign in with the Telegram account that is already in the payment group.
2. Open **API development tools** and create an application if needed.
3. Put the numeric app ID in `TELEGRAM_API_ID` and the API hash in `TELEGRAM_API_HASH` in `.env`. These are user-session credentials, not a bot token. Never publish them.
4. Leave `TELEGRAM_CHAT_ID` empty until you identify the correct group. The app can show the dashboard even before the Telegram fields are complete.
5. In PowerShell, from this project folder, authorize the existing local Telethon session:

   ```powershell
   .\.venv\Scripts\python.exe listener.py --login
   ```

   Enter your phone number and Telegram's one-time login code in the local terminal if requested. Enter your two-step-verification password there if Telegram asks. The app reuses `payment-monitor.session`; do not delete or share it.
6. List groups without sending a message:

   ```powershell
   .\.venv\Scripts\python.exe listener.py --list-groups
   ```

   Copy the ID of the correct PayWay payment group into `TELEGRAM_CHAT_ID` in `.env`. The account must already be a member of the group. Do not use the payment bot's username as the group.

## 4. Start and test locally

1. Double-click `start_payment_monitor.bat`. It starts the local API in a minimized console and opens `http://127.0.0.1:8765/`. If another copy is already responding, it reuses it instead of opening a second server.
2. Confirm the screen says **Disconnected** before starting Telegram. Click **Start Listening**.
3. When authorized and connected, the status changes to **Connected**. New valid notifications from the configured group are parsed and written to the existing `payment_history.sqlite3`. Duplicate transaction IDs are ignored.
4. The dashboard refreshes every few seconds without a manual refresh. It shows the newest saved transaction or **Waiting for payment…** when no transaction exists. Stopping listening does not delete the last payment or database history.
5. Click **Stop Listening** to stop Telegram monitoring while leaving the dashboard running.

The listener processes new Telegram events only; it does not fetch old group messages at startup. The API may show the latest transaction already stored in the database.

### Safe local checks

In PowerShell opened at the project folder:

```powershell
.\.venv\Scripts\python.exe -m pytest -v
node --check app.js
Invoke-RestMethod http://127.0.0.1:8765/healthz
```

The health endpoint reports only that the local API is running. Unit tests use fake payment records and do not log in to Telegram. Never test by sending a fake payment into the real group.

## 5. Optional: start monitoring at Windows sign-in

First complete Telegram sign-in and configure the group ID. Then double-click `install_autostart.bat`. It adds one shortcut to the current Windows user's Startup folder; no administrator account or scheduled task is created.

At the next Windows sign-in, the shortcut starts the local API, attempts to start Telegram monitoring, and opens the dashboard. If the session needs authorization or Telegram settings are missing, the dashboard reports that; it will not ask for a login code in the background. Complete the one-time sign-in manually using the command above.

To remove automatic startup, double-click `remove_autostart.bat`. This removes only the Payment Monitor shortcut and does not delete your `.env`, Telegram session, database, payment history, or logs.

## Settings in `.env`

| Setting | Purpose |
| --- | --- |
| `TELEGRAM_API_ID` | Numeric app ID from `my.telegram.org`. |
| `TELEGRAM_API_HASH` | Private Telegram app hash from `my.telegram.org`. |
| `TELEGRAM_CHAT_ID` | Numeric ID or supported public username of the single group to monitor. |
| `API_TOKEN` | Private random key used server-side to sign browser sessions. Never put it in HTML, JavaScript, or GitHub Pages. |
| `API_HOST` | Must remain `127.0.0.1`; other bind addresses are rejected. |
| `API_PORT` | Local port; the supplied setup uses `8765`. |
| `DATABASE_PATH` | Existing SQLite file path. Keep its current value to preserve history. |
| `RETENTION_DAYS` | How long payment rows are retained. |
| `LOG_LEVEL` | Local log detail, normally `INFO`. |

An old `CORS_ORIGINS` line in an existing `.env` is ignored. The local API has no CORS access for GitHub Pages or other websites.

## Troubleshooting

- **The page does not open:** check `logs\listener.log` and `logs\console.log`; make sure nothing else is using port 8765.
- **Telegram setup message:** fill in the named missing `.env` variables, then click Start again.
- **One-time login required:** run `.\.venv\Scripts\python.exe listener.py --login` in a normal local PowerShell window. Do not enter codes in the browser.
- **Connected but no payment appears:** confirm the correct `TELEGRAM_CHAT_ID`, that the signed-in account is in that group, and that the bot posts new ABA payment notifications there. Old messages are not replayed.
- **GitHub Pages shows disconnected:** expected. Open the local address on the Windows computer; Pages cannot reach this loopback-only service.
- **Khmer voice:** the dashboard shows Khmer amount words as text. The Windows voices previously checked were English-only; no real Khmer voice has been verified. The monitor does not claim to speak Khmer or substitute an English voice.
- **Private data:** customer names and transaction IDs are sensitive. Keep `.env`, `payment-monitor.session`, SQLite files, logs, and local backups out of GitHub.

## Repository checks

```powershell
.\.venv\Scripts\python.exe -m pytest -v
node --check app.js
```
