import os
import shutil
import glob
from aws_billing.aws_billing import run_billing

def move_excel_files(destination_dir):
    os.makedirs(destination_dir, exist_ok=True)
    excel_files = glob.glob("./excel_output/*.xlsx")
    for f in excel_files:
        shutil.move(f, os.path.join(destination_dir, os.path.basename(f)))

def run_961(start_date, end_date):
    print("Running 961 Billing...")
    os.environ["AWS_PROFILE"] = "kloudr-961"
    run_billing(start_date, end_date, False, "", "Name", "offshore", "")
    run_billing(start_date, end_date, True, "AWS Bentham Science", "Name", "offshore", "")
    run_billing(start_date, end_date, True, "AWS Bentham Science", "Name", "offshore", "btsc")
    run_billing(start_date, end_date, True, "AWS Bentham Science", "Name", "offshore", "personal")
    move_excel_files("./excel_output/offshore")

def run_leb(start_date, end_date):
    print("Running Lebanon Billing...")
    os.environ["AWS_PROFILE"] = "kloudr-leb"
    run_billing(start_date, end_date, False, "", "Name", "lebanon", "")
    run_billing(start_date, end_date, True, "AWS OMT", "Name", "lebanon", "")
    run_billing(start_date, end_date, True, "AWS Connect", "Name", "lebanon", "")
    run_billing(start_date, end_date, True, "AWS CSS Freighters", "Name", "lebanon", "")
    run_billing(start_date, end_date, True, "AWS CSS Providers", "Name", "lebanon", "")
    move_excel_files("./excel_output/leb")

def run_ksa(start_date, end_date):
    print("Running KSA Billing...")
    os.environ["AWS_PROFILE"] = "kloudr-ksa"
    run_billing(start_date, end_date, False, "", "Name", "ksa", "")
    move_excel_files("./excel_output/ksa")
