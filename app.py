# --- app.py (Updated with upload support for all 4 Excel files) ---

import streamlit as st
import os
import pandas as pd
import datetime
import reconciliation
from salary_automation import setup_environment, send_epf_reminder
from email.mime.text import MIMEText


# ✅ MUST BE FIRST
st.set_page_config(page_title="Salary Reconciliation Agent", page_icon="📄", layout="wide")

# Title
st.title("📄 Salary Reconciliation AI Agent")

# Setup environment
env_data = setup_environment()

# Section: EPF Email Test
st.subheader("📧 EPF Reminder Email Preview")

default_subject = "EPF Upload Reminder"
default_body = """Dear Team,

This is a reminder to upload EPF before end of day today.

Thanks,
Tax Team
"""

# Editable subject & body
subject = st.text_input("Email Subject", default_subject)
body = st.text_area("Email Body", default_body, height=200)

if st.button("Send Test Email"):
    success = send_epf_reminder(
        smtp_user=st.secrets["SMTP_USER"],
        smtp_pass=st.secrets["SMTP_PASS"],
        body=body
    )
    if success:
        st.success("✅ Test email sent successfully!")
    else:
        st.error("❌ Failed to send email. Check SMTP credentials.")

# Tabs for EPF Upload and Report
tab1, tab2 = st.tabs(["📤 Upload Input Files", "📥 View Reconciliation Report"])

# TAB 1: Upload all 4 input files
with tab1:
    st.header("📤 Upload Salary / EPF / TDS / Bank SOA Files")
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    save_folder = f"data/{today}"
    os.makedirs(save_folder, exist_ok=True)

    files_uploaded = {
        'salary.xlsx': st.file_uploader("📄 Upload Salary Sheet", type=["xlsx"], key="upload_salary"),
        'epf_payment.xlsx': st.file_uploader("📄 Upload EPF Payment Sheet", type=["xlsx"], key="upload_epf"),
        'tds.xlsx': st.file_uploader("📄 Upload TDS Sheet", type=["xlsx"], key="upload_tds"),
        'bank_soa.xlsx': st.file_uploader("📄 Upload Bank SOA Sheet", type=["xlsx"], key="upload_bank"),
    }

    for filename, fileobj in files_uploaded.items():
        if fileobj:
            with open(os.path.join(save_folder, filename), "wb") as f:
                f.write(fileobj.getbuffer())
            st.success(f"✅ {filename} uploaded to {save_folder}")

# TAB 2: Reconciliation Report
with tab2:
    st.header("📥 Reconciliation Report")
    report_path = f"SalaryReports/{today}/reconciliation_result.xlsx"
    if os.path.exists(report_path):
        st.success("Reconciliation Report Found:")
        df = pd.read_excel(report_path)
        st.dataframe(df)
        with open(report_path, "rb") as f:
            st.download_button("📥 Download Report", f, file_name="reconciliation_result.xlsx")
    else:
        st.warning("No reconciliation report available yet. Please check after auto-run on 25th or upload all inputs.")

# Manual Trigger Section
st.divider()
st.subheader("🔄 Manual Reconciliation Trigger")

if st.button("🚀 Run Reconciliation Now"):
    try:
        reconciliation.run_reconciliation()
        st.success("✅ Reconciliation completed successfully!")
    except Exception as e:
        st.error(f"❌ Reconciliation failed: {e}")

if __name__ == "__main__":
    try:
        folder, smtp_user, smtp_pass = setup_environment()
        send_epf_reminder(smtp_user, smtp_pass)
        print("✅ EPF Reminder Email Sent Successfully!")
    except Exception as e:
        print(f"❌ Error sending EPF Reminder: {e}")

