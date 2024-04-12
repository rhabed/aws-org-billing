import unittest
import os
from unittest.mock import patch

from aws_billing.aws_billing import (
    get_org_client,
    get_ce_client,
    close_account_from_org,
    get_list_of_accounts,
    process_billing_results,
    aws_billing_service,
    aws_billing,
    tabulate_to_excel,
    main,
)
from aws_billing.objects.classes import Account, StatusEnum, find_account
from typing import Optional, List
from pydantic import ValidationError
import pandas as pd


class TestAwsBilling(unittest.TestCase):
    def setUp(self):
        self.AWS_PROFILE = os.getenv("AWS_PROFILE")
        self.ACCOUNT_LIST = list()

    def test_get_org_client(self):
        with patch("boto3.Session") as mock_session:
            get_org_client(self.AWS_PROFILE)
            mock_session.assert_called_once_with(profile_name=self.AWS_PROFILE)

    def test_get_ce_client(self):
        with patch("boto3.Session") as mock_session:
            get_ce_client(self.AWS_PROFILE)
            mock_session.assert_called_once_with(profile_name=self.AWS_PROFILE)

    @patch("builtins.input", return_value="yes")
    def test_close_account_from_org(self, mocked_input):
        # mocked_input.return_value = ['yes']
        with patch("boto3.client") as mock_client:
            close_account_from_org(mock_client, "123456789012")
            mock_client.close_account.assert_called_once_with(AccountId="123456789012")

    def test_get_list_of_accounts(self):
        with patch("boto3.client") as mock_client:
            accounts = get_list_of_accounts(mock_client)
            self.assertIsInstance(accounts, list)
            for account in accounts:
                self.assertIsInstance(account, Account)

    def test_process_billing_results(self):
        groups = [
            {
                "Keys": ["123456789012", "EC2"],
                "Metrics": {
                    "UnblendedCost": {
                        "Amount": "100.00",
                        "Unit": "USD",
                    }
                },
            },
            {
                "Keys": ["123456789012", "S3"],
                "Metrics": {
                    "UnblendedCost": {
                        "Amount": "50.00",
                        "Unit": "USD",
                    }
                },
            },
        ]
        account_list = [
            Account(
                account_id="123456789012",
                account_name="account_name",
                root_email="root@email.com",
                status=StatusEnum.active,
            )
        ]
        table = process_billing_results(groups, account_list)
        self.assertEqual(
            table,
            [
                ["account_name", "EC2", 100.00, "USD"],
                ["account_name", "S3", 50.00, "USD"],
            ],
        )

    def test_aws_billing_service(self):
        with patch("boto3.client") as mock_client:
            aws_billing_service(
                mock_client,
                "2024-03-01",
                "2024-04-01",
                self.ACCOUNT_LIST,
            )
            mock_client.get_cost_and_usage.assert_called_once()

    def test_aws_billing(self):
        with patch("boto3.client") as mock_client:
            aws_billing(
                mock_client,
                "2024-03-01",
                "2024-04-01",
                self.ACCOUNT_LIST,
            )
            mock_client.get_cost_and_usage.assert_called_once()

    def test_tabulate_to_excel(self):
        data = [
            ["Account Name", "AWS Service", "Charges", "Currency"],
            ["account_name", "EC2", 100.00, "USD"],
        ]
        tabulate_to_excel(
            data,
            headers=["Account Name", "AWS Service", "Charges", "Currency"],
            filename="test.xlsx",
            index=False,
        )
        self.assertTrue(os.path.isfile("test.xlsx"))

    def test_main(self):
        with patch(
            "aws_billing.aws_billing.get_org_client"
        ) as mock_get_org_client, patch(
            "aws_billing.aws_billing.get_ce_client"
        ) as mock_get_ce_client, patch(
            "aws_billing.aws_billing.get_list_of_accounts"
        ) as mock_get_list_of_accounts, patch(
            "aws_billing.aws_billing.aws_billing"
        ) as mock_aws_billing, patch(
            "aws_billing.aws_billing.aws_billing_service"
        ) as mock_aws_billing_service, patch(
            "aws_billing.aws_billing.tabulate_to_excel"
        ) as mock_tabulate_to_excel:
            main()
            mock_get_org_client.assert_called_once()
            mock_get_ce_client.call_count == 2
            mock_get_list_of_accounts.assert_called_once()
            mock_aws_billing.assert_called_once()
            mock_aws_billing_service.assert_called_once()
            mock_tabulate_to_excel.assert_called()


if __name__ == "__main__":
    unittest.main()
