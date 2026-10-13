# DomZzz-Payment Speaker

A free, local-first Windows Telegram listener and static ABA KHQR payment dashboard. It recognizes new payment notifications from one configured Telegram group, saves transactions in a private SQLite database, and presents a Khmer voice announcement on each browser/device that the owner enables.

> **Khmer speech limitation:** Windows on the machine used to build this project reported only Microsoft David and Microsoft Zira (`en-US`) voices. Neither is a Khmer voice, and this project will not use either to speak Khmer text. The upstream eSpeak NG language list also does not list Khmer. The dashboard only offers actual browser voices whose reported language is Khmer (`km`); if the receiving device has none, it displays an error and keeps payments visible without announcing them. Voice availability and pronunciation must be tested on the actual device; voice discovery is not a pronunciation-quality guarantee.

## What runs where

- **GitHub Pages** can host the HTML, CSS, and JavaScript for free. It cannot run Python, keep a Telegram session alive, or host the private payment database.
- **Your Windows computer** runs the Python listener, Telegram user session, authenticated API, and SQLite file. The listener only watches the configured chat and never sends a message to Telegram.
- **Each browser/device** polls the authenticated API, stores its own short pending-speech queue and cursor locally, and speaks only through a locally installed Khmer browser voice. A new device first loads the latest history silently.
- Payment names and transaction IDs are sensitive customer information. A bearer token protects the private API, but anyone who gets the token can read and export the retained history. Share it only with devices you trust.

## Quick start (Windows 10/11)

