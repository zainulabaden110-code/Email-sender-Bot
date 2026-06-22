"""
EngageBot — Facebook Messenger Runner
=======================================
Run this script to send Facebook messages ONLY.
Usage: python run_facebook.py
"""

import sys
from engagebot import load_config, setup_logger, SessionReport, EmailSender, FacebookBot, print_summary


def main():
    print("\n" + "="*50)
    print("  EngageBot — Facebook Messenger Runner")
    print("="*50)
    print("\n  This tool will message contacts in your Facebook")
    print("  Page inbox — people who already messaged YOU first.\n")

    cfg = load_config("config.yaml")
    logger = setup_logger(cfg)

    if not cfg["facebook"].get("enabled", True):
        print("\n[!] Facebook is disabled in config.yaml")
        print("    Set  facebook.enabled: true  to use this.\n")
        sys.exit(0)

    max_c = cfg["facebook"].get("max_contacts_per_session", 50)
    template = cfg["messaging"].get("default_template", "order_followup")
    targets = cfg.get("target_contacts", [])

    print(f"  Max contacts this session : {max_c}")
    print(f"  Message template          : {template}")
    if targets:
        print(f"  Target filter             : {', '.join(targets)}")
    else:
        print(f"  Target filter             : All inbox contacts")

    confirm = input("\nStart Facebook messaging bot? (yes/no): ").strip().lower()
    if confirm != "yes":
        print("Cancelled.")
        sys.exit(0)

    report  = SessionReport(cfg)
    email_s = EmailSender(cfg, logger)
    fb_bot  = FacebookBot(cfg, logger, report)

    fb_bot.run()
    print_summary(report, logger, email_s, cfg)


if __name__ == "__main__":
    main()
