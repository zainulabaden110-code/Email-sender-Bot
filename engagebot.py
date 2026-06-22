"""
EngageBot — Automated Customer Engagement Tool
================================================
Legitimate use only: follow-ups with existing customers,
opted-in contact lists, and your own Facebook Page inbox.

Author: EngageBot
Version: 2.0
"""

import os
import sys
import time
import random
import logging
import csv
import json
from datetime import datetime
from pathlib import Path

import yaml

# Optional imports — checked at runtime
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import (
        TimeoutException, NoSuchElementException,
        StaleElementReferenceException, WebDriverException
    )
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

try:
    import schedule as schedule_lib
    SCHEDULE_AVAILABLE = True
except ImportError:
    SCHEDULE_AVAILABLE = False


# ─────────────────────────────────────────────────────────────
#  Config Loader
# ─────────────────────────────────────────────────────────────

def load_config(path: str = "config.yaml") -> dict:
    """Load and validate configuration from YAML file."""
    if not os.path.exists(path):
        print(f"[ERROR] Config file not found: {path}")
        print("Please make sure config.yaml is in the same folder as this script.")
        sys.exit(1)
    with open(path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    return cfg


# ─────────────────────────────────────────────────────────────
#  Logger Setup
# ─────────────────────────────────────────────────────────────

def setup_logger(cfg: dict) -> logging.Logger:
    """Configure file + console logging."""
    log_dir = Path(cfg["logging"]["log_dir"])
    log_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"engagebot_{timestamp}.log"

    level = getattr(logging, cfg["logging"].get("log_level", "INFO").upper(), logging.INFO)

    logger = logging.getLogger("engagebot")
    logger.setLevel(level)
    logger.handlers.clear()

    # File handler
    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setLevel(level)

    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(level)

    fmt = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    fh.setFormatter(fmt)
    ch.setFormatter(fmt)

    logger.addHandler(fh)
    logger.addHandler(ch)

    logger.info(f"EngageBot started. Log file: {log_file}")
    return logger


# ─────────────────────────────────────────────────────────────
#  Session Report (CSV)
# ─────────────────────────────────────────────────────────────

class SessionReport:
    """Tracks every messaging attempt and saves a CSV report."""

    def __init__(self, cfg: dict):
        self.records = []
        self.log_dir = Path(cfg["logging"]["log_dir"])
        self.save_csv = cfg["logging"].get("save_csv_report", True)
        self.start_time = datetime.now()

    def record(self, name: str, channel: str, status: str, note: str = ""):
        self.records.append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "name": name,
            "channel": channel,      # "facebook" | "email"
            "status": status,        # "success" | "failed" | "skipped"
            "note": note
        })

    def summary(self) -> dict:
        total = len(self.records)
        success = sum(1 for r in self.records if r["status"] == "success")
        failed = sum(1 for r in self.records if r["status"] == "failed")
        skipped = sum(1 for r in self.records if r["status"] == "skipped")
        elapsed = (datetime.now() - self.start_time).seconds
        return {
            "total": total,
            "success": success,
            "failed": failed,
            "skipped": skipped,
            "elapsed_seconds": elapsed
        }

    def save(self):
        if not self.save_csv or not self.records:
            return
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_path = self.log_dir / f"report_{timestamp}.csv"
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=self.records[0].keys())
            writer.writeheader()
            writer.writerows(self.records)
        return csv_path


# ─────────────────────────────────────────────────────────────
#  Email Sender
# ─────────────────────────────────────────────────────────────

