## 1. Setup and Dependencies

- [x] 1.1 Add `streamlit` to `requirements.txt`
- [x] 1.2 Create the `ui/` directory for the Streamlit application

## 2. Refactor Core Logic

- [x] 2.1 Create `billing_runner.py` that encapsulates the logic from `run_961.sh`, `run_leb.sh`, and `run_ksa.sh`
- [x] 2.2 Refactor `aws_billing/aws_billing.py` to expose a function that can be called with arguments, avoiding direct CLI-only execution

## 3. AWS Authentication Integration

- [x] 3.1 Implement an AWS session check utility using `boto3.sts.get_caller_identity`
- [x] 3.2 Implement an `aws_login` function that triggers `aws login` (or `aws sso login`) via `subprocess`

## 4. Streamlit UI Implementation

- [x] 4.1 Implement the basic layout of `ui/app.py` with title and description
- [x] 4.2 Add date range selection components (Start Date, End Date)
- [x] 4.3 Add a profile/region selector (961, Lebanon, KSA, or All)
- [x] 4.4 Implement the "Run Reports" button with progress tracking and log output
- [x] 4.5 Implement an "AWS Status" sidebar component showing current login status and a "Login" button
- [x] 4.6 Add a file list component to show and download generated `.xlsx` files from `excel_output/`

## 5. Verification

- [x] 5.1 Run the Streamlit UI locally and verify all components render correctly
- [x] 5.2 Test the AWS login flow through the UI
- [x] 5.3 Trigger a report run from the UI and verify the output files are generated in the correct directories
