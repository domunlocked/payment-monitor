# Payment Monitor

A small, local-only Windows dashboard for monitoring new ABA PayWay payment notices from one configured Telegram group. The Python service parses incoming notices, stores unique transactions in the existing SQLite database, and shows the latest payment in the browser.

## Important privacy limits

- The dashboard and API bind only to `127.0.0.1:8765`. They are available on the Windows computer running the app, not on a phone over Wi-Fi or from GitHub Pages.
- GitHub Pages can host static files, but it cannot access this computer's Telegram session or database. The public static page deliberately does not call a remote API.
- There is no public tunnel, router port, permissive CORS, or remote access in this setup.
- Payment names and transaction references are private customer data. Keep `.env`, `payment-monitor.session`, `payment_history.sqlite3`, logs, and backups off GitHub.
- The Windows machine checked for this project had English voices only. Khmer number text is displayed, but a real Khmer voice was not available there and English is never used as a substitute.

## Quick setup

See [SETUP_SIMPLE.md](./SETUP_SIMPLE.md) for beginner-friendly Windows installation, Telegram sign-in, listener start/stop, testing, and optional Windows sign-in startup.

## Developer checks

```powershell
.\.venv\Scripts\python.exe -m pytest -v
node --check app.js
```

The automated tests use synthetic payment messages and do not connect to Telegram. A real Telegram sign-in and a live payment notification must be tested on the owner's Windows computer.
