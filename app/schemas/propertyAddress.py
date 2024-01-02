from pydantic import BaseModel, Field, EmailStr, Extra
from typing import Optional
from .customer import Customer

"""
Defines a Pydantic model representing a property address.

This module contains the Pydantic PropertyAddress model, which defines the structure of property address data:
- ID (automatically generated)
- Street
- City
- Optional attributes: Postal code, State code
"""
class PropertyAddress(BaseModel):
    class Config:
        orm_mode = True
        exclude = {"_id", "customer_id"}

    _id: Optional[str] = Field(None, description="Automatically generated ID")
    customer_id: Optional[str] = None
    street: str
    city: str
    postal_code: Optional[str] 
    state_code: Optional[str]
    
class CustomerResponse(BaseModel):
    id: str
    first_name: str
    last_name: str
    email: str
    electricity_usage_kwh: Optional[int]
    old_roof: Optional[bool]
    property_address: Optional[PropertyAddress]