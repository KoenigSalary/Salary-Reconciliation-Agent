import os
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.utils import formataddr
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
EPF_FOLDER = "epf_uploads"  # Folder where EPF sheet is uploaded
EPF_FLAG_PATH = "epf_uploaded.flag"  # Flag file path

# Email config
def send_epf_reminder():
    to_email = "tax@koenig-solutions.com"
    subject = "EPF Upload Reminder"
    body = """Dear Team,

This is a friendly reminder to upload the EPF sheet for last month.

Regards,
Tax Team
"""
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = formataddr(("Tax Team", SMTP_USER))
    msg['To'] = to_email

    with smtplib.SMTP("smtp.office365.com", 587) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)

    print("✅ EPF Reminder Email Sent Successfully!")

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

# Entry point for cron or GitHub Action
if __name__ == "__main__":
    if not SMTP_USER or not SMTP_PASS:
        raise ValueError("SMTP_USER or SMTP_PASS not set in .env")

    now = datetime.now()
    current_day = now.day
    current_hour = now.hour

    # Reset flag on 1st of the month
    if current_day == 1 and current_hour == 0:
        if os.path.exists(EPF_FLAG_PATH):
            os.remove(EPF_FLAG_PATH)
            print("🧹 Reset EPF flag for the new month.")

    # On 24th, check if EPF uploaded
    elif current_day == 24:
        if os.path.exists(EPF_FLAG_PATH):
            print("✅ EPF already uploaded. Skipping reminders.")
        else:
            uploaded = check_epf_uploaded()
            if not uploaded and current_hour in [9, 14, 18]:
                send_epf_reminder()
            elif not uploaded:
                print(f"⏱ Not a scheduled reminder time: {current_hour}h")
