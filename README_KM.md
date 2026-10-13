# DomZzz-Payment Speaker

កម្មវិធីឥតគិតថ្លៃដែលដំណើរការនៅលើកុំព្យូទ័រ Windows ផ្ទាល់ខ្លួន។ វាស្តាប់តែសារទូទាត់ ABA PayWay ថ្មីៗក្នុងក្រុម Telegram ដែលអ្នកកំណត់ រក្សាទុកក្នុង SQLite ឯកជន និងបង្ហាញផ្ទាំងគ្រប់គ្រងដែលនិយាយចំនួនប្រាក់ជាភាសាខ្មែរ បើឧបករណ៍របស់អ្នកមានសំឡេងខ្មែរពិត។

> **ដែនកំណត់សំឡេងខ្មែរ៖** កុំព្យូទ័រ Windows ដែលយើងបានពិនិត្យមានតែសំឡេង Microsoft David និង Microsoft Zira ភាសា `en-US` ប៉ុណ្ណោះ។ កម្មវិធីនេះមិនប្រើសំឡេងអង់គ្លេសដើម្បីអានភាសាខ្មែរទេ។ បញ្ជីភាសា eSpeak NG បច្ចុប្បន្នក៏មិនមានភាសាខ្មែរដែរ។ Dashboard បង្ហាញតែសំឡេង browser ដែលកំណត់ភាសា `km` ប៉ុណ្ណោះ។ បើមិនមានសំឡេងខ្មែរ កម្មវិធីនឹងបង្ហាញកំហុស ប៉ុន្តែការទូទាត់នៅតែបង្ហាញលើផ្ទាំង។ ត្រូវសាកល្បងលើទូរសព្ទ/កុំព្យូទ័រពិត ព្រោះការរកឃើញសំឡេងមិនធានាគុណភាពបញ្ចេញសំឡេងទេ។

## កម្មវិធីដំណើរការនៅទីណា

- **GitHub Pages** ផ្ទុកតែគេហទំព័រឋិតិវន្ត HTML/CSS/JavaScript ដោយឥតគិតថ្លៃ។ វាមិនអាចដំណើរការ Python, Telegram session ឬមូលដ្ឋានទិន្នន័យឯកជនបានទេ។
- **កុំព្យូទ័រ Windows របស់អ្នក** ដំណើរការ Python listener, Telegram user session, API ដែលការពារដោយ token និង SQLite។ Listener ស្តាប់តែក្រុមដែលបានកំណត់ ហើយមិនផ្ញើសារទៅ Telegram ទេ។
- **ឧបករណ៍នីមួយៗ** ទាញយកការទូទាត់ថ្មីតាម API មានសោ កត់ត្រាជួរប្រកាសផ្ទាល់ខ្លួន និងប្រកាសតែពេលអ្នកបើកសំឡេង។ ឧបករណ៍ថ្មីបង្ហាញប្រវត្តិថ្មីៗដោយមិនអានជាសំឡេង។
- ឈ្មោះអតិថិជន លេខប្រតិបត្តិការ និងប្រវត្តិទូទាត់ជាព័ត៌មានឯកជន។ អ្នកណាដែលទទួលបាន API token អាចអាន/នាំចេញប្រវត្តិបាន។ ចែករំលែកតែជាមួយឧបករណ៍ដែលអ្នកទុកចិត្ត។

## ដំឡើងលើ Windows 10/11

