import os
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.utils import formataddr

EPF_FOLDER = "epf_uploads"
EPF_FLAG_PATH = "epf_uploaded.flag"
REMINDER_LOG_PATH = "epf_reminder_log.txt"

# Reusable function to send EPF reminder (with optional body & subject)
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

# Automatically mark flag if EPF file is detected
def check_epf_uploaded():
    if not os.path.exists(EPF_FOLDER):
        return False
    for file in os.listdir(EPF_FOLDER):
        if file.lower().endswith(('.xls', '.xlsx')):
            with open(EPF_FLAG_PATH, 'w') as f:
                f.write("EPF uploaded")
            print(f"📁 EPF file detected: {file} — Flag created.")
            return True
    return False

# Check if a reminder has already been sent for this hour today
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

# Entry point for cron or automation
print("🚀 EPF Reminder Script Started")
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    SMTP_USER = os.getenv("SMTP_USER")
    SMTP_PASS = os.getenv("SMTP_PASS")

    if not SMTP_USER or not SMTP_PASS:
        raise ValueError("SMTP_USER or SMTP_PASS not set in .env")

    now = datetime.now()
    current_day = now.day
    current_hour = now.hour

    # Reset flag and log on 1st at midnight
    if current_day == 1 and current_hour == 0:
        if os.path.exists(EPF_FLAG_PATH):
            os.remove(EPF_FLAG_PATH)
            print("🧹 Reset EPF flag for the new month.")
        if os.path.exists(REMINDER_LOG_PATH):
            os.remove(REMINDER_LOG_PATH)
            print("🧹 Cleared reminder log for new month.")

    # On 24th, send reminder only if not uploaded and not already sent this hour
    elif True:
        if os.path.exists(EPF_FLAG_PATH):
            print("✅ EPF already uploaded. Skipping reminders.")
        else:
            print("❗ FLAG FILE NOT FOUND")
            uploaded = check_epf_uploaded()
            if not uploaded and current_hour in [9, 14, 18]:
                if not already_sent_reminder(current_hour):
                    epf_reminder(SMTP_USER, SMTP_PASS)
                else:
                    print(f"⏱ Reminder already sent for {current_hour}:00 today. Skipping.")
            elif not uploaded:
                print(f"⏱ Not a scheduled reminder time: {current_hour}:00")
