# AWS Cost Management Scripts (Work in Progress and Testing)

This repository contains three Python functions that interact with the AWS Cost Management Service to retrieve and report billing information:

- get_list_of_accounts: Retrieves a paginated list of AWS accounts using the IAM service and returns them as Account objects (assuming you have an Account class defined).
- aws_billing: Fetches AWS billing cost data for a specified period, grouped by linked account, and prints a table summarizing the results.
- aws_billing_service: Similar to aws_billing.py, but also groups the data by service within each linked account.

# Installation
`python3 -m venv .vevn`

`. .venv/bin/activate`

`python3 -m pip install -r requirements`

# Execution
Ensure you have an environment variable named AWS_PROFILE set before running the following command.

`python3 aws-billing.py`

# Contributing
[Contributing](CONTRIBUTING.md)

# License
[License](LICENSE)