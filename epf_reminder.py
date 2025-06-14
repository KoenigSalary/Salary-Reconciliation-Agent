import os
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.utils import formataddr
from dotenv import load_dotenv

# Constants
EPF_FOLDER = "epf_uploads"
REMINDER_LOG_PATH = "epf_reminder_log.txt"

# Function to send reminder email
def epf_reminder(smtp_user, smtp_pass, body=None, subject=None):
    to_email = "tax@koenig-solutions.com"
    body = body or """Dear Team,

This is a friendly reminder to upload the EPF sheet for last month.

Regards,
Tax Team
"""
    subject = subject or "EPF Upload Reminder"

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = formataddr(("Tax Team", smtp_user))
    msg['To'] = to_email

    try:
        with smtplib.SMTP("smtp.office365.com", 587) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
        print("✅ EPF Reminder Email Sent Successfully!")
        return True
    except Exception as e:
        print(f"❌ Failed to send reminder: {e}")
        return False

# Detect uploaded EPF file (auto-check folder only)
def check_epf_uploaded():
    if not os.path.exists(EPF_FOLDER):
        print("📁 EPF folder not found.")
        return False
    for file in os.listdir(EPF_FOLDER):
        if file.lower().endswith(('.xls', '.xlsx')):
            print(f"📄 EPF file detected: {file}")
            return True
    print("⚠️ No EPF file found.")
    return False

# Prevent duplicate reminders in same hour
def already_sent_reminder(hour):
    today = datetime.now().strftime("%Y-%m-%d")
    log_entry = f"{today}-{hour}"
    if os.path.exists(REMINDER_LOG_PATH):
        with open(REMINDER_LOG_PATH, "r") as f:
            if log_entry in f.read():
                return True
    with open(REMINDER_LOG_PATH, "a") as f:
        f.write(log_entry + "\n")
    return False

# Entry point
print("🚀 EPF Reminder Script Started")
if __name__ == "__main__":
    load_dotenv()
    SMTP_USER = os.getenv("SMTP_USER")
    SMTP_PASS = os.getenv("SMTP_PASS")

    if not SMTP_USER or not SMTP_PASS:
        raise ValueError("SMTP_USER or SMTP_PASS not set in .env")

    now = datetime.now()
    current_day = now.day
    current_hour = now.hour

    # ✅ Allow execution only on 1st at midnight or on 24th
    if not (current_day == 24 or (current_day == 1 and current_hour == 0)):
        print(f"⛔ Today is {current_day}, {current_hour}:00. Not the scheduled time. Exiting.")
        exit()

    # 🧹 Monthly Reset on 1st at 00:00
    if current_day == 1 and current_hour == 0:
        if os.path.exists(REMINDER_LOG_PATH):
            os.remove(REMINDER_LOG_PATH)
            print("🧹 Cleared reminder log for the new month.")
        exit()  # Exit after reset

    # 📧 Send reminder on 24th if file not uploaded and not already sent for this hour
    if current_day == 24:
        uploaded = check_epf_uploaded()
        if uploaded:
            print("✅ EPF already uploaded. No reminder needed.")
        elif current_hour in [9, 14, 18]:
            if not already_sent_reminder(current_hour):
                epf_reminder(SMTP_USER, SMTP_PASS)
            else:
                print(f"⏱ Reminder already sent for {current_hour}:00 today. Skipping.")
        else:
            print(f"🕒 Current time {current_hour}:00 is not a reminder slot. Skipping.")
