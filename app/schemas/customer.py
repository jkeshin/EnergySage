from pydantic import BaseModel, Field, EmailStr, Extra
from typing import Optional
from .propertyAddress import PropertyAddress

"""
Defines a Pydantic model representing Customer details.

This module contains the Pydantic Customer model, which defines the structure of customer data:
- ID
- First name
- Last name
- Email
- Optional attributes: electricity usage, old roof status, property address
"""
class Customer(BaseModel):
    class Config:
        orm_mode = True
        extra = Extra.forbid

    id: str
    first_name: str
    last_name: str
    email: str
    electricity_usage_kwh: Optional[int] = None
    old_roof: Optional[bool] = None
    property_address: Optional[PropertyAddress] = None