1. ដំឡើង **Python 3.11 ឬ 3.12** ពី [python.org](https://www.python.org/downloads/windows/)។ ជ្រើស Python Launcher និង **Add Python to PATH**។
2. ទាញយក/ក្លូន repository ហើយពន្លាឯកសារ។ ចុចពីរដង `install.bat`។ វាបង្កើត `.venv` ដំឡើង package ហើយបង្កើត `.env` ដែលមាន API token ចៃដន្យ។ **កុំបង្ហោះ `.env` ទៅ GitHub**។
3. បង្កើត Telegram API credentials ដោយប្រើគណនី Telegram របស់អ្នក៖
   - ចូល [my.telegram.org](https://my.telegram.org/) → **API development tools** → បង្កើតកម្មវិធី។
   - បញ្ចូល `api_id` ក្នុង `TELEGRAM_API_ID` និង `api_hash` ក្នុង `TELEGRAM_API_HASH` នៃឯកសារ `.env`។ នេះជាព័ត៌មានសម្រាប់ Telegram user client មិនមែន Bot token ទេ។
   - ពេលដំណើរការលើកដំបូង Telethon សួរលេខទូរសព្ទ លេខកូដចូល និងពាក្យសម្ងាត់ 2-step verification (បើបានបើក) នៅក្នុង terminal លើកុំព្យូទ័ររបស់អ្នក។ កុំចែករំលែកកូដ ពាក្យសម្ងាត់ ឬឯកសារ `payment-monitor.session`។
4. រកលេខសម្គាល់ក្រុមដោយមិនផ្ញើសារទៅក្រុម៖
   - ត្រូវប្រាកដថាគណនី Telegram នោះបានចូលរួមក្រុម និងទទួលសារជូនដំណឹង PayWay by ABA។
   - បើក PowerShell ក្នុងថតគម្រោង ហើយដំណើរការ `.\.venv\Scripts\python.exe listener.py --list-groups`។ ជ្រើសឈ្មោះក្រុមត្រឹមត្រូវ ហើយចម្លងលេខ ID ទៅ `TELEGRAM_CHAT_ID` ក្នុង `.env`។ ពាក្យបញ្ជានេះបង្ហាញបញ្ជីនៅលើកុំព្យូទ័ររបស់អ្នក មិនបង្ហោះសារទៅក្រុមទេ។
   - ក៏អាចប្រើ username សាធារណៈរបស់ក្រុមដែលមានទម្រង់ `@username` បាន។ កុំបញ្ចូលឈ្មោះបង្ហាញ ឬ bot username។
5. **សាកល្បងលើកុំព្យូទ័រជាមុន៖** ដំណើរការ `start_listener.bat` ហើយបញ្ចប់ការអនុញ្ញាត Telegram។ បើក [http://127.0.0.1:8765/](http://127.0.0.1:8765/) លើកុំព្យូទ័រដដែល។ បញ្ចូល API token ពីឯកសារ `.env` ក្នុងប្រអប់តភ្ជាប់។
6. ពិនិត្យសំឡេងដោយ `.\.venv\Scripts\python.exe listener.py --check-voice`។ នៅក្នុង Dashboard ចុច **Test Khmer voice** រួចចុច **Enable audio**។ បើមិនមានសំឡេងខ្មែរ កម្មវិធីនឹងប្រាប់ច្បាស់ ហើយមិនប្តូរទៅសំឡេងអង់គ្លេសទេ។
7. រត់តេស្តដោយបើក PowerShell ហើយប្រើ `.\.venv\Scripts\python.exe -m pytest`។ តេស្តប្រើឈ្មោះអតិថិជន/លេខប្រតិបត្តិការសាកល្បង មិនត្រូវការចូល Telegram ឬទិន្នន័យអតិថិជនពិតទេ។

Listener ដំណើរការតែសារថ្មីៗបន្ទាប់ពីវាបានចាប់ផ្ដើម។ វាមិនទាញយក ឬអានសារចាស់ទេ។ Transaction ID ដដែលត្រូវបានរំលង។ បើអ៊ីនធឺណិតដាច់ កម្មវិធីព្យាយាមភ្ជាប់ឡើងវិញ។ ចុច **Ctrl+C** ឬបិទបង្អួចដើម្បីឈប់ ហើយបើក `start_listener.bat` ដើម្បីចាប់ផ្ដើមម្ដងទៀត។

## បើក Dashboard លើទូរសព្ទ/ថេប្លេត

**លំនាំដើមដែលណែនាំ៖ ប្រើ Wi-Fi ឯកជនដូចគ្នា** ដោយមិនបាច់ប្រើ relay/account។ ជម្រើស VPN ពីចម្ងាយឥតគិតថ្លៃអាស្រ័យលើលក្ខខណ្ឌសេវា; កុំសន្មតថាផែនការប្រើផ្ទាល់ខ្លួនអនុញ្ញាតការតាមដានការទូទាត់អាជីវកម្ម។

### ភ្ជាប់ពីគ្រប់បណ្ដាញដោយ HTTPS (ជម្រើស Tailscale Serve)

1. ដំឡើង Tailscale លើ Windows និងទូរសព្ទ/ថេប្លេត ហើយចូល **tailnet ឯកជនដូចគ្នា**។ ផែនការ **Personal** បច្ចុប្បន្នឥតគិតថ្លៃសម្រាប់ការប្រើផ្ទាល់ខ្លួនមិនមែនពាណិជ្ជកម្ម តែត្រូវមានគណនី ហើយលក្ខខណ្ឌអាចផ្លាស់ប្តូរ។ ពិនិត្យ [ព័ត៌មានផែនការ](https://tailscale.com/pricing)។
2. ទុក `API_HOST=127.0.0.1` ក្នុង `.env` ហើយបើក listener។ បើស្នើ សូមបើក HTTPS certificates សម្រាប់ tailnet។
3. បើក PowerShell ថ្មី ហើយដំណើរការ `tailscale serve 8765`។ វាបង្ហាញអាសយដ្ឋាន HTTPS ឯកជន ដូចជា `https://your-pc.example.ts.net`។ ទុកបង្អួច Serve ឱ្យដំណើរការ។ សូមមើល [សៀវភៅណែនាំ Serve](https://tailscale.com/docs/features/tailscale-serve)។
4. បន្ថែម origin របស់ GitHub Pages (ឧ. `https://YOUR_GITHUB_USERNAME.github.io` ដោយមិនបញ្ចូលផ្លូវ URL) ទៅ `CORS_ORIGINS` ក្នុង `.env` ហើយចាប់ផ្ដើម listener ឡើងវិញ។
5. បើក GitHub Pages លើទូរសព្ទ បញ្ចូលអាសយដ្ឋាន HTTPS ពី Serve និង API token។ ឧបករណ៍ចល័តត្រូវភ្ជាប់ Tailscale ពេលប្រើ។

នេះជាការតភ្ជាប់ VPN ឯកជន មិនមែន tunnel សាធារណៈទេ។ កុំប្រើ Tailscale Funnel និងកុំបើក port របស់ listener ទៅអ៊ីនធឺណិត។ Tailscale ជាសេវាខាងក្រៅដែលជាជម្រើស ត្រូវការគណនី/កម្មវិធី ហើយអាចផ្លាស់ប្ដូរលក្ខខណ្ឌឥតគិតថ្លៃបាន។ វាមិនមានការធានាថានឹងនៅឥតគិតថ្លៃ ឬមាន uptime ជាក់លាក់ទេ។ បើលក្ខខណ្ឌ Personal មិនអនុញ្ញាតការប្រើប្រាស់របស់អ្នក សូមប្រើ Wi-Fi ឯកជនដូចគ្នា; គម្រោងនេះមិនសន្យាថាមាន hosted relay ឥតគិតថ្លៃសម្រាប់អាជីវកម្មទេ។

### ប្រើ Wi-Fi តែមួយ (គ្មានគណនី VPN)

1. ភ្ជាប់ទូរសព្ទ និងកុំព្យូទ័រទៅ Wi-Fi ឯកជនដូចគ្នា។ កំណត់ `API_HOST=0.0.0.0` ក្នុង `.env` ហើយបើក listener ឡើងវិញ។ **កុំកំណត់ router port forwarding**។
2. បើ Windows Firewall សួរ អនុញ្ញាតតែ **Private networks** មិនមែន Public។
3. រត់ `ipconfig` លើ Windows ដើម្បីរក IPv4 ឯកជន (ឧ. `192.168.1.25`)។ បើក `http://192.168.1.25:8765/` លើទូរសព្ទ។ Listener ផ្ញើតែឯកសារ dashboard បីប៉ុណ្ណោះ មិនបង្ហាញ `.env`, database, session ឬ logs ទេ។
4. បញ្ចូល API token បើកសំឡេង និងសាកល្បង។ HTTP មិនអ៊ិនគ្រីប token/ប្រវត្តិទូទាត់លើ Wi-Fi ទេ ដូច្នេះប្រើតែលើបណ្ដាញឯកជនដែលទុកចិត្ត និងមិនដំណើរការពីក្រៅ Wi-Fi។

កុំប្រើអាសយដ្ឋាន `http://192.168...` ក្នុងទំព័រ GitHub Pages HTTPS ព្រោះ browser រារាំងការភ្ជាប់មិនមាន HTTPS។ បើគ្មាន VPN ឯកជន សូមប្រើរបៀប Wi-Fi ខាងលើ ឬប្រើ Dashboard លើកុំព្យូទ័រដែលដំណើរការ listener។

## បង្ហោះ Dashboard ទៅ GitHub Pages

1. Push គម្រោងទៅ **public repository** នៅ GitHub (GitHub Pages ឥតគិតថ្លៃសម្រាប់ public repository; private repository អាចត្រូវការផែនការ GitHub ដែលមាន Pages)។ ចូល **Settings → Pages → Build and deployment** ហើយជ្រើស **GitHub Actions**។
2. Workflow `.github/workflows/pages.yml` បង្ហោះតែឯកសារ static ពេល push ទៅ `main`។ រង់ចាំរហូត Pages បង្ហាញអាសយដ្ឋានគេហទំព័រ។
3. កុំបញ្ចូល `.env`, `.session`, `.sqlite3`, logs, API token ឬរូបភាពដែលបង្ហាញព័ត៌មានអតិថិជនទៅ repository/Pages។ `.gitignore` មិនជំនួសការត្រួតពិនិត្យ `git status` មុន push ទេ។ GitHub Pages ជាសាធារណៈ មិនមែនកន្លែងរក្សាទុកទិន្នន័យឯកជន។

## ការកំណត់ និងឯកជនភាព

- `.env` មាន `TELEGRAM_API_ID`, `TELEGRAM_API_HASH`, `TELEGRAM_CHAT_ID`, `API_TOKEN`, `CORS_ORIGINS`, `API_HOST`, `API_PORT`, `DATABASE_PATH`, `RETENTION_DAYS` និង `LOG_LEVEL`។ API token ត្រូវមានយ៉ាងតិច 32 តួអក្សរ; `install.bat` បង្កើតវាដោយចៃដន្យ។
- `CORS_ORIGINS` ជាបញ្ជី origin ពិតប្រាកដ ដូចជា `https://YOUR_GITHUB_USERNAME.github.io`។ មិនប្រើ wildcard ទេ។
- `API_HOST` លំនាំដើម `127.0.0.1`។ ប្រើ `0.0.0.0` តែ Wi-Fi ឯកជនប៉ុណ្ណោះ។ ប្រើ VPN Serve ដោយភ្ជាប់ទៅ loopback។
- SQLite លុបទិន្នន័យចាស់ជាង `RETENTION_DAYS` (លំនាំដើម 365 ថ្ងៃ) ពេល listener ចាប់ផ្ដើម និងពេលរក្សាទុកការទូទាត់ថ្មី។
- `/api/status`, `/api/payments`, `/api/payments.csv` ត្រូវការបញ្ចូល bearer token។ `/healthz` បង្ហាញតែថា HTTP server កំពុងដំណើរការឬអត់។ API មិនមាន route សរសេរ/ផ្លាស់ប្ដូរទិន្នន័យទេ។
- API token រក្សាទុកក្នុង local storage របស់ browser លើឧបករណ៍នីមួយៗ។ កុំប្រើ profile ដែលអ្នកដទៃអាចបើកបាន។ CSV export មានប្រវត្តិទូទាត់/ព័ត៌មានផ្ទាល់ខ្លួន។ ការប្រកាសបិទ/បើក និងជួរសំឡេងបំបែកតាម browser នីមួយៗ។
- ឧបករណ៍ថ្មីចាប់ផ្ដើមពីចំណុចចុងក្រោយក្នុង database ដោយមិនអានប្រវត្តិចាស់។ ឧបករណ៍ដែលបានភ្ជាប់ពីមុនរក្សាទុក cursor និងជួររង់ចាំក្នុង local storage ផ្ទាល់ខ្លួន។
- សំឡេងដំណើរការតែក្នុង browser/device ដែលបានបើកសំឡេង ហើយនៅពេល browser អនុញ្ញាត និងឧបករណ៍មិន mute។ ការបិទសំឡេង/គ្មាន Khmer voice មិនប៉ះពាល់ការបង្ហាញទិន្នន័យទេ។

## សំឡេងខ្មែរ និងការដោះស្រាយបញ្ហា

កម្មវិធីប្រើតែសំឡេង Khmer ដែល browser រាយថាជាភាសា `km` ប៉ុណ្ណោះ។ វាមិនផ្ញើសារទៅ paid TTS service និងមិនប្ដូរទៅសំឡេងអង់គ្លេសទេ។ Windows ដែលបានពិនិត្យមានតែសំឡេង `en-US`; បញ្ជីភាសា eSpeak NG [មិនមាន Khmer](https://github.com/espeak-ng/espeak-ng/blob/master/docs/languages.md)។ នេះមិនមែនជាភស្តុតាងថាគ្មាន Khmer TTS នៅកន្លែងណាមួយទេ ប៉ុន្តែមិនមាន engine Khmer offline ឥតគិតថ្លៃដែលគម្រោងនេះអាចធានាថាដំណើរការបាន។ ដំណោះស្រាយឥតគិតថ្លៃដែលគួរឱ្យទុកចិត្តគឺប្រើ dashboard មើលការទូទាត់ ហើយបើកសំឡេងតែពេលមាន Khmer voice ពិត។

- **គ្មានការទូទាត់៖** ពិនិត្យស្ថានភាព Telegram, group ID, membership និងទម្រង់សារថ្មី។ សារមុន listener ដំណើរការមិនត្រូវបាន replay ទេ។
- **ទូរសព្ទភ្ជាប់មិនបាន៖** ពិនិត្យថា listener កំពុងដំណើរការ, IP/port ត្រឹមត្រូវ, firewall អនុញ្ញាត Private network។ GitHub Pages ត្រូវការអាសយដ្ឋាន Tailscale Serve HTTPS មិនមែន LAN HTTP IP។
- **401:** បញ្ចូល `API_TOKEN` ថ្មីពី `.env` ហើយចុច **Forget saved token** រួចភ្ជាប់ម្ដងទៀត។
- **CORS:** បន្ថែម origin ត្រឹមត្រូវទៅ `CORS_ORIGINS` ហើយ restart listener។
- **គ្មានសំឡេង៖** ពិនិត្យថាមាន Khmer voice ក្នុង system/browser, ចុច Enable audio/Test, ពិនិត្យ volume/mute។ កុំជ្រើសសំឡេងអង់គ្លេស។
- **សារកំហុសក្នុង listener៖** ពិនិត្យ `logs\listener.log`។ Log មិនសរសេរ token, API hash, session token, ឈ្មោះអតិថិជន ឬ Transaction ID ពេញលេញទេ។

## ចាប់ផ្ដើមពេល Windows បើក

បើក **Task Scheduler** → បង្កើត task ថ្មី → Trigger **At log on** → Action បើកឯកសារ `start_listener.bat` ក្នុងថតគម្រោង និងកំណត់ **Start in** ជាថតគម្រោង។ កុំបើក listener ពីរដែលប្រើ Telegram session/database ដូចគ្នា។ កុំព្យូទ័រត្រូវនៅបើក និងមានអ៊ីនធឺណិត។

រត់ automated tests ដោយ `.\.venv\Scripts\python.exe -m pytest`។ ការចូល Telegram ពិត ការមកដល់សារ ABA សំឡេង Windows/browser លើទូរសព្ទ និង VPN ត្រូវសាកល្បងលើឧបករណ៍ពិតរបស់អ្នក។
