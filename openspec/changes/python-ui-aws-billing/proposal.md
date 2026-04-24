## Why

The current process for generating AWS billing reports involves manual CLI execution of multiple shell scripts and separate AWS login steps. This is error-prone and lacks a user-friendly interface for date selection and process monitoring. A local Python-based UI will streamline the workflow and make the tool more accessible.

## What Changes

- Add a Streamlit-based local UI for interacting with the billing system.
- Implement a date picker for selecting billing periods.
- Add UI controls to trigger the billing generation process (equivalent to `run.sh`).
- Integrate AWS authentication management into the UI to ensure a valid session before running reports.
- Refactor script execution logic to be callable from Python.

## Capabilities

### New Capabilities
- `billing-ui`: A local web interface providing date selection and report generation triggers.
- `aws-auth-manager`: A component to handle AWS login/SSO authentication and session validation.

### Modified Capabilities
<!-- No existing capabilities to modify. -->

## Impact

- **New Dependencies**: `streamlit`, `boto3` (if not already present), and potentially `aws-sso-util` or similar for login helpers.
- **Project Structure**: Addition of a `ui/` directory for Streamlit components.
- **Execution Flow**: Shift from direct shell script execution to a Python-driven execution model.
