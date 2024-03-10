from typing import Tuple
from pydantic import BaseModel, EmailStr
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


def find_account(account_list, attribute, value):
    for account in account_list:
        if getattr(account, attribute) == value:
            return account
    return None
