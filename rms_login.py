from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from dotenv import load_dotenv
import os

def login_rms():
    load_dotenv()
    rms_url = os.getenv("RMS_URL", "https://rms.koenig-solutions.com/")
    rms_user = os.getenv("RMS_USER")
    rms_pass = os.getenv("RMS_PASS")

    if not rms_user or not rms_pass:
        raise ValueError("RMS_USER and RMS_PASS must be set in the .env file.")

    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=options)
    driver.get(rms_url)

    driver.find_element(By.ID, "txtUserName").send_keys(rms_user)
    driver.find_element(By.ID, "txtPassword").send_keys(rms_pass)
    driver.find_element(By.ID, "btnSubmit").click()
    time.sleep(2)
    return driver