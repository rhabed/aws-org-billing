import boto3
import os
from pprint import pprint
from tabulate import tabulate
from objects.classes import Account, StatusEnum, find_account
from typing import Optional, List
from pydantic import ValidationError
import pandas as pd

AWS_PROFILE = os.getenv("AWS_PROFILE")
ACCOUNT_LIST = list()


def get_org_client(aws_profile_name=AWS_PROFILE):
    session = boto3.Session(profile_name=aws_profile_name)
    client = session.client("organizations")
    return client


def get_ce_client(aws_profile_name=AWS_PROFILE):
    session = boto3.Session(profile_name=aws_profile_name)
    client = session.client("ce")
    return client


def close_account_from_org(boto3_client, account_id):
    user_confirmation = input(
        f"Are you sure closing AWS account {account_id} (yes/No): "
    )
    if user_confirmation == "yes":
        client = boto3_client
        res = client.close_account(AccountId=account_id)
        pprint(res)
    else:
        pprint(f"Aborting closure of account: {account_id}")


def get_list_of_accounts(boto3_client: boto3.client) -> List[Account]:
    """Fetches a paginated list of accounts using boto3, creates Account objects,
    and returns them in a list.

    Args:
        boto3_client: A boto3 client for AWS IAM.

    Returns:
        A list of Account objects representing the retrieved accounts.
    """

    account_list: List[Account] = []
    paginator = boto3_client.get_paginator("list_accounts")

    for page in paginator.paginate():
        accounts = page.get("Accounts", [])
        for account in accounts:
            try:
                account_data = {
                    "account_id": account.get("Id"),
                    "account_name": account.get("Name"),
                    "root_email": account.get("Email"),
                    "status": account.get("Status"),
                }
                account_list.append(Account(**account_data))
            except ValidationError as e:
                print(
                    f"Error creating Account object: {e.errors()}"
                )  # Informative error message

    # Print table only if there are accounts (avoid empty table output)
    if account_list:
        table = [["Account ID", "Root Email", "Account Name", "Account Status"]]
        table.extend(
            [
                [acc.account_id, acc.root_email, acc.account_name, acc.status]
                for acc in account_list
            ]
        )
        # print(tabulate(table, headers="firstrow", tablefmt="fancy_grid"))

    return account_list


def process_billing_results(groups, account_list) -> list:
    """Processes billing results groups and creates table data.

    Args:
        groups: A list of billing results groups.
        account_list: A list of account objects for name lookup.

    Returns:
        A list of lists representing the table data.
    """

    table = []
    for group in groups:
        account_name = accountid = group.get("Keys")[0]
        account = find_account(account_list, "account_id", accountid)
        if account:
            account_name = getattr(account, "account_name")

        service = (
            group.get("Keys", [])[1] if len(group.get("Keys")) > 1 else "Total"
        )  # Handle optional service
        amount = round(
            float(group.get("Metrics").get("UnblendedCost", {}).get("Amount", 0.0)), 2
        )
        unit = group.get("Metrics").get("UnblendedCost", {}).get("Unit", "")
        if amount != 0:
            table.append([account_name, service, amount, unit])
    return table


def aws_billing_service(
    boto3_client: boto3.client,
    start_date: str,
    end_date: str,
    account_list: List,
    granularity: str = "MONTHLY",
) -> None:
    """Fetches AWS billing cost data grouped by linked account and service."""

    response = boto3_client.get_cost_and_usage(
        TimePeriod={"Start": start_date, "End": end_date},
        Granularity=granularity,
        Metrics=["UnblendedCost"],
        GroupBy=[
            {"Type": "DIMENSION", "Key": "LINKED_ACCOUNT"},
            {"Type": "DIMENSION", "Key": "SERVICE"},  # Serice grouping
        ],
        Filter={
            "Not": {
                "Dimensions": {
                    "Key": "RECORD_TYPE",
                    "Values": ["Tax", "Credit", "Refund", "Distributor Discount"],
                }
            },
        },
    )

    table = process_billing_results(
        response.get("ResultsByTime", [])[0].get("Groups", []), account_list
    )

    if table:
        print(tabulate(table, headers="firstrow", tablefmt="fancy_grid"))

    return table


def aws_billing(
    boto3_client: boto3.client,
    start_date: str,
    end_date: str,
    account_list: List,
    granularity: str = "MONTHLY",
) -> None:
    """Fetches AWS billing cost data grouped by linked account and service."""

    response = boto3_client.get_cost_and_usage(
        TimePeriod={"Start": start_date, "End": end_date},
        Granularity=granularity,
        Metrics=["UnblendedCost"],
        GroupBy=[
            {"Type": "DIMENSION", "Key": "LINKED_ACCOUNT"},
        ],
        Filter={
            "Not": {
                "Dimensions": {
                    "Key": "RECORD_TYPE",
                    "Values": ["Tax", "Credit", "Refund", "Distributor Discount"],
                }
            },
        },
    )

    table = process_billing_results(
        response.get("ResultsByTime", [])[0].get("Groups", []), account_list
    )

    if table:
        print(tabulate(table, headers="firstrow", tablefmt="fancy_grid"))

    return table


def tabulate_to_excel(
    data,
    headers="firstrow",
    filename="output_table.xlsx",
    sheet_name="Sheet1",
    index=False,
):
    """
    Exports a tabulate table (with headers in the first row or provided separately) to an Excel file.

    Args:
        data: A list of lists representing the table data, with or without headers in the first row.
        filename: The output Excel file name (default: "output_table.xlsx").
        sheet_name: The name of the worksheet in the Excel file (default: "Sheet1").
        index: Boolean flag to include (True) or exclude (False) the index column (default: False).

    Returns:
        None
    """

    # Create DataFrame using tabulate
    try:
        df = pd.DataFrame(
            data, columns=headers
        )  # tabulate(data, headers=headers, tablefmt="plain"))
    except ValueError as e:
        print("Error:", e)
    # Export DataFrame to Excel
    df.to_excel(filename, sheet_name=sheet_name, index=index)


def main():

    ACCOUNT_LIST = get_list_of_accounts(get_org_client())

    billing_table = aws_billing(
        get_ce_client(), "2024-03-01", "2024-04-01", ACCOUNT_LIST
    )
    # Create DataFrame using tabulate with headers="firstrow"
    tabulate_to_excel(
        data=billing_table,
        headers=["Account Name", "AWS Service", "kloudr Charges", "Currency"],
        filename="excel_output/billing.xlsx",
    )
    billing_table = aws_billing_service(
        get_ce_client(), "2024-03-01", "2024-04-01", ACCOUNT_LIST
    )
    tabulate_to_excel(
        data=billing_table,
        headers=["Account Nane", "AWS Service", "kloudr Charges", "Currency"],
        filename="excel_output/billing_services.xlsx",
    )


if __name__ == "__main__":
    main()
