import streamlit as st
import datetime
import os
import sys
import glob

# Add the parent directory to sys.path so we can import from aws_auth and billing_runner
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aws_auth import check_aws_session
from billing_runner import run_961, run_leb, run_ksa

st.set_page_config(page_title="AWS Org Billing UI", layout="wide")

st.title("AWS Organization Billing")
st.markdown("Generate and manage AWS billing reports across different regions/profiles.")

# --- Sidebar: AWS Authentication ---
st.sidebar.header("AWS Authentication")

# Mapping of nice names to AWS profiles
PROFILES = {
    "Offshore": "kloudr-961",
    "Lebanon": "kloudr-leb",
    "KSA": "kloudr-ksa"
}

selected_auth_profile = st.sidebar.selectbox("Check Status For Profile:", list(PROFILES.values()))

# Check session
is_logged_in, msg = check_aws_session(selected_auth_profile)

if is_logged_in:
    st.sidebar.success("✅ " + msg)
else:
    st.sidebar.error("❌ Not logged in or expired session.")
    st.sidebar.warning(msg)
    st.sidebar.info(f"Please run `aws login` in your terminal, then click Refresh.")

if st.sidebar.button("Refresh Status"):
    st.rerun()

st.sidebar.markdown("---")

# --- Main Area: Report Generation ---
st.header("Generate Reports")

col1, col2 = st.columns(2)

with col1:
    today = datetime.date.today()
    first_of_month = today.replace(day=1)
    last_month_first = (first_of_month - datetime.timedelta(days=1)).replace(day=1)
    
    start_date = st.date_input("Start Date", value=last_month_first)
    
with col2:
    end_date = st.date_input("End Date", value=first_of_month)

region = st.selectbox("Region/Profile to Run:", ["Offshore", "Lebanon", "KSA", "All"])

if st.button("Run Reports", type="primary"):
    str_start = start_date.strftime("%Y-%m-%d")
    str_end = end_date.strftime("%Y-%m-%d")
    
    with st.status("Running Billing Reports...", expanded=True) as status:
        try:
            if region == "Offshore" or region == "All":
                st.write("Running Offshore billing...")
                run_961(str_start, str_end)
            if region == "Lebanon" or region == "All":
                st.write("Running Lebanon billing...")
                run_leb(str_start, str_end)
            if region == "KSA" or region == "All":
                st.write("Running KSA billing...")
                run_ksa(str_start, str_end)
            status.update(label="Billing Reports Complete!", state="complete", expanded=False)
            st.success("Reports generated successfully!")
        except Exception as e:
            status.update(label="Error occurred", state="error", expanded=True)
            st.error(f"An error occurred: {e}")

st.markdown("---")

# --- File Browser ---
st.header("Generated Reports")
st.markdown("Download generated `.xlsx` files from the `excel_output/` directory.")

excel_output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "excel_output")
if not os.path.exists(excel_output_dir):
    os.makedirs(excel_output_dir)

# Find all excel files
excel_files = []
for root, _, files in os.walk(excel_output_dir):
    for f in files:
        if f.endswith('.xlsx'):
            excel_files.append(os.path.join(root, f))

if not excel_files:
    st.info("No generated reports found.")
else:
    for file_path in sorted(excel_files, reverse=True):
        rel_path = os.path.relpath(file_path, excel_output_dir)
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(rel_path)
        with col2:
            with open(file_path, "rb") as f:
                st.download_button(
                    label="Download",
                    data=f,
                    file_name=os.path.basename(file_path),
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key=file_path
                )