class EmailSender:
    """Handles SMTP email sending with retry and templating."""

    def __init__(self, cfg: dict, logger: logging.Logger):
        self.cfg = cfg["email"]
        self.business = cfg.get("business", {})
        self.logger = logger
        self.enabled = self.cfg.get("enabled", False)

    def _build_message(self, template_key: str, to_name: str, to_email: str) -> tuple:
        """Build subject + body from template."""
        import random
        templates = self.cfg.get("email_templates", {})
        if template_key not in templates:
            raise ValueError(f"Email template '{template_key}' not found in config.")

        tpl = templates[template_key]
        
        # Adding variation / spintax
        greetings = [
            "We hope you are doing well.",
            "We hope this email finds you well.",
            "Trust you are having a productive week.",
            "Hope you are having a wonderful day."
        ]
        quotes = [
            "Small daily improvements lead to big long-term results.",
            "Consistency is more powerful than motivation.",
            "Success is the sum of small efforts repeated day in and day out.",
            "The future depends on what you do today."
        ]
        chosen_greeting = random.choice(greetings)
        chosen_quote = random.choice(quotes)
        
        subject = tpl["subject"].format(
            name=to_name,
            business_name=self.business.get("name", "Our Team")
        )
        body = tpl.get("body", "").format(
            name=to_name,
            business_name=self.business.get("name", "Our Team"),
            greeting=chosen_greeting,
            quote=chosen_quote
        )
        
        body_html = None
        if "body_html_file" in tpl:
            try:
                with open(tpl["body_html_file"], "r", encoding="utf-8") as f:
                    body_html = f.read()
                    # Safe replacement for HTML
                    body_html = body_html.replace("{name}", to_name).replace("{business_name}", self.business.get("name", "Our Team")).replace("{greeting}", chosen_greeting).replace("{quote}", chosen_quote)
            except Exception as e:
                self.logger.error(f"Failed to read body_html_file {tpl['body_html_file']}: {e}")
        elif "body_html" in tpl:
            body_html = tpl["body_html"]
            body_html = body_html.replace("{name}", to_name).replace("{business_name}", self.business.get("name", "Our Team")).replace("{greeting}", chosen_greeting).replace("{quote}", chosen_quote)
            
        return subject, body, body_html

    def send(self, to_email: str, to_name: str, template_key: str,
             report: SessionReport, retries: int = 3) -> bool:
        """Send a single email with retry logic."""
        if not self.enabled:
            self.logger.warning("Email sending is disabled in config.")
            return False

        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart

        try:
            subject, body, body_html = self._build_message(template_key, to_name, to_email)
        except ValueError as e:
            self.logger.error(f"Template error: {e}")
            report.record(to_name, "email", "failed", str(e))
            return False

        import uuid
        msg = MIMEMultipart("alternative")
        msg["From"] = self.cfg["sender_email"]
        msg["To"] = to_email
        msg["Subject"] = subject
        
        # Anti-Spam Headers
        msg["Message-ID"] = f"<{uuid.uuid4()}@{self.cfg['sender_email'].split('@')[-1]}>"
        msg["Reply-To"] = self.cfg["sender_email"]
        msg["List-Unsubscribe"] = f"<mailto:{self.cfg['sender_email']}?subject=unsubscribe>"
        
        if body:
            msg.attach(MIMEText(body, "plain", "utf-8"))
        if body_html:
            msg.attach(MIMEText(body_html, "html", "utf-8"))

        wait = self.cfg.get("retry_wait", 5)
        for attempt in range(1, retries + 1):
            try:
                with smtplib.SMTP(self.cfg["smtp_host"], self.cfg["smtp_port"]) as server:
                    if self.cfg.get("use_tls", True):
                        server.starttls()
                    smtp_login = self.cfg.get("smtp_login", self.cfg["sender_email"])
                    server.login(smtp_login, self.cfg["sender_password"])
                    server.sendmail(self.cfg["sender_email"], to_email, msg.as_string())

                self.logger.info(f"[EMAIL] ✓ Sent to {to_name} <{to_email}>")
                report.record(to_name, "email", "success")
                return True

            except Exception as e:
                self.logger.warning(
                    f"[EMAIL] Attempt {attempt}/{retries} failed for {to_email}: {e}"
                )
                if attempt < retries:
                    time.sleep(wait * attempt)

        self.logger.error(f"[EMAIL] ✗ All retries exhausted for {to_email}")
        report.record(to_name, "email", "failed", "All retries failed")
        return False

    def send_campaign(self, contacts_csv: str, template_key: str, report: SessionReport):
        """Send emails to all contacts in a CSV file."""
        if not os.path.exists(contacts_csv):
            self.logger.error(f"Contacts file not found: {contacts_csv}")
            return

        with open(contacts_csv, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            contacts = list(reader)

        if not contacts:
            self.logger.warning("Contacts CSV is empty.")
            return

        self.logger.info(f"Starting email campaign: {len(contacts)} contacts, template '{template_key}'")

        for i, contact in enumerate(contacts, 1):
            name = contact.get("name", "Valued Customer").strip()
            email = contact.get("email", "").strip()

            if not email:
                self.logger.warning(f"Skipping {name} — no email address.")
                report.record(name, "email", "skipped", "No email address")
                continue

            self.logger.info(f"[{i}/{len(contacts)}] Sending to {name} <{email}>")
            self.send(email, name, template_key, report)

            # Polite delay between emails to avoid spam filters
            delay = random.uniform(15, 25)
            time.sleep(delay)

    def send_notification(self, subject: str, body: str):
        """Send a notification email (e.g. session summary) to the business owner."""
        if not self.enabled:
            return
        import smtplib
        from email.mime.text import MIMEText

        msg = MIMEText(body, "plain", "utf-8")
        msg["From"] = self.cfg["sender_email"]
        msg["To"] = self.cfg["recipient_email"]
        msg["Subject"] = subject

        try:
            with smtplib.SMTP(self.cfg["smtp_host"], self.cfg["smtp_port"]) as server:
                if self.cfg.get("use_tls", True):
                    server.starttls()
                server.login(self.cfg["sender_email"], self.cfg["sender_password"])
                server.sendmail(
                    self.cfg["sender_email"],
                    self.cfg["recipient_email"],
                    msg.as_string()
                )
        except Exception as e:
            # Notification failure is non-fatal
            pass


# ─────────────────────────────────────────────────────────────
#  Human-like Typing Helper
# ─────────────────────────────────────────────────────────────

def human_type(element, text: str, min_cps: float, max_cps: float):
    """Type text character by character with random delays (human simulation)."""
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(min_cps, max_cps))


# ─────────────────────────────────────────────────────────────
#  Facebook Messenger Bot
# ─────────────────────────────────────────────────────────────

class FacebookBot:
    """
    Automates follow-up messages to your existing Facebook Page inbox.
    Only messages contacts who have ALREADY initiated a conversation
    with your page.
    """

    # Stable, semantic CSS selectors (more resilient than absolute XPaths)
    # These target Messenger's chat list and input area by role/aria attributes
    SELECTORS = {
        # Chat list items in the inbox sidebar
        "chat_items": [
            "div[role='row']",
            "div[data-testid='mwthreadlist-item']",
            "div[aria-label][role='row']",
        ],
        # Message input box (multiple fallbacks)
        "message_input": [
            "div[role='textbox'][contenteditable='true']",
            "textarea[placeholder]",
            "div[contenteditable='true']",
            "textarea",
        ],
        # Contact/sender name inside a chat item
        "contact_name": [
            "span[dir='auto']",
            "span.x1lliihq",
            "span",
        ]
    }

    def __init__(self, cfg: dict, logger: logging.Logger, report: SessionReport):
        self.cfg = cfg
        self.fb_cfg = cfg["facebook"]
        self.msg_cfg = cfg["messaging"]
        self.delay_cfg = cfg["delays"]
        self.retry_cfg = cfg["retry"]
        self.logger = logger
        self.report = report
        self.driver = None
        self.wait = None
        self.messages_sent = 0

    # ── Template Resolver ────────────────────────────────────

    def _get_message(self, contact_name: str) -> str:
        """Pick a template (randomly from available ones) and fill {name}."""
        templates_dict = self.msg_cfg.get("templates", {})
        default_key = self.msg_cfg.get("default_template", "order_followup")

        all_keys = list(templates_dict.keys())
        if not all_keys:
            return f"Hi {contact_name}! 👋\n\nThank you for reaching out. We'll get back to you shortly!"

        # Use default + alternates for variety
        chosen_key = random.choice(all_keys)
        template = templates_dict.get(chosen_key, templates_dict.get(default_key, ""))
        return template.format(name=contact_name.split()[0] if contact_name else "there")

    # ── Browser Setup ────────────────────────────────────────

    def _setup_driver(self):
        """Launch Chrome with anti-detection options."""
        if not SELENIUM_AVAILABLE:
            self.logger.error("Selenium is not installed. Run: pip install selenium")
            raise RuntimeError("Selenium not available")

        options = webdriver.ChromeOptions()

        # Suppress automation flags (reduces detection risk)
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        # Realistic window size
        options.add_argument("--window-size=1366,768")

        # Optional: use your existing Chrome profile (keeps you logged in)
        # Uncomment the line below and set your profile path:
        # options.add_argument(r"--user-data-dir=C:\Users\YourName\AppData\Local\Google\Chrome\User Data")
        # options.add_argument("--profile-directory=Default")

        self.driver = webdriver.Chrome(options=options)

        # Mask webdriver property
        self.driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )

        self.wait = WebDriverWait(
            self.driver,
            self.fb_cfg.get("page_load_timeout", 20)
        )
        self.logger.info("Chrome browser launched.")

    # ── Login ────────────────────────────────────────────────

    def _login(self):
        """Open Facebook and wait for the user to log in manually."""
        self.driver.get(self.fb_cfg["url"])
        wait_sec = self.fb_cfg.get("login_wait_seconds", 40)

        self.logger.info(
            f"\n{'='*55}\n"
            f"  ACTION REQUIRED: Please log into Facebook now.\n"
            f"  You have {wait_sec} seconds.\n"
            f"  The bot will start automatically after login.\n"
            f"{'='*55}"
        )
        print(f"\n>>> Please log in to Facebook in the browser window.")
        print(f">>> Bot will continue automatically in {wait_sec} seconds...\n")

        for remaining in range(wait_sec, 0, -5):
            print(f"    Starting in {remaining} seconds...", end="\r")
            time.sleep(5)

        self.logger.info("Login wait complete. Proceeding.")

    # ── Find Element with Fallback Selectors ─────────────────

    def _find_element(self, selector_list: list, parent=None, timeout: float = 5):
        """Try multiple CSS selectors and return the first match."""
        context = parent or self.driver
        for selector in selector_list:
            try:
                elements = context.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    return elements
            except Exception:
                continue
        return []

    # ── Get Contact Name ─────────────────────────────────────

    def _get_contact_name(self, chat_element) -> str:
        """Extract the contact's name from a chat list item."""
        for selector in self.SELECTORS["contact_name"]:
            try:
                spans = chat_element.find_elements(By.CSS_SELECTOR, selector)
                for span in spans:
                    text = span.get_attribute("outerText") or span.text
                    if text and len(text.strip()) > 1 and "\n" not in text.strip():
                        return text.strip().split("\n")[0]
            except StaleElementReferenceException:
                break
            except Exception:
                continue
        return "Unknown"

    # ── Find Message Input ───────────────────────────────────

    def _find_message_input(self):
        """Find the message input box using multiple selector fallbacks."""
        for selector in self.SELECTORS["message_input"]:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for el in elements:
                    if el.is_displayed() and el.is_enabled():
                        return el
            except Exception:
                continue
        return None

    # ── Send One Message ─────────────────────────────────────

    def _send_message_to_contact(self, chat_element, contact_name: str) -> bool:
        """Click a chat and send the personalized message."""
        max_attempts = self.retry_cfg.get("max_attempts", 3)
        backoff = self.retry_cfg.get("backoff_factor", 2)

        for attempt in range(1, max_attempts + 1):
            try:
                # Click the conversation
                chat_element.click()
                time.sleep(random.uniform(
                    self.delay_cfg["after_click"],
                    self.delay_cfg["after_click"] + 1
                ))

                # Find message input
                msg_box = self._find_message_input()
                if msg_box is None:
                    raise NoSuchElementException("Message input not found")

                # Build personalized message
                message_text = self._get_message(contact_name)

                # Type like a human
                msg_box.click()
                time.sleep(0.3)
                human_type(
                    msg_box,
                    message_text,
                    self.delay_cfg["typing_min_cps"],
                    self.delay_cfg["typing_max_cps"]
                )

                # Small pause before sending (natural behavior)
                time.sleep(random.uniform(0.5, 1.2))
                msg_box.send_keys(Keys.ENTER)

                self.messages_sent += 1
                self.logger.info(f"  ✓ Message sent to: {contact_name}")
                self.report.record(contact_name, "facebook", "success")
                return True

            except (StaleElementReferenceException, NoSuchElementException) as e:
                wait_time = self.retry_cfg.get("retry_wait", 6) * (backoff ** (attempt - 1))
                self.logger.warning(
                    f"  Attempt {attempt}/{max_attempts} failed for '{contact_name}': {type(e).__name__}. "
                    f"Waiting {wait_time:.0f}s..."
                )
                time.sleep(wait_time)

            except Exception as e:
                self.logger.warning(
                    f"  Attempt {attempt}/{max_attempts} unexpected error for '{contact_name}': {e}"
                )
                time.sleep(self.retry_cfg.get("retry_wait", 6))

        self.logger.error(f"  ✗ Failed to message '{contact_name}' after {max_attempts} attempts.")
        self.report.record(contact_name, "facebook", "failed", "Max retries reached")
        return False

    # ── Main Run Loop ────────────────────────────────────────

    def run(self):
        """Main execution: log in, scroll inbox, send messages."""
        if not SELENIUM_AVAILABLE:
            self.logger.error(
                "Selenium not installed. Run: pip install selenium"
            )
            return

        target_contacts = set(
            n.lower() for n in self.cfg.get("target_contacts", [])
        )
        max_contacts = self.fb_cfg.get("max_contacts_per_session", 50)
        processed = set()

        try:
            self._setup_driver()
            self._login()

            self.logger.info("Starting inbox scan...")
            scroll_attempts = 0
            max_scroll_attempts = 30  # Safety limit

            while len(processed) < max_contacts and scroll_attempts < max_scroll_attempts:
                # Find all chat items currently visible
                chat_items = self._find_element(self.SELECTORS["chat_items"])

                if not chat_items:
                    self.logger.warning("No chat items found. Check selectors or page load.")
                    time.sleep(3)
                    scroll_attempts += 1
                    continue

                new_found = False
                for chat in chat_items:
                    if len(processed) >= max_contacts:
                        break

                    name = self._get_contact_name(chat)
                    name_key = name.lower()

                    # Skip already processed
                    if name_key in processed or name == "Unknown":
                        continue

                    # Apply target filter if set
                    if target_contacts and name_key not in target_contacts:
                        self.logger.debug(f"  Skipping (not in target list): {name}")
                        continue

                    self.logger.info(
                        f"[{len(processed)+1}/{max_contacts}] Processing: {name}"
                    )
                    processed.add(name_key)
                    new_found = True

                    success = self._send_message_to_contact(chat, name)

                    # Batch break
                    if self.messages_sent > 0 and \
                       self.messages_sent % self.delay_cfg.get("batch_size", 20) == 0:
                        break_secs = random.randint(
                            self.delay_cfg["batch_break_min"],
                            self.delay_cfg["batch_break_max"]
                        )
                        self.logger.info(
                            f"\n  >>> Batch break: pausing {break_secs}s to stay safe...\n"
                        )
                        time.sleep(break_secs)

                    # Per-message delay
                    delay = random.uniform(
                        self.delay_cfg["min_between_messages"],
                        self.delay_cfg["max_between_messages"]
                    )
                    self.logger.debug(f"  Waiting {delay:.1f}s before next message...")
                    time.sleep(delay)

                if not new_found:
                    # Scroll down to load more conversations
                    try:
                        sidebar = self.driver.find_elements(
                            By.CSS_SELECTOR, "div[role='navigation']"
                        )
                        if sidebar:
                            self.driver.execute_script(
                                "arguments[0].scrollTop += 500;", sidebar[-1]
                            )
                        else:
                            self.driver.execute_script("window.scrollBy(0, 400);")
                        time.sleep(self.delay_cfg.get("after_scroll", 2))
                        scroll_attempts += 1
                    except Exception as e:
                        self.logger.warning(f"Scroll failed: {e}")
                        scroll_attempts += 1
                else:
                    scroll_attempts = 0  # Reset if we found new contacts

        except KeyboardInterrupt:
            self.logger.info("Bot stopped by user (Ctrl+C).")
        except WebDriverException as e:
            self.logger.error(f"Browser error: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}", exc_info=True)
        finally:
            self._shutdown()

    def _shutdown(self):
        """Close browser gracefully."""
        if self.driver:
            try:
                self.driver.quit()
            except Exception:
                pass
        self.logger.info("Browser closed.")


