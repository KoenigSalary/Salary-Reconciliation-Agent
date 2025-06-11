from salary_automation import setup_environment
import smtplib
from email.mime.text import MIMEText

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

if __name__ == "__main__":
    try:
        folder, smtp_user, smtp_pass = setup_environment()
        send_epf_reminder(smtp_user, smtp_pass)
        print("EPF Reminder Email Sent Successfully!")
    except Exception as e:
        print(f"Error sending EPF Reminder: {e}")
