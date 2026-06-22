"""
EngageBot — Web Development Email Campaign Runner
===================================================
Run this script to send emails ONLY for Web Development.
Usage: python run_email_web.py
"""

import sys
from engagebot import load_config, setup_logger, SessionReport, EmailSender, print_summary


def main():
    print("\n" + "="*50)
    print("  EngageBot — Web Dev Campaign Runner")
    print("="*50 + "\n")

    # Load from the new web config file instead
    cfg = load_config("config_web.yaml")
    logger = setup_logger(cfg)
    report = SessionReport(cfg)
    email_sender = EmailSender(cfg, logger)

    if not cfg["email"].get("enabled", False):
        print("\n[!] Email is disabled in config_web.yaml")
        print("    Set  email.enabled: true  to use this feature.\n")
        sys.exit(0)

    contacts_file = cfg.get("contacts", {}).get("csv_file", "test_websiteemails.csv")
    template_key  = cfg["messaging"].get("default_template", "modern_website_pitch")

    logger.info(f"Contacts file : {contacts_file}")
    logger.info(f"Template      : {template_key}")

    confirm = input("\nSend emails now? (yes/no): ").strip().lower()
    if confirm != "yes":
        print("Cancelled.")
        sys.exit(0)

    email_sender.send_campaign(contacts_file, template_key, report)
    print_summary(report, logger, email_sender, cfg)


if __name__ == "__main__":
    main()