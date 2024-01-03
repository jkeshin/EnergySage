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
        exclude = {"_id"}

    _id: Optional[str] = Field(None, description="Automatically generated ID")
    _customer_id: Optional[str] = None
    street: Optional[str]
    city: Optional[str]
    postal_code: Optional[str] 
    state_code: Optional[str]
    
class CustomerResponse(BaseModel):
    """
    Defines a Pydantic model representing a CustomerResponse address.

    This module contains the Pydantic CustomerResponse model, which defines the structure of property address data:
    - id 
    - first_name 
    - last_name 
    - email 
    - electricity_usage_kwh 
    - old_roof 
    - property_address 
    """
    id: str
    first_name: str
    last_name: str
    email: str
    electricity_usage_kwh: Optional[int]
    old_roof: Optional[bool]
    property_address: Optional[PropertyAddress]