"""
EngageBot — Email Campaign Runner
===================================
Run this script to send emails ONLY (no browser needed).
Usage: python run_email.py
"""

import sys
from engagebot import load_config, setup_logger, SessionReport, EmailSender, print_summary


def main():
    print("\n" + "="*50)
    print("  EngageBot — Email Campaign Runner")
    print("="*50 + "\n")

    config_path = sys.argv[1] if len(sys.argv) > 1 else "config.yaml"
    cfg = load_config(config_path)
    logger = setup_logger(cfg)
    report = SessionReport(cfg)
    email_sender = EmailSender(cfg, logger)

    if not cfg["email"].get("enabled", False):
        print("\n[!] Email is disabled in config.yaml")
        print("    Set  email.enabled: true  to use this feature.\n") 
        sys.exit(0)

    contacts_file = cfg.get("contacts", {}).get("csv_file", "contacts.csv")
    template_key  = cfg["messaging"].get("default_template", "student_issue_resolution") 

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
