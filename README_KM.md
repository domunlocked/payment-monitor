# Payment Monitor

កម្មវិធីនេះដំណើរការលើកុំព្យូទ័រ Windows របស់អ្នក ដើម្បីតាមដានសារទូទាត់ ABA PayWay ថ្មីៗក្នុងក្រុម Telegram មួយដែលបានកំណត់។ កម្មវិធីរក្សាទុកប្រតិបត្តិការមិនស្ទួនក្នុង SQLite ហើយបង្ហាញតែការទូទាត់ចុងក្រោយលើផ្ទាំង។

## សុវត្ថិភាព និងឯកជនភាព

- API និង Dashboard ដំណើរការតែលើ `127.0.0.1:8765` ក្នុងកុំព្យូទ័រនេះប៉ុណ្ណោះ។ ទូរសព្ទលើ Wi-Fi ផ្សេង ឬ GitHub Pages មិនអាចចូលប្រើ Telegram session និង database ក្នុងកុំព្យូទ័រនេះបានទេ។
- GitHub Pages អាចផ្ទុកឯកសារ static ប៉ុណ្ណោះ មិនអាចដំណើរការ Python ឬ Telegram listener បានទេ។
- មិនមាន tunnel សាធារណៈ ការបើក router port ឬ CORS ទូលំទូលាយទេ។
- ឈ្មោះអតិថិជន និងលេខប្រតិបត្តិការជាព័ត៌មានឯកជន។ កុំបង្ហោះ `.env`, `payment-monitor.session`, `payment_history.sqlite3`, logs និង backup ទៅ GitHub។
- កុំព្យូទ័រ Windows ដែលបានពិនិត្យមានតែសំឡេងអង់គ្លេស។ កម្មវិធីបង្ហាញចំនួនជាអក្សរខ្មែរ ប៉ុន្តែមិនប្រើសំឡេងអង់គ្លេសជំនួសសំឡេងខ្មែរទេ។

## ការណែនាំ

សូមអាន [SETUP_SIMPLE.md](./SETUP_SIMPLE.md) សម្រាប់ការដំឡើងលើ Windows ការចូល Telegram ការចាប់ផ្ដើម/បញ្ឈប់ listener ការសាកល្បង និងការកំណត់ឱ្យចាប់ផ្ដើមពេលចូល Windows។

## សាកល្បង

```powershell
.\.venv\Scripts\python.exe -m pytest -v
node --check app.js
```

តេស្តស្វ័យប្រវត្តិប្រើសារសាកល្បង ហើយមិនភ្ជាប់ទៅ Telegram ទេ។ ការសាកល្បង Telegram ពិតត្រូវធ្វើលើកុំព្យូទ័រ Windows របស់ម្ចាស់គណនី។
