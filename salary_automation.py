import os
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText

def setup_environment():
    load_dotenv()
    folder = os.getcwd()
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")
    if not smtp_user or not smtp_pass:
        raise ValueError("SMTP_USER or SMTP_PASS not set in .env")
    return folder, smtp_user, smtp_pass

def send_epf_reminder(smtp_user, smtp_pass):
    to_email = "tax@koenig-solutions.com"
    subject = "EPF Upload Reminder"
    body = """Dear Team,

This is a friendly reminder to upload the EPF sheet for this month.

Regards,
Tax Team
"""
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = smtp_user
    msg['To'] = to_email

    with smtplib.SMTP("smtp.office365.com", 587) as server:
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)
