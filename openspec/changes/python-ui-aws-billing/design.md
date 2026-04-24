## Context

The project currently uses shell scripts (`run.sh`, `run_961.sh`, etc.) to orchestrate AWS billing report generation. This process involves manual date entry and AWS authentication via CLI. The goal is to provide a local Python UI to make this process more intuitive and robust.

## Goals / Non-Goals

**Goals:**
- Provide a Streamlit-based web interface for running billing reports.
- Allow users to select start and end dates via a UI component.
- Handle AWS authentication (SSO) from within the UI.
- Provide real-time feedback (logs) during report generation.
- List generated reports for easy access.

**Non-Goals:**
- Replacing the existing CLI scripts (they should remain as an alternative).
- Building a full cloud-hosted dashboard (the UI is for local use).

## Decisions

- **Framework**: Use **Streamlit** for the UI. It allows rapid development of data-focused interfaces and handles Python integration natively.
- **Orchestration**: Create a Python-based `BillingRunner` that replicates the logic in the `.sh` files. This allows the UI to trigger specific "jobs" (e.g., Run Lebanon, Run 961, Run KSA) or run all of them.
- **AWS Authentication**: Rely on the terminal CLI (`aws login`) for authentication. The UI will only verify the authentication status using `boto3` (`sts get-caller-identity`). If invalid, it will prompt the user to run the command in their terminal. This avoids complexities with subprocess interaction and browser popups.
- **Concurrency**: Run the billing scripts in a background thread or process to prevent the Streamlit UI from freezing during execution.
- **File Management**: Maintain the existing `excel_output/` structure but add a UI section to browse and download/open these files.

## Risks / Trade-offs

- [Risk] Streamlit is not ideal for handling long-running processes without careful implementation of threading/state. → [Mitigation] Use `st.status` and background threads to keep the UI responsive.
- [Risk] `aws sso login` requires browser interaction. → [Mitigation] The UI will trigger the command, and the user will follow the usual CLI-SSO flow in their browser. The UI will wait for completion.
- [Risk] Replicating `.sh` logic in Python might lead to duplication. → [Mitigation] Refactor the `.sh` logic into a configuration-driven Python runner that both the UI and future CLI scripts can use.
