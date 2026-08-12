import os
import zipfile
from datetime import datetime

import pandas as pd
import streamlit as st
from jinja2 import Template
from weasyprint import HTML

# -----------------------------------------------------------------------------
# Streamlit App Configuration
# -----------------------------------------------------------------------------
st.set_page_config(page_title="Recruitr Payroll", layout="centered")

st.title("Recruitr™ Payroll PDF Generator")

if os.path.exists("payroll_app_logo.png"):
    st.image("payroll_app_logo.png", width=300)

uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])

output_folder = "generated_payslips"
os.makedirs(output_folder, exist_ok=True)

# -----------------------------------------------------------------------------
# HTML & CSS Template for Payslip PDF
# -----------------------------------------------------------------------------
html_template = """
<!DOCTYPE html>
<html>
<head>
<style>
    @page {
        size: A4;
        margin: 15mm;
        @bottom-center {
            content: "Powered by Recruitr™ People Tech";
            font-family: 'Helvetica Neue', Arial, sans-serif;
            font-size: 9pt;
            color: #888888;
            border-top: 1px solid #e0e0e0;
            width: 100%;
            padding-top: 8px;
        }
    }
    
    body {
        font-family: 'Helvetica Neue', Arial, sans-serif;
        font-size: 10pt;
        color: #2c3e50;
        line-height: 1.4;
        margin: 0;
        padding: 0;
    }

    /* Header Styling */
    .company-header {
        text-align: center;
        padding-bottom: 15px;
        margin-bottom: 20px;
        border-bottom: 2px solid #2c3e50;
    }
    .company-header h2 {
        margin: 0 0 5px 0;
        font-size: 16pt;
        color: #1a365d;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .company-header h3 {
        margin: 0;
        font-size: 12pt;
        color: #4a5568;
        font-weight: 500;
    }

    /* Common Table Styles */
    table {
        width: 100%;
        border-collapse: collapse;
    }

    .info-table {
        margin-bottom: 20px;
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 4px;
    }

    .info-table td {
        padding: 8px 12px;
        border-bottom: 1px solid #edf2f7;
    }

    .info-table tr:last-child td {
        border-bottom: none;
    }

    .label {
        font-weight: 600;
        color: #4a5568;
        width: 18%;
        background-color: #f1f5f9;
    }

    .value {
        color: #1a202c;
        width: 32%;
    }

    /* Financial Side-by-Side Tables */
    .payroll-container {
        width: 100%;
        margin-bottom: 20px;
    }

    .col-left {
        width: 49%;
        vertical-align: top;
        padding-right: 1%;
    }

    .col-right {
        width: 49%;
        vertical-align: top;
        padding-left: 1%;
    }

    .financial-table {
        border: 1px solid #cbd5e1;
    }

    .financial-table th {
        background-color: #1e293b;
        color: #ffffff;
        font-weight: 600;
        text-align: left;
        padding: 8px 12px;
        font-size: 9.5pt;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .financial-table td {
        padding: 7px 12px;
        border-bottom: 1px solid #e2e8f0;
        font-size: 9.5pt;
    }

    .financial-table tr:nth-child(even) {
        background-color: #f8fafc;
    }

    .text-right {
        text-align: right;
    }

    .total-row td {
        background-color: #e2e8f0 !important;
        font-weight: bold;
        color: #0f172a;
        border-top: 2px solid #cbd5e1;
        border-bottom: none;
    }

    /* Net Pay Highlight Box */
    .net-pay-card {
        background: #f0fdf4;
        border: 1px solid #bbf7d0;
        border-left: 6px solid #16a34a;
        padding: 12px 16px;
        margin-top: 15px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .net-pay-title {
        font-size: 11pt;
        font-weight: bold;
        color: #15803d;
        text-transform: uppercase;
    }

    .net-pay-amount {
        font-size: 15pt;
        font-weight: bold;
        color: #166534;
        float: right;
    }

    .clear {
        clear: both;
    }
</style>
</head>
<body>

<div class="company-header">
    <h2>CRAFTECHCO IT SOLUTIONS PRIVATE LIMITED</h2>
    <h3>Payslip for {{month}}</h3>
</div>

<!-- Employee Details Header -->
<table class="info-table">
    <tr>
        <td class="label">Employee Name</td>
        <td class="value">{{name}}</td>
        <td class="label">Employee ID</td>
        <td class="value">{{emp_id}}</td>
    </tr>
    <tr>
        <td class="label">Designation</td>
        <td class="value">{{designation}}</td>
        <td class="label">Date of Joining</td>
        <td class="value">{{doj}}</td>
    </tr>
    <tr>
        <td class="label">PF Account No.</td>
        <td class="value">{{pf}}</td>
        <td class="label">Pay Date</td>
        <td class="value">{{salary_date}}</td>
    </tr>
</table>

<!-- Earnings & Deductions Tables -->
<table class="payroll-container" style="border: none;">
    <tr style="border: none;">
        <td class="col-left" style="border: none;">
            <table class="financial-table">
                <thead>
                    <tr>
                        <th>Earnings</th>
                        <th class="text-right">Amount</th>
                    </tr>
                </thead>
                <tbody>
                    {% for k, v in earnings.items() %}
                    <tr>
                        <td>{{k}}</td>
                        <td class="text-right">₹ {{ "{:,.2f}".format(v) }}</td>
                    </tr>
                    {% endfor %}
                    <tr class="total-row">
                        <td>Total Earnings</td>
                        <td class="text-right">₹ {{ "{:,.2f}".format(total_earnings) }}</td>
                    </tr>
                </tbody>
            </table>
        </td>
        <td class="col-right" style="border: none;">
            <table class="financial-table">
                <thead>
                    <tr>
                        <th>Deductions</th>
                        <th class="text-right">Amount</th>
                    </tr>
                </thead>
                <tbody>
                    {% for k, v in deductions.items() %}
                    <tr>
                        <td>{{k}}</td>
                        <td class="text-right">₹ {{ "{:,.2f}".format(v) }}</td>
                    </tr>
                    {% endfor %}
                    <tr class="total-row">
                        <td>Total Deductions</td>
                        <td class="text-right">₹ {{ "{:,.2f}".format(total_deductions) }}</td>
                    </tr>
                </tbody>
            </table>
        </td>
    </tr>
</table>

<!-- Net Pay Highlight -->
<div class="net-pay-card">
    <span class="net-pay-title">Take Home Salary (Net Pay)</span>
    <span class="net-pay-amount">₹ {{ "{:,.2f}".format(net_pay) }}</span>
    <div class="clear"></div>
</div>

</body>
</html>
"""

