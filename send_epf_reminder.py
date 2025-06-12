def send_epf_reminder(smtp_user, smtp_pass):
    import smtplib
    from email.mime.text import MIMEText

    to_email = "tax@koenig-solutions.com"
    subject = "EPF Upload Reminder"
    body = """Dear Team,

This is a friendly reminder to upload the EPF sheet for last month.

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
