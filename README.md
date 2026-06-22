# EngageBot v2.0 — Automated Customer Engagement Tool
### For Small Businesses | Facebook Messenger + Email Automation

---

## 📦 What's Inside

```
fb_messaging_bot/
├── engagebot.py        ← Main bot engine (core logic)
├── run_facebook.py     ← Run Facebook messenger bot only
├── run_email.py        ← Run email campaign only
├── config.yaml         ← ⭐ All settings — edit this file
├── contacts.csv        ← Your email contact list
├── requirements.txt    ← Python packages needed
├── logs/               ← Auto-created: all session logs + CSV reports
└── README.md           ← This file
```

---

## ✅ STEP 1 — Install Python

Download Python 3.10 or newer from: https://www.python.org/downloads/

During install, **tick the checkbox**: ✅ "Add Python to PATH"

---

## ✅ STEP 2 — Install Google Chrome

Make sure Google Chrome is installed on your computer.
Download from: https://www.google.com/chrome/

---

## ✅ STEP 3 — Install Required Libraries

Open **Command Prompt** (Windows) or **Terminal** (Mac/Linux) and run:

```bash
pip install -r requirements.txt
```

This installs: selenium, webdriver-manager, pyyaml, schedule

---

## ✅ STEP 4 — Configure Your Settings

Open `config.yaml` in any text editor (Notepad, VS Code, etc.)

### Key settings to change:

```yaml
business:
  name: "My Shop Name"           # ← Your business name
  owner_email: "you@gmail.com"   # ← Your email

facebook:
  max_contacts_per_session: 30   # ← How many to message per run (start low!)

messaging:
  default_template: "order_followup"   # ← Which message template to use

email:
  enabled: true                        # ← Set to true to use email
  sender_email: "yourshop@gmail.com"
  sender_password: "xxxx xxxx xxxx"    # ← Gmail App Password (see below)
  recipient_email: "notify@gmail.com"
```

---

## ✅ STEP 5 — Set Up Gmail App Password (For Email Feature)

1. Go to your Google Account: https://myaccount.google.com
2. Click **Security** → **2-Step Verification** (enable it first if needed)
3. Scroll down → click **App Passwords**
4. Select App: "Mail", Device: "Windows Computer"
5. Click **Generate** → copy the 16-character password
6. Paste it in `config.yaml` under `sender_password`

> ⚠️ NEVER use your real Gmail password. Always use an App Password.

---

## ✅ STEP 6 — Prepare Your Contacts List (For Email)

Edit `contacts.csv` — add your customers:

```csv
name,email,phone,notes
Ahmed Khan,ahmed@example.com,+923001234567,Order #1001
Sara Malik,sara@gmail.com,+923009876543,Follow-up
```

**Rules:**
- `name` and `email` columns are required
- `phone` and `notes` are optional
- Save the file in the same folder as the bot

---

## 🚀 HOW TO RUN

### Option A — Facebook Messenger Bot

```bash
python run_facebook.py
```

- A Chrome browser will open automatically
- **Log into your Facebook Business Page** in that browser
- Bot will wait 40 seconds for you to log in
- Then it will start messaging contacts in your inbox

### Option B — Email Campaign

```bash
python run_email.py
```

- No browser needed
- Reads from `contacts.csv`
- Sends emails to all contacts using the configured template

### Option C — Both Facebook + Email Together

```bash
python engagebot.py
```

---

## 📋 MESSAGE TEMPLATES

Edit your messages in `config.yaml` under `messaging.templates`.

Use `{name}` to automatically insert the contact's first name:

```yaml
templates:
  order_followup: |
    Hi {name}! 👋
    Your order has been confirmed. Thank you!

  new_promotion: |
    Hello {name}!
    We have a special offer just for you! 🎉
```

You can add as many templates as you want. Switch between them by changing:
```yaml
messaging:
  default_template: "order_followup"   # ← change template name here
```

---

## ⏰ AUTO-SCHEDULING (Run Automatically Every Day)

To have the bot run automatically at a specific time, edit `config.yaml`:

```yaml
schedule:
  enabled: true
  run_at: "09:00"          # 24-hour format
  timezone: "Asia/Karachi"
  repeat: "daily"          # daily | weekdays | once
```

Then run once and leave it:
```bash
python engagebot.py
```

The bot will keep running in the background and start automatically at the scheduled time.

---

## 📊 LOGS & REPORTS

After every run, check the `logs/` folder:

- `engagebot_YYYYMMDD_HHMMSS.log` — Detailed session log
- `report_YYYYMMDD_HHMMSS.csv` — Spreadsheet of every message attempt

The CSV report shows:
| timestamp | name | channel | status | note |
|---|---|---|---|---|
| 2025-02-20 09:15:22 | Ahmed Khan | facebook | success | |
| 2025-02-20 09:15:55 | Sara Malik | email | success | |
| 2025-02-20 09:16:30 | Unknown | facebook | skipped | No name |

---

## 🛡️ SAFETY FEATURES EXPLAINED

| Feature | What it does |
|---|---|
| Random delays (12–28s) | Waits a random time between each message |
| Batch breaks | Pauses 90–180s after every 20 messages |
| Human-like typing | Types each character with small random delays |
| Retry system | Retries failed messages up to 3 times |
| Max contact cap | Never exceeds your set limit per session |
| Target filter | Optional: only message specific names |

**Recommended limits for safety:**
- Start with `max_contacts_per_session: 20` for the first week
- Increase gradually to 50 maximum
- Do NOT run 24/7 — run once per day maximum
- Use `schedule.run_at` during business hours (9am–6pm)

---

## ❓ COMMON PROBLEMS & FIXES

**Problem:** `selenium` not found
**Fix:** Run `pip install selenium`

---

**Problem:** Chrome doesn't open / ChromeDriver error
**Fix:** Run `pip install webdriver-manager` — the bot handles ChromeDriver automatically

---

**Problem:** Bot can't find message box on Facebook
**Fix:** Facebook sometimes changes its layout. Try:
1. Log in manually and make sure you can see your inbox
2. Check that you are on the **Business Suite** inbox URL
3. Wait for the page to fully load before the bot starts

---

**Problem:** Gmail email not sending
**Fix:**
1. Make sure you used an **App Password** (not your real password)
2. Make sure **2-Step Verification** is ON in your Google account
3. Check that `smtp_port: 587` and `use_tls: true` in config

---

**Problem:** Bot sends to wrong people
**Fix:** Use the target filter in config.yaml:
```yaml
target_contacts:
  - "Ahmed Khan"
  - "Sara Malik"
```

---

## 📌 BEST PRACTICES FOR SELLING TO SMALL BUSINESSES

1. **Advise clients to start slow** — 20 messages/day for week 1
2. **Templates should feel personal** — use {name} always
3. **Only message people who messaged them first** — this is the key rule
4. **Keep logs** — so clients have a record of all activity
5. **Run during business hours** — 9am to 6pm only
6. **Do not run every day** — every 2–3 days is safer for Facebook

---

## 🔧 CUSTOMIZATION FOR RESELLING

To rebrand this tool for your clients:

1. Change the bot name in `engagebot.py` (line 8: `EngageBot`)
2. Update the print messages in `run_facebook.py` and `run_email.py`
3. Create a custom `config.yaml` for each client with their:
   - Business name
   - Email credentials
   - Message templates
   - Contact list

Each client gets their own folder with their own config and contacts file.

---

## 📞 SUPPORT

For issues or customization, check the `logs/` folder first —
most problems are explained clearly in the log file.

---

*EngageBot v2.0 — Built for legitimate customer engagement.*
*Use responsibly: only message people who have consented to hear from you.*
