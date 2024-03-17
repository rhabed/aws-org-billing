import boto3
import os
from pprint import pprint
from tabulate import tabulate
from objects.classes import Account, StatusEnum, find_account
from typing import Optional, List
from pydantic import ValidationError

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


# Billing
def aws_billing_service(
    boto3_client: boto3.client,
    start_date: str,
    end_date: str,
    account_list: List,
    granularity: str = "MONTHLY",
) -> None:
    """Fetches AWS billing cost data for the specified period and granularity,
    groups by linked account and service, and prints a table summarizing the results.

    Args:
        boto3_client: A boto3 client for AWS Cost Management Service.
        start_date: The start date of the billing period in YYYY-MM-DD format.
        end_date: The end date of the billing period in YYYY-MM-DD format.
        granularity: The granularity of the data (default: "MONTHLY"). Options include
            "DAILY", "HOURLY", or "MONTHLY".
    """

    response = boto3_client.get_cost_and_usage(
        TimePeriod={"Start": start_date, "End": end_date},
        Granularity=granularity,
        Metrics=["UnblendedCost"],
        GroupBy=[
            {"Type": "DIMENSION", "Key": "LINKED_ACCOUNT"},
            {"Type": "DIMENSION", "Key": "SERVICE"},
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

    # Process results and create table data
    table = [["AccountId", "Service", "Amount", "Unit"]]
    for group in response.get("ResultsByTime", [])[0].get("Groups", []):
        account_name = accountid = group.get("Keys")[0]
        account = find_account(account_list, "account_id", accountid)
        if account:
            account_name = getattr(account, "account_name")
        service = group.get("Keys")[1]
        amount = round(
            float(group.get("Metrics").get("UnblendedCost", {}).get("Amount", 0.0)), 2
        )
        unit = group.get("Metrics").get("UnblendedCost", {}).get("Unit", "")
        table.append([account_name, service, amount, unit])

    # Print table only if there's data (avoid empty table output)
    if table:
        print(tabulate(table, headers="firstrow", tablefmt="fancy_grid"))


def aws_billing(
    boto3_client: boto3.client,
    start_date: str,
    end_date: str,
    account_list: List,
    granularity: str = "MONTHLY",
) -> None:
    """Fetches AWS billing cost data for the specified period and granularity,
    groups by linked account, and prints a table summarizing the results.

    Args:
        boto3_client: A boto3 client for AWS Cost Management Service.
        start_date: The start date of the billing period in YYYY-MM-DD format.
        end_date: The end date of the billing period in YYYY-MM-DD format.
        granularity: The granularity of the data (default: "MONTHLY"). Options include
            "DAILY", "HOURLY", or "MONTHLY".
    """

    response = boto3_client.get_cost_and_usage(
        TimePeriod={"Start": start_date, "End": end_date},
        Granularity=granularity,
        Metrics=["UnblendedCost"],
        GroupBy=[{"Type": "DIMENSION", "Key": "LINKED_ACCOUNT"}],
        Filter={
            "Not": {
                "Dimensions": {
                    "Key": "RECORD_TYPE",
                    "Values": ["Tax", "Credit", "Refund", "Distributor Discount"],
                }
            },
        },
    )

    # Process results and create table data
    table = [["AccountId", "Amount", "Unit"]]
    for group in response.get("ResultsByTime", [])[0].get("Groups", []):
        account_name = accountid = group.get("Keys")[0]
        account = find_account(account_list, "account_id", accountid)
        if account:
            account_name = getattr(account, "account_name")

        amount = round(
            float(group.get("Metrics").get("UnblendedCost", {}).get("Amount", 0.0)), 2
        )
        unit = group.get("Metrics").get("UnblendedCost", {}).get("Unit", "")
        table.append([account_name, amount, unit])

    # Print table only if there's data (avoid empty table output)
    if table:
        print(tabulate(table, headers="firstrow", tablefmt="fancy_grid"))


def main():
    ACCOUNT_LIST = get_list_of_accounts(get_org_client())

    aws_billing(get_ce_client(), "2024-02-01", "2024-03-01", ACCOUNT_LIST)
    aws_billing_service(get_ce_client(), "2024-02-01", "2024-03-01", ACCOUNT_LIST)


if __name__ == "__main__":
    main()
