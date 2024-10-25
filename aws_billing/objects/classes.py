from typing import Tuple, Optional
from pydantic import BaseModel, EmailStr, validator
import decimal
from enum import Enum


class StatusEnum(Enum):
    active = "ACTIVE"
    suspended = "SUSPENDED"
    pending_closure = "PENDING_CLOSURE"


class Account(BaseModel):
    account_id: str
    account_name: str
    root_email: EmailStr
    status: StatusEnum


class BillingItem(BaseModel):
    aws_account_name: str
    aws_service: Optional[str] = None
    cost: Optional[decimal.Decimal] = 0
    start_date: Optional[str] = None
    end_date: Optional[str] = None


def find_account(account_list, attribute, value):
    """
    Finds an Account object in account_list by comparing the object's attribute to value.

    Args:
        account_list: A list of Account objects.
        attribute: The name of the attribute to search for.
        value: The value to search for.

    Returns:
        The first matching Account object, or None if no match was found.
    """
    for account in account_list:
        if getattr(account, attribute) == value:
            return account
    return None
