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
