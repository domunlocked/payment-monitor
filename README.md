# Payment Monitor

A small Windows application for monitoring new ABA PayWay payment notices from one configured Telegram group. The PC remains the only Telegram client and keeps full local SQLite history. A protected Cloudflare Tunnel can let the existing GitHub Pages dashboard poll the PC directly; there is no cloud database or account login.

## Important privacy limits

- The local dashboard and API bind only to `127.0.0.1:8765`; no router port is opened.
- The optional tunnel is HTTPS and read-only for the remote dashboard. It requires a separate private `REMOTE_ACCESS_TOKEN`, accepts browser access only from this GitHub Pages origin, and returns minimized payment fields. It does not reuse the local `API_TOKEN`.
- The remote key is entered by the owner and kept in the active browser tab's session storage; it is never embedded in public JavaScript. Anyone who obtains it can view the returned payment history.
- The Windows API does not expose Telegram controls or CSV export remotely. Telegram credentials and the complete SQLite database stay on the PC.
- Payment names and transaction references are private customer data. Keep `.env`, `payment-monitor.session`, `payment_history.sqlite3`, logs, and backups off GitHub.
- Phone announcements require a real Khmer voice in the phone browser. If unavailable, the app displays payments but does not substitute an English voice. Speech is not guaranteed while the phone tab is closed or suspended.

## Quick setup

See [SIMPLE_SETUP.md](./SIMPLE_SETUP.md) for Cloudflare Tunnel setup, Windows startup, phone access, and speech limitations. [SETUP_SIMPLE.md](./SETUP_SIMPLE.md) covers local-only operation.

## Developer checks

```powershell
.\.venv\Scripts\python.exe -m pytest -v
node --check app.js
node --test tests/test_payment_notifications.test.js tests/test_phone_speech.test.js
```

The automated tests use synthetic payment messages and do not connect to Telegram, Cloudflare, or the real payment group. A real tunnel/Telegram integration must be tested on the owner's own Windows PC.