1. Install **Python 3.11 or 3.12** from [python.org](https://www.python.org/downloads/windows/). During setup, enable the Python launcher and **Add Python to PATH**.
2. Download/clone this repository, extract it, then double-click `install.bat`. It creates `.venv`, installs dependencies from `requirements.txt`, copies `.env.example` to `.env`, and generates a private API token. Do not upload `.env`.
3. Create Telegram API credentials using your own Telegram account:
   - Sign in at [my.telegram.org](https://my.telegram.org/), open **API development tools**, and create an application.
   - Copy its numeric **api_id** and **api_hash** into `TELEGRAM_API_ID` and `TELEGRAM_API_HASH` in `.env`. These are Telegram user-client credentials, **not** a bot token.
   - Keep the account signed in and able to receive its Telegram login code. On the first listener authorization, Telethon asks for the phone number, one-time login code, and (if enabled) two-step-verification password in the local terminal. Never share these or the generated `payment-monitor.session` file.
4. Find the exact group ID without posting anything to the group:
   - Make sure the PayWay by ABA bot's payment notifications arrive in the group on the Telegram account you authorized.
   - Run `.\.venv\Scripts\python.exe listener.py --list-groups` from PowerShell in the project folder. Sign in if requested; choose the exact group name and copy its numeric ID into `TELEGRAM_CHAT_ID` in `.env`. This command lists dialogs locally and does not send a group message.
   - Alternatively use the group's public `@username`. Do not put a display name or bot username here.
5. **Use the desktop first:** run `start_listener.bat`, complete Telegram authorization, then open [http://127.0.0.1:8765/](http://127.0.0.1:8765/) on that same computer. Copy the API token from your private `.env` into the connection form. The connection indicator reports Telegram connection separately from browser audio status.
6. Check for a local Khmer voice with `.\.venv\Scripts\python.exe listener.py --check-voice`. On the dashboard click **Test Khmer voice**, then **Enable audio**. Enabling audio speaks a short Khmer sample as a browser interaction. If no true Khmer voice is installed, the test explains the limitation; do not select an English voice as a substitute.
7. **Check parsing:** in another PowerShell window run `.\.venv\Scripts\python.exe -m pytest`. Automated tests use synthetic customer and transaction data and do not need Telegram login or access to a real group.

The listener reads only **new** Telegram updates after it is running; it does not fetch/announce old group messages at startup. Duplicate transaction IDs are ignored. If Telegram or the network disconnects, the listener retries with increasing delays. Stop it with **Ctrl+C** or close the listener window; start it again with `start_listener.bat`.

## Open the dashboard on a phone/tablet

**Recommended default: same trusted Wi-Fi**, which requires no relay account and keeps the listener off the public internet. The optional remote VPN below is free only if your intended use is covered by its current plan terms; do not assume a personal-use plan permits commercial payment monitoring.

### Private HTTPS access from any network (optional: Tailscale Serve)

1. Install Tailscale on the Windows computer and the phone/tablet and sign both into the **same private tailnet**. Tailscale currently describes its **Personal** plan as free for **non-commercial personal use** and requires an account. If this monitors a shop or other business payments, check the current [plan details and terms](https://tailscale.com/pricing); do not rely on that free plan unless your use is permitted.
2. Keep `API_HOST=127.0.0.1` in `.env`, start this listener, and enable HTTPS certificates for your tailnet if prompted.
3. In a separate PowerShell window, run `tailscale serve 8765`. It prints a private HTTPS address such as `https://your-pc.example.ts.net`. Keep Serve running while using the dashboard. Tailscale documents Serve as private to devices in your tailnet and gives this exact port-proxy pattern in its [Serve guide](https://tailscale.com/docs/features/tailscale-serve).
4. Add the **GitHub Pages site origin** (origin only, no page path) to `CORS_ORIGINS` in `.env`, for example `https://YOUR_GITHUB_USERNAME.github.io`. For a custom Pages domain, use that HTTPS origin instead. Restart the Python listener after changing `.env`.
5. Open the GitHub Pages dashboard on the phone, enter the private Serve HTTPS address and your `.env` API token, enable audio, and test the Khmer voice. The phone needs to be signed into Tailscale whenever it connects.

This is an authenticated private VPN connection, **not** a public tunnel. Do not use Tailscale Funnel or publish the listener port to the internet. Tailscale is an optional third-party service: it requires an account and client software, its free tier is limited to permitted non-commercial use, and its current limits/availability may change without an uptime guarantee. If those terms do not cover your use, use the same-Wi-Fi mode below; this project does not promise a free, business-eligible hosted relay.

### Same Wi-Fi only (no VPN/account)

1. Connect the Windows computer and phone to the same trusted, private Wi-Fi. In `.env`, set `API_HOST=0.0.0.0`. Do **not** configure router port forwarding.
2. Restart `start_listener.bat`. If Windows Firewall prompts, allow access only on **Private networks**, never public networks.
3. On Windows, find the computer's private IPv4 address with `ipconfig` (for example `192.168.1.25`), then on the phone open `http://192.168.1.25:8765/`. This app serves only the dashboard's three public static files and does not serve `.env`, the database, session, or logs. Since the page and API are same-origin, no additional CORS origin is required for this local URL.
4. Enter the API token, enable audio, and test it. Keep this HTTP-only setup on trusted Wi-Fi: bearer tokens and payment details are not encrypted in transit on the LAN. It will not work from outside that Wi-Fi.

Do not paste a `http://192.168...` address into the GitHub Pages HTTPS dashboard; modern browsers block HTTPS pages from fetching insecure HTTP APIs. Do not open a router port or leave the API exposed to public networks. If no private VPN is available, use the same-Wi-Fi setup or the dashboard on the listener computer.

## Publish the static site with GitHub Pages

1. Push the project to a **public GitHub repository** (GitHub Pages is available at no charge for public repositories; private-repository Pages availability depends on your GitHub plan). In **Settings → Pages → Build and deployment**, choose **GitHub Actions**. The workflow in `.github/workflows/pages.yml` deploys only static site files when you push to `main`.
2. Wait for the Pages workflow and open the URL shown in the Pages settings (normally `https://USERNAME.github.io/REPOSITORY/`). For a project site, the browser origin is `https://USERNAME.github.io`—use that origin in `.env` for the remote Tailscale setup.
3. Never copy `.env`, `.session`, `.sqlite3`, logs, or an API token into the public repository, the Pages files, or screenshots. `.gitignore` excludes private runtime files; verify `git status` before pushing. GitHub Pages is public static hosting, not a private host for customer data.

## Configuration reference

| `.env` setting | Purpose |
| --- | --- |
| `TELEGRAM_API_ID`, `TELEGRAM_API_HASH` | User API credentials from [my.telegram.org](https://my.telegram.org/). |
| `TELEGRAM_CHAT_ID` | One configured numeric Telegram group ID, or its public `@username`. |
| `API_TOKEN` | At least 32 random characters; generated by `install.bat`. Enter it only in the dashboard on trusted devices. |
| `CORS_ORIGINS` | Comma-separated exact browser origins allowed to call the API. No wildcards are used. |
| `API_HOST` | Defaults to loopback (`127.0.0.1`). Only bind `0.0.0.0` for a trusted private LAN; use the loopback binding behind a VPN proxy. |
| `API_PORT` | Defaults to `8765`. |
| `DATABASE_PATH` | Defaults to the ignored local file `payment_history.sqlite3`. |
| `RETENTION_DAYS` | Defaults to 365 days; expired records are deleted at listener startup and when a payment is saved. |

Accepted messages must contain a USD `$` or KHR `៛` amount, `paid by`, a date, `via` method, merchant, transaction ID, and APV. Amount grouping commas and up to two USD decimal digits are accepted; bank text and a masked account suffix are optional. Invalid notices are ignored. No full message text, name, account suffix, transaction ID, or token is written to the application log.

The read-only API has bearer-authenticated `/api/status`, `/api/payments`, and `/api/payments.csv` routes. `/healthz` reports only whether the HTTP process is up. Browser origins must exactly match `CORS_ORIGINS`; cross-origin credentials and write routes are disabled. The dashboard token is saved in that device's browser local storage to survive reloads. Keep the browser/device private, avoid shared profiles, and use **Forget saved token** when appropriate. The CSV export contains personal transaction history.

### Khmer TTS: what is and is not promised

The application:

- Inspects local Windows voices with `listener.py --check-voice`.
- Lets the browser offer/select only voices it identifies with a `km` language tag. Speed and volume are per-browser settings.
- Never sends audio/payment text to a speech API and never falls back to English.
- Serializes each device's own new-payment queue. First connection starts at the current database watermark, so an initial visit does not read old payments aloud; later visits on the same browser resume from its saved cursor.

The Windows host tested during implementation exposed only English `en-US` voices. The current [eSpeak NG language list](https://github.com/espeak-ng/espeak-ng/blob/master/docs/languages.md) does not list Khmer either. These checks do not prove that no Khmer TTS exists anywhere; they do mean this project cannot honestly promise a reliable, free offline Khmer voice. Check whether your device/browser has a **real Khmer** voice. Otherwise the closest reliable free option is the dashboard with visible payments and no speech until an actual Khmer voice is available.

## Start automatically and troubleshoot

- **Windows Task Scheduler:** create a task triggered **At log on** for your Windows user; set program to the project path `start_listener.bat` and **Start in** to the project folder. Do not run two listener copies against the same Telegram session/database. The PC must remain powered on and connected to the internet.
- **Missing API credentials:** open `.env` in a text editor, fill in the values, save, and restart. The API hash and API token are different secrets.
- **Group not listed:** sign into the same Telegram account that receives the PayWay group notification, then run `listener.py --list-groups`. Check that the account is a group member and use its printed numeric ID.
- **Telegram prompts for a code each time:** close the extra listener copy and keep `payment-monitor.session` in the project folder. Never share or upload it.
- **No payments:** confirm Telegram says Connected, the configured group ID is correct, the PayWay bot posts in that group, and the next notification is a valid payment format. Notifications from before listener startup are not replayed.
- **Phone cannot connect:** confirm both devices are on the same private network, the listener is still open, the IP/port are correct, and Windows Firewall allows private-network access. For GitHub Pages, use the HTTPS Tailscale Serve address, not a LAN HTTP IP, and add the exact Pages origin in `.env`.
- **401 / access denied:** re-enter the current `API_TOKEN` from `.env`, check for stale browser configuration, then use **Forget saved token** and reconnect.
- **CORS error:** add the exact page origin (scheme + hostname + optional port, without a path) to `CORS_ORIGINS`, restart the listener, and reload the page.
- **No voice / silent audio:** use the browser's voice settings to install/check a Khmer-language system voice, reload the dashboard, enable audio with a user click, check the browser/device volume and mute switch, and press the speech test button. Do not choose an English voice for Khmer.
- **Port conflict:** change `API_PORT`, restart the listener, and include the new port in the dashboard URL.
- **Tests:** `.\.venv\Scripts\python.exe -m pytest`. Live Telegram login, real payment arrival, real Windows SAPI inventory, phone-browser voice selection, and Tailscale connectivity require the user's own devices and are not simulated by unit tests.

## Project files

```text
DomZzz-Payment-Speaker/
├── index.html
├── styles.css
├── app.js
├── listener.py
├── parser.py
├── khmer_numbers.py
├── tts_service.py
├── database.py
├── api.py
├── config.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── README_KM.md
├── install.bat
├── start_listener.bat
├── tests/
│   ├── test_parser.py
│   ├── test_khmer_numbers.py
│   ├── test_deduplication.py
│   ├── test_api.py
│   └── test_tts_service.py
└── .github/workflows/pages.yml
```
