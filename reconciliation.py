import pandas as pd
import os
import datetime

def load_files(epf_path, salary_path, tds_path, bank_soa_path):
    epf_df = pd.read_excel(epf_path)
    salary_df = pd.read_excel(salary_path)
    tds_df = pd.read_excel(tds_path)
    bank_soa_df = pd.read_excel(bank_soa_path)
    return epf_df, salary_df, tds_df, bank_soa_df

def clean_dataframes(epf_df, salary_df, tds_df, bank_soa_df):
    epf_df.columns = epf_df.columns.str.strip()
    salary_df.columns = salary_df.columns.str.strip()
    tds_df.columns = tds_df.columns.str.strip()
    bank_soa_df.columns = bank_soa_df.columns.str.strip()

    salary_df = salary_df.dropna(subset=['Employee ID'])
    epf_df = epf_df.dropna(subset=['UAN'])
    tds_df = tds_df.dropna(subset=['Employee ID'])
    bank_soa_df = bank_soa_df.dropna(subset=['Particulars'])

    return epf_df, salary_df, tds_df, bank_soa_df

def perform_reconciliation(epf_df, salary_df, tds_df, bank_soa_df):
    # Merge Salary and EPF on UAN
    merged_df = pd.merge(salary_df, epf_df, how="left", on="UAN")

    # Merge with TDS on Employee ID
    merged_df = pd.merge(merged_df, tds_df, how="left", on="Employee ID", suffixes=('', '_TDS'))

    # Identify salary payments from bank SOA
    bank_soa_df['Particulars'] = bank_soa_df['Particulars'].astype(str)
    salary_in_bank = bank_soa_df[bank_soa_df['Particulars'].str.contains('Salary', case=False, na=False)]

    # Flag if Employee ID exists in bank SOA
    merged_df["Salary_Paid_in_Bank"] = merged_df["Employee ID"].isin(salary_in_bank['Employee ID']).astype(int)

    # Flag missing values
    merged_df["EPF_Missing"] = merged_df["EPF Amount"].isnull()
    merged_df["TDS_Missing"] = merged_df["TDS Amount"].isnull()
    merged_df["Salary_Not_Paid_in_Bank"] = merged_df["Salary_Paid_in_Bank"] == 0

    return merged_df

def save_reconciliation_report(reconciled_df, save_folder):
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    output_folder = f"SalaryReports/{today}"
    os.makedirs(output_folder, exist_ok=True)
    output_path = os.path.join(output_folder, "reconciliation_result.xlsx")
    reconciled_df.to_excel(output_path, index=False)
    return output_path

def run_full_reconciliation(epf_file, salary_file, tds_file, bank_soa_file):
    epf_df, salary_df, tds_df, bank_soa_df = load_files(epf_file, salary_file, tds_file, bank_soa_file)
    epf_df, salary_df, tds_df, bank_soa_df = clean_dataframes(epf_df, salary_df, tds_df, bank_soa_df)
    reconciled_df = perform_reconciliation(epf_df, salary_df, tds_df, bank_soa_df)
    output_path = save_reconciliation_report(reconciled_df, "SalaryReports")
    return output_path

def run_reconciliation():
    base_dir = os.path.dirname(os.path.abspath(__file__))  # full path of script directory
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    data_folder = os.path.join(base_dir, "data", today)

    epf_path = os.path.join(data_folder, "epf_payment.xlsx")
    salary_path = os.path.join(data_folder, "salary.xlsx")
    tds_path = os.path.join(data_folder, "tds.xlsx")
    bank_soa_path = os.path.join(data_folder, "bank_soa.xlsx")

    file_map = {
        "epf_payment.xlsx": epf_path,
        "salary.xlsx": salary_path,
        "tds.xlsx": tds_path,
        "bank_soa.xlsx": bank_soa_path
    }

    missing_files = [name for name, path in file_map.items() if not os.path.exists(path)]

    if missing_files:
        raise FileNotFoundError(f"The following file(s) are missing in {data_folder}:\n" + "\n".join(missing_files))

    final_report = run_full_reconciliation(epf_path, salary_path, tds_path, bank_soa_path)
    print(f"Reconciliation completed. Report saved at: {final_report}")
    return final_report

