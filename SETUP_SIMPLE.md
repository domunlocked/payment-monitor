# Local Windows setup

The local app keeps Telegram credentials, the authorized Telethon session, and the complete SQLite payment history on this PC. It binds only to `127.0.0.1:8765`. For optional phone access from anywhere, configure the protected HTTPS tunnel using [SIMPLE_SETUP.md](./SIMPLE_SETUP.md).

## Install and configure

1. Install Python 3.12 and run `install.bat`. It creates the existing `.venv` and does not replace an existing `.env`.
2. Generate a strong API key locally:

   ```powershell
   .\.venv\Scripts\python.exe -c "import secrets; print(secrets.token_urlsafe(48))"
   ```

   Put the value in `.env` as `API_TOKEN=...`. Use a new value if an old key may have been exposed.
3. Enter Telegram app ID/hash from [my.telegram.org](https://my.telegram.org/) in `.env`. Authorize the existing local session and list groups:

   ```powershell
   .\.venv\Scripts\python.exe listener.py --login
   .\.venv\Scripts\python.exe listener.py --list-groups
   ```

   Set the correct group ID in `TELEGRAM_CHAT_ID`. Telegram sign-in codes are entered only in this local terminal.

## Start and monitor

Double-click `start_payment_monitor.bat`, then use **Start Listening** on the local dashboard at [http://127.0.0.1:8765/](http://127.0.0.1:8765/). The listener processes new incoming notifications only, deduplicates transaction and source message IDs, and preserves the latest payment/history when stopped or restarted.

Install the tunnel and its Windows service as described in [SIMPLE_SETUP.md](./SIMPLE_SETUP.md) to enable phone access. `start_payment_monitor.bat` will attempt to start the `cloudflared` Windows service if present, and logs a local warning if unavailable; local Telegram monitoring still starts.

To start the monitor automatically at Windows sign-in, run `install_autostart.bat`. Run `remove_autostart.bat` to remove its Startup shortcut. Neither script removes `.env`, Telegram session, database, or logs.

## Important local settings

| Setting | Purpose |
| --- | --- |
| `TELEGRAM_API_ID`, `TELEGRAM_API_HASH` | Private Telegram user-session API credentials. |
| `TELEGRAM_CHAT_ID` | The one group to monitor. |
| `API_TOKEN` | Local dashboard session-signing secret. Do not send it to the phone or publish it. |
| `REMOTE_ACCESS_TOKEN` | Separate remote read-only phone key; configure together with `REMOTE_API_ORIGIN`. |
| `API_HOST` | Must remain `127.0.0.1`. |
| `API_PORT` | Must remain `8765`. |
| `DATABASE_PATH` | Existing SQLite history path; keep it unchanged to preserve data. |
| `REMOTE_API_ORIGIN` | Optional HTTPS tunnel origin. Must match the hostname in `remote-config.js`. |

Keep `.env`, `payment-monitor.session`, SQLite files, logs, tunnel credentials, and local backups out of GitHub. The phone needs a real Khmer browser speech voice; if none is installed, payments appear but are not spoken. Mobile browsers may suspend speech while the page is backgrounded or closed.