# -----------------------------------------------------------------------------
# Business Logic & Processing
# -----------------------------------------------------------------------------
required = [
    "Name", "ID", "Designation", "DOJ", "PF No.", "Basic", "HRA", "Special",
    "Medical", "Other", "PPF", "PT", "ESIC", "IT", "Loan", "Advance",
    "Month", "Salary Date"
]

if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file)
        
        # Strip trailing/leading spaces from column header names
        df.columns = df.columns.str.strip()

        st.success("Excel uploaded successfully")
        st.dataframe(df)

        st.write("Detected Columns:", list(df.columns))

        missing = [c for c in required if c not in df.columns]
        if missing:
            st.error(f"Missing required columns: {missing}")
            st.stop()

        # Sanitize financial numeric data
        numeric_cols = ["Basic", "HRA", "Special", "Medical", "Other", "PPF", "PT", "ESIC", "IT", "Loan", "Advance"]
        for c in numeric_cols:
            df[c] = pd.to_numeric(
                df[c].astype(str).str.replace(",", "").str.replace("-", "0"), 
                errors="coerce"
            ).fillna(0)

        # Format dates & strings
        df["DOJ"] = pd.to_datetime(df["DOJ"], errors="coerce").dt.strftime("%d-%m-%Y")
        df["Salary Date"] = pd.to_datetime(df["Salary Date"], errors="coerce").dt.strftime("%d-%m-%Y")
        df["PF No."] = df["PF No."].fillna("NA")

        zip_name = f"Payslips_{datetime.now():%Y%m%d_%H%M%S}.zip"
        zip_path = os.path.join(output_folder, zip_name)

        progress = st.progress(0)

        with zipfile.ZipFile(zip_path, "w") as z:
            for i, row in df.iterrows():
                earnings = {
                    "Basic": row["Basic"],
                    "House Rent Allowance": row["HRA"],
                    "Special Allowance": row["Special"],
                    "Medical Allowance": row["Medical"],
                    "Other Allowance": row["Other"]
                }
                deductions = {
                    "PPF": row["PPF"],
                    "PT": row["PT"],
                    "ESIC": row["ESIC"],
                    "Income Tax": row["IT"],
                    "Loan": row["Loan"],
                    "Advance": row["Advance"]
                }

                total_earnings = sum(earnings.values())
                total_deductions = sum(deductions.values())
                net_pay = total_earnings - total_deductions

                html = Template(html_template).render(
                    name=row["Name"],
                    emp_id=row["ID"],
                    designation=row["Designation"],
                    doj=row["DOJ"],
                    pf=row["PF No."],
                    salary_date=row["Salary Date"],
                    month=row["Month"],
                    earnings=earnings,
                    deductions=deductions,
                    total_earnings=total_earnings,
                    total_deductions=total_deductions,
                    net_pay=net_pay
                )

                pdf_name = f'{row["ID"]}_{row["Month"]}_Payslip.pdf'
                pdf_path = os.path.join(output_folder, pdf_name)
                
                # Render HTML string to PDF file
                HTML(string=html).write_pdf(pdf_path)
                
                # Add generated PDF to zip archive
                z.write(pdf_path, arcname=pdf_name)
                
                # Update progress bar
                progress.progress((i + 1) / len(df))

        with open(zip_path, "rb") as f:
            st.success("Payslips generated successfully!")
            st.download_button(
                label="📥 Download Payslips ZIP",
                data=f,
                file_name=zip_name,
                mime="application/zip"
            )

    except Exception as e:
        st.exception(e)
else:
    st.info("Please upload an Excel (.xlsx) file.")