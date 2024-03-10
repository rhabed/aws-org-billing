# AWS Cost Management Scripts (Work in Progress)

This repository contains three Python functions that interact with the AWS Cost Management Service to retrieve and report billing information:

- get_list_of_accounts: Retrieves a paginated list of AWS accounts using the IAM service and returns them as Account objects (assuming you have an Account class defined).
- aws_billing: Fetches AWS billing cost data for a specified period, grouped by linked account, and prints a table summarizing the results.
- aws_billing_service: Similar to aws_billing.py, but also groups the data by service within each linked account.

