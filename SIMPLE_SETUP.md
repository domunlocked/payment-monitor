# Simple phone access — Payment Monitor

**The Windows PC runs Telegram and keeps the full SQLite history.** GitHub Pages remains the dashboard. A Cloudflare Tunnel gives the PC a stable HTTPS address without router port forwarding. The phone polls the PC directly; there is no Supabase, cloud database, account login, or Telegram login on the phone.

## Privacy and security

- The local API stays bound to `127.0.0.1:8765`; never change it to `0.0.0.0` or open a router port.
- The remote tunnel serves only read-only status and payment routes. It accepts browser requests only from `https://domunlocked.github.io`, and the API requires the separate `REMOTE_ACCESS_TOKEN` from the PC's `.env` on every request.
- The phone key is typed into the page and stored only in that browser tab's session storage. It is not included in GitHub Pages JavaScript. Use **Forget key** to clear it.
- Anyone who obtains your key can read the remote payment fields. Treat it as a password; rotate it immediately if exposed. The key does not permit remote listener start/stop or CSV download.
- The API shares only amount, currency, payment status, payment date/time, transaction ID, received time, and Khmer announcement. Customer name, masked account, bank, merchant, APV, Telegram credentials/session, and the full SQLite file remain on the PC.
- Cloudflare carries the HTTPS tunnel traffic as the reverse-proxy provider. The app does not store a cloud copy, but you must trust Cloudflare to relay these API requests; a public GitHub Pages compromise could also steal a key while it is being entered. This is the trade-off for no separate dashboard account and access through the existing public website.
- Cloudflare Tunnel has a free offering, subject to provider terms and limits. A stable custom hostname requires a domain configured in Cloudflare; a domain may cost money. Free terms are not guaranteed forever.
- Do not enable Cloudflare Access or another login gate for the tunnel hostname: it can block browser API calls unless separately configured. The app's private access key is the intended protection.

## One-time setup

### 1. Create a stable Cloudflare Tunnel

1. Have a domain you control and add it to a Cloudflare account. Follow Cloudflare's instructions to activate its DNS. Registration/renewal of a domain can cost money.
2. Install Cloudflare Tunnel on Windows:

   ```powershell
   winget install --id Cloudflare.cloudflared
   ```

   Close and reopen PowerShell.
3. In the Cloudflare dashboard, open **Zero Trust → Networks → Tunnels** (menu names may change), create a named tunnel, and select the Windows connector. Add a **Published application route / Public hostname**:
   - Hostname: `payments.YOUR-DOMAIN` (for example, `payments.example.com`)
   - Service type: `HTTP`
   - URL: `127.0.0.1:8765`
   - Do not enable an Access login policy for this hostname.
4. Use Cloudflare's displayed Windows service install command in an **Administrator PowerShell** window to install the tunnel as a Windows service. The tunnel token in that command is private: never paste it in chat, the project, or GitHub. The Cloudflared service should be configured to start automatically with Windows.
5. Confirm the HTTPS hostname resolves to the tunnel. Do not make a router change or open port 8765 to the internet.

### 2. Configure the local API and public website

1. In this project's `.env`, keep `API_HOST=127.0.0.1` and `API_PORT=8765`. Set:

   ```dotenv
   REMOTE_API_ORIGIN=https://payments.YOUR-DOMAIN
   ```

   Use only the HTTPS origin, no path or trailing slash.
2. Generate separate fresh local and phone keys:

   ```powershell
   .\.venv\Scripts\python.exe -c "import secrets; print('API_TOKEN='+secrets.token_urlsafe(48)); print('REMOTE_ACCESS_TOKEN='+secrets.token_urlsafe(48))"
   ```

   Put each printed assignment on its own line in `.env`. Keep both private. `API_TOKEN` signs local dashboard sessions and is never sent to the phone. The separate `REMOTE_ACCESS_TOKEN` grants only the remote read-only routes and is the key you enter on the phone. **Replace any previously exposed `API_TOKEN`.**
3. Edit the public `remote-config.js` file to match the tunnel hostname:

   ```javascript
   window.PAYMENT_MONITOR_REMOTE = Object.freeze({
     apiBaseUrl: "https://payments.YOUR-DOMAIN"
   });
   ```

   The hostname is public configuration. Never put either key or the Cloudflare tunnel token in this file.
4. Review changes and run the tests before publishing. Push only reviewed project source to the existing `main` branch (never force-push). GitHub Pages deploys the static dashboard through the existing Actions workflow. Do not publish `.env`, tunnel credentials, Telegram session, database, logs, or backups.

## Start the PC and use your phone

1. Start/confirm the `cloudflared` Windows service, then double-click `start_payment_monitor.bat`. The script starts the local API/listener service once and attempts to start the tunnel service if installed. Local monitoring can still run if the tunnel is offline.
2. On the PC, open [http://127.0.0.1:8765/](http://127.0.0.1:8765/) and press **Start Listening** if Telegram is not already connected.
3. On the phone (Wi-Fi or mobile data), open [https://domunlocked.github.io/payment-monitor/](https://domunlocked.github.io/payment-monitor/).
4. Enter `REMOTE_ACCESS_TOKEN` from the PC `.env`, then press **Connect**. The key is held only in that tab's session storage. Tap **Forget key** to clear it.
5. Tap **Speaker On**, then tap **Start Listening**. The initial history loads silently; only later payment IDs can be spoken. Polling runs about every 2.5 seconds, and reconnects resume from the last seen ID without replaying old records.
6. The phone must have a genuine Khmer (`km`) SpeechSynthesis voice for Khmer speech. If it does not, payments still show but are not spoken; English is not used as a substitute. Keep the page open and awake. Mobile browsers may suspend polling/speech in background tabs or after closing the page.

To start Payment Monitor automatically when your Windows account signs in, run `install_autostart.bat`; use `remove_autostart.bat` to uninstall that shortcut. The separately installed Cloudflared Windows service starts independently.

## Offline and troubleshooting

- **PC online** means the remote API responded. The badge separately reports Telegram connection. If the PC, internet, or tunnel is offline, the phone reports a disconnect and retries automatically; local payment history remains on the PC.
- **Key rejected (401):** verify the value entered on the phone matches `REMOTE_ACCESS_TOKEN` in the PC `.env`. If in doubt, generate a new remote key, update `.env`, restart Payment Monitor, and enter the new key.
- **Browser CORS/403:** ensure `REMOTE_API_ORIGIN` in `.env`, the Cloudflare hostname, and `apiBaseUrl` in `remote-config.js` match exactly. The site allows only `https://domunlocked.github.io`; private browsing extensions/content blockers can interfere.
- **Tunnel offline:** check that the Cloudflared Windows service is running and its dashboard route points to `http://127.0.0.1:8765`. Start the PC app before testing.
- **Local page unavailable:** run `start_payment_monitor.bat`; check `logs\startup.log`, `logs\console.log`, and `logs\listener.log`. Do not share logs without removing private data.
- **No Khmer voice:** try another mobile browser/device and enable its Khmer speech voice if available. Speech cannot be guaranteed when the phone tab is suspended or closed.
- Existing local SQLite history is not uploaded elsewhere; remote reads go through the tunnel directly to the PC.

## Checks

Run from the project folder:

```powershell
.\.venv\Scripts\python.exe -m pytest -v
node --check app.js
node --test tests\test_payment_notifications.test.js
node --test tests\test_phone_speech.test.js
```