# ─────────────────────────────────────────────────────────────
#  Summary & Notification
# ─────────────────────────────────────────────────────────────

def print_summary(report: SessionReport, logger: logging.Logger,
                  email_sender: EmailSender, cfg: dict):
    """Print session summary and send notification email."""
    s = report.summary()
    csv_path = report.save()

    summary_lines = [
        "",
        "=" * 50,
        "  EngageBot — Session Complete",
        "=" * 50,
        f"  Total Processed : {s['total']}",
        f"  ✓ Sent          : {s['success']}",
        f"  ✗ Failed        : {s['failed']}",
        f"  ~ Skipped       : {s['skipped']}",
        f"  Time Elapsed    : {s['elapsed_seconds']}s",
    ]
    if csv_path:
        summary_lines.append(f"  Report saved    : {csv_path}")
    summary_lines.append("=" * 50)

    for line in summary_lines:
        logger.info(line)

    # Email notification
    if cfg["email"].get("enabled") and cfg["email"].get("send_summary_on_completion"):
        business_name = cfg.get("business", {}).get("name", "EngageBot")
        subject = f"{business_name} — Bot Session Summary"
        body = "\n".join(summary_lines)
        email_sender.send_notification(subject, body)


# ─────────────────────────────────────────────────────────────
#  Entry Point
# ─────────────────────────────────────────────────────────────

