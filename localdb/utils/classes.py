from pydantic import BaseModel, validator
import datetime

class BillingItem(BaseModel):
    aws_account_id: str
    aws_service: str
    cost: float
    start_date: str
    end_date: str

    @validator('start_date', 'end_date', always=True)
    def validate_dates(cls, value, values):
        start_date = datetime.datetime.strptime(values['start_date'], "%Y-%m-%d")
        end_date = datetime.datetime.strptime(values['end_date'], "%Y-%m-%d")

        if start_date >= end_date:
            raise ValueError("Start date must be before end date")

        return value