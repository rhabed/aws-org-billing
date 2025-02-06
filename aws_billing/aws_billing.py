import boto3
import os
from pprint import pprint
from tabulate import tabulate
import sys
import datetime
import click

sys.path.insert(0, "./aws_billing/objects")
from classes import Account, find_account
from typing import Optional, List
from pydantic import ValidationError
import pandas as pd

AWS_PROFILE = os.getenv("AWS_PROFILE")
ACCOUNT_LIST = list()
TODAY = datetime.date.today()
FIRST = TODAY.replace(day=1)
LAST_MONTH = FIRST - datetime.timedelta(days=1)


def get_org_client(aws_profile_name=AWS_PROFILE):
    session = boto3.Session(profile_name=aws_profile_name)
    client = session.client("organizations")
    return client


def get_ce_client(aws_profile_name=AWS_PROFILE):
    session = boto3.Session(profile_name=aws_profile_name)
    client = session.client("ce")
    return client


def close_account_from_org(boto3_client, account_id):
    user_confirmation = input(f"Are you sure closing AWS account {account_id} (yes/No): ")
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
                print(f"Error creating Account object: {e.errors()}")  # Informative error message

    # Print table only if there are accounts (avoid empty table output)
    if account_list:
        table = [["Account ID", "Root Email", "Account Name", "Account Status"]]
        table.extend(
            [[acc.account_id, acc.root_email, acc.account_name, acc.status] for acc in account_list]
        )
        print(tabulate(table, headers="firstrow", tablefmt="fancy_grid"))

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
        name = accountid = group.get("Keys")[0]
        account = find_account(account_list, "account_id", accountid)
        if account:
            name = getattr(account, "account_name")
        if name.startswith("Name$"):
            name = name[5:]

        service = (
            group.get("Keys", [])[1] if len(group.get("Keys")) > 1 else "Total"
        )  # Handle optional service
        amount = round(float(group.get("Metrics").get("UnblendedCost", {}).get("Amount", 0.0)), 3)
        unit = group.get("Metrics").get("UnblendedCost", {}).get("Unit", "")
        if amount != 0 and ("AWS-Out-Bytes" not in service and "DataTransfer" not in service):
            table.append([name, service, amount, unit])
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


def get_cost_allocation_tags(
    boto3_client: boto3.client,
    start_date: str,  # format: yyyy-mm-dd
    end_date: str,
    tag_key: str,
    account_id: str,
):
    response = boto3_client.get_tags(
        TimePeriod={"Start": start_date, "End": end_date},
        TagKey=tag_key,
        Filter={
            "Dimensions": {
                "Key": "LINKED_ACCOUNT",
                "Values": [account_id],
            }
        },
    )
    return response.get("Tags", [])


def aws_billing_tags(
    boto3_client: boto3.client,
    start_date: str,
    end_date: str,
    account_list: List,
    account_id: str,
    tag_key: str,
    tagValue: List,
    granularity: str = "MONTHLY",
):
    """Fetches AWS billing cost data grouped by Tag and service."""

    # still cannot read the correct services

    response = boto3_client.get_cost_and_usage(
        TimePeriod={"Start": start_date, "End": end_date},
        Granularity=granularity,
        Metrics=["UnblendedCost"],
        GroupBy=[
            {"Type": "TAG", "Key": tag_key},
            {"Type": "DIMENSION", "Key": "SERVICE"},  # Service grouping
        ],
        Filter={
            "And": [
                {
                    "Not": {
                        "Dimensions": {
                            "Key": "RECORD_TYPE",
                            "Values": [
                                "Tax",
                                "Credit",
                                "Refund",
                                "Distributor Discount",
                            ],
                        }
                    }
                },
                {
                    "Tags": {
                        "Key": tag_key,
                        "Values": tagValue,
                    },
                },
                {
                    "Dimensions": {
                        "Key": "LINKED_ACCOUNT",
                        "Values": [account_id],
                    },
                },
            ]
        },
    )
    table = process_billing_results(
        response.get("ResultsByTime", [])[0].get("Groups", []), account_list
    )

    if table:
        print(tabulate(table, headers="firstrow", tablefmt="fancy_grid"))

    return table


def aws_billing_tags2(
    boto3_client: boto3.client,
    start_date: str,
    end_date: str,
    account_list: List,
    account_id: str,
    tag_key: str,
    tagValue: List,
    granularity: str = "MONTHLY",
):
    """Fetches AWS billing cost data grouped by Tag and service."""

    # still cannot read the correct services

    response = boto3_client.get_cost_and_usage(
        TimePeriod={"Start": start_date, "End": end_date},
        Granularity=granularity,
        Metrics=["UnblendedCost"],
        GroupBy=[
            {"Type": "TAG", "Key": tag_key},
            # {"Type": "DIMENSION", "Key": "SERVICE"},
            {"Type": "DIMENSION", "Key": "USAGE_TYPE"},
        ],
        Filter={
            "And": [
                {
                    "Not": {
                        "Dimensions": {
                            "Key": "RECORD_TYPE",
                            "Values": [
                                "Tax",
                                "Credit",
                                "Refund",
                                "Distributor Discount",
                            ],
                        }
                    }
                },
                {
                    "Dimensions": {
                        "Key": "SERVICE",
                        "Values": ["EC2 - Other", "Amazon Elastic Compute Cloud - Compute"],
                    },
                },
                {
                    "Tags": {
                        "Key": tag_key,
                        "Values": tagValue,
                    },
                },
                {
                    "Dimensions": {
                        "Key": "LINKED_ACCOUNT",
                        "Values": [account_id],
                    },
                },
            ]
        },
    )
    print(response)
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


@click.command()
@click.option(
    "--str_date",
    is_flag=False,
    default=LAST_MONTH.strftime(f"%Y-%m-01"),
    help="Reports Start Date",
)
@click.option("--end_date", is_flag=False, default=FIRST, help="Reports End Date")
@click.option(
    "--tag_billing_required",
    is_flag=False,
    default="False",
    help="Is Tag Billing Required? (True|False)",
)
@click.option("--account_name", is_flag=False, default="", help="Account Name for Tag Billing")
@click.option("--tag_key", is_flag=False, default="Name", help="Tag Key")
def main(str_date, end_date, tag_billing_required, account_name, tag_key):
    ACCOUNT_LIST = get_list_of_accounts(get_org_client())

    if tag_billing_required in ("True", "true"):
        account = find_account(ACCOUNT_LIST, "account_name", account_name)
        account_name = "".join(account_name).replace(" ", "_").lower()
        account_id = None
        if account:
            account_id = account.account_id
            print(f"account_id: {account_id}")
        if account_id:
            tags = get_cost_allocation_tags(
                get_ce_client(), str_date, end_date, tag_key, account_id
            )
            billing_table = aws_billing_tags2(
                get_ce_client(), str_date, end_date, ACCOUNT_LIST, account_id, tag_key, tags
            )
            tabulate_to_excel(
                data=billing_table,
                headers=["Tag", "Usage Type", "Charges", "Currency"],
                filename=f"excel_output/{end_date}_{account_name}_billing_tags_by_{tag_key}.xlsx",
            )
        else:
            print(f"No account_id found for specified account {account_name}")
    if tag_billing_required in ("false", "False"):
        aws_billing(get_ce_client(), str_date, end_date, ACCOUNT_LIST)
        billing_table = aws_billing_service(get_ce_client(), str_date, end_date, ACCOUNT_LIST)

        tabulate_to_excel(
            data=billing_table,
            headers=["Account Name", "AWS Service", "Charges", "Currency"],
            filename=f"excel_output/{end_date}_billing_services.xlsx",
        )


if __name__ == "__main__":
    main()
    # get_list_of_accounts(get_org_client())