def run_once(cfg: dict, logger: logging.Logger):
    """Run one full bot session (Facebook + optional email campaign)."""
    report = SessionReport(cfg)
    email_sender = EmailSender(cfg, logger)

    # ── Facebook Messenger ───────────────────────────────────
    if cfg["facebook"].get("enabled", True):
        logger.info("Starting Facebook Messenger automation...")
        fb_bot = FacebookBot(cfg, logger, report)
        fb_bot.run()
    else:
        logger.info("Facebook automation is disabled in config.")

    # ── Email Campaign ───────────────────────────────────────
    if cfg["email"].get("enabled", False):
        contacts_file = cfg.get("contacts", {}).get("csv_file", "contacts.csv")
        template_key = cfg["messaging"].get("default_template", "order_followup")
        logger.info(f"Starting email campaign from: {contacts_file}")
        email_sender.send_campaign(contacts_file, template_key, report)
    else:
        logger.info("Email campaign is disabled in config.")

    # ── Summary ──────────────────────────────────────────────
    print_summary(report, logger, email_sender, cfg)


def main():
    print("\n" + "="*55)
    print("  EngageBot v2.0 — Customer Engagement Automation")
    print("  For legitimate use: existing customers & opted-in contacts")
    print("="*55 + "\n")

    cfg = load_config("config.yaml")
    logger = setup_logger(cfg)

    # ── Scheduled mode ───────────────────────────────────────
    sched_cfg = cfg.get("schedule", {})
    if sched_cfg.get("enabled", False):
        if not SCHEDULE_AVAILABLE:
            logger.error("Schedule library not installed. Run: pip install schedule")
            sys.exit(1)

        run_time = sched_cfg.get("run_at", "09:00")
        repeat = sched_cfg.get("repeat", "daily")

        logger.info(f"Scheduler enabled: will run {repeat} at {run_time}")

        def scheduled_job():
            logger.info("Scheduled run starting...")
            run_once(cfg, logger)

        if repeat == "daily":
            schedule_lib.every().day.at(run_time).do(scheduled_job)
        elif repeat == "weekdays":
            for day in ["monday", "tuesday", "wednesday", "thursday", "friday"]:
                getattr(schedule_lib.every(), day).at(run_time).do(scheduled_job)
        else:
            schedule_lib.every().day.at(run_time).do(scheduled_job)

        print(f"Bot scheduled to run {repeat} at {run_time}. Press Ctrl+C to stop.\n")
        while True:
            schedule_lib.run_pending()
            time.sleep(30)
    else:
        # ── Immediate single run ─────────────────────────────
        run_once(cfg, logger)


if __name__ == "__main__":
    main()
