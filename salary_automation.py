import datetime
import logging
import os
from dotenv import load_dotenv

def setup_environment():
    load_dotenv()
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")

    if not smtp_user or not smtp_pass:
        raise ValueError("SMTP_USER and SMTP_PASS must be set in the .env file.")

    now = datetime.datetime.now()
    current_year = now.year
    current_month = now.month

    if current_month == 1:
        previous_month = 12
        previous_year = current_year - 1
    else:
        previous_month = current_month - 1
        previous_year = current_year

    previous_month_name = datetime.date(previous_year, previous_month, 1).strftime("%B")
    folder_name = f"SalaryReports/{previous_month_name}_{previous_year}"
    os.makedirs(folder_name, exist_ok=True)

    logging.basicConfig(
        filename=f"{folder_name}/automation.log",
        level=logging.INFO,
        format="%(asctime)s:%(levelname)s:%(message)s"
    )

    return folder_name, smtp_user, smtp_pass
