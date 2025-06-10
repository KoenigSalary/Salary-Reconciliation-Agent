# auto_run.py

from salary_automation import setup_environment
from rms_login import login_rms, download_salary_sheet, download_bank_soa, close_driver
from reconciliation import run_full_reconciliation
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
import datetime

def send_report_email(smtp_user, smtp_pass, report_path, to_email):
    msg = MIMEMultipart()
    msg['Subject'] = '✅ Reconciliation Report - Auto Generated'
    msg['From'] = smtp_user
    msg['To'] = to_email

    msg.attach(MIMEText("Please find the attached reconciliation report.", 'plain'))

    with open(report_path, "rb") as file:
        part = MIMEApplication(file.read(), Name=os.path.basename(report_path))
        part['Content-Disposition'] = f'attachment; filename="{os.path.basename(report_path)}"'
        msg.attach(part)

    server = smtplib.SMTP("smtp.office365.com", 587)
    server.starttls()
    server.login(smtp_user, smtp_pass)
    server.send_message(msg)
    server.quit()

if __name__ == "__main__":
    env = setup_environment()

    # 1. Login and download
    driver = login_rms()
    download_salary_sheet(driver, "data")
    download_bank_soa(driver, "data")
    close_driver(driver)

    # 2. Define file paths
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    base_path = f"data/{today}"
    epf_path = os.path.join(base_path, "epf_payment.xlsx")  # Assumes uploaded on 24th
    salary_path = os.path.join(base_path, "salary_sheet.xlsx")
    tds_path = os.path.join(base_path, "tds_payment.xlsx")
    bank_soa_path = os.path.join(base_path, "bank_soa.xlsx")

    # 3. Run reconciliation
    report_path = run_full_reconciliation(epf_path, salary_path, tds_path, bank_soa_path)

    # 4. Email result
    send_report_email(env["smtp_user"], env["smtp_pass"], report_path, "praveen.chaudhary@koenig-solutions.com")
