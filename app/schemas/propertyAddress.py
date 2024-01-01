from pydantic import BaseModel, Field, EmailStr, Extra
from typing import Optional

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
    street: str
    city: str
    postal_code: Optional[str] 
    state_code: Optional[str]