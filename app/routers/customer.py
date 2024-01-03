from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.schemas.customer import Customer
from app.schemas.propertyAddress import PropertyAddress, CustomerResponse
from app.database import get_db
from app.models.customer import CustomerModel
from app.models.propertyAddress import PropertyAddressModel
from app.helpers import check_if_email_unique, create_property_address_record, validate_email, validate_postal_code, get_customer_and_property_address
from typing import List

import uuid, re

router = APIRouter()

"""
Defines API endpoints related to customer operations.

This module contains FastAPI router definitions for handling customer-related operations:
- Creating a customer
- Reading a single customer by ID
- Reading all customers
- Updating a customer

It utilizes SQLAlchemy models and helper functions for database interactions.
"""

ELECTRICITY_USAGE_KWH = "electricity_usage_kwh"
OLD_ROOF = "old_roof"
PROPERTY_ADDRESS = "property_address"
EMAIL = 'email'
CUSTOMER_REQUIRED_FIELDS = ['first_name', 'last_name', 'email']
POSTAL_CODE = 'postal_code'
ID = "id"

@router.post("/customer/", response_model=CustomerResponse)
def create_customer(customer_payload: dict, db: Session = Depends(get_db)):
    """
    Endpoint to create a new customer with optional property address.

    Args:
    - customer_payload (dict): Payload containing customer details.
    - db (Session): SQLAlchemy database session.

    Returns:
    - CustomerResponse: Created customer and property address details.
    """

    if not set(CUSTOMER_REQUIRED_FIELDS).issubset(customer_payload.keys()):
        raise HTTPException(status_code=400, detail="Missing Required Information")
    
    if not validate_email(customer_payload.get(EMAIL)):
        raise HTTPException(status_code=400, detail="Please enter correct email - abc@xyz.com")

    if not check_if_email_unique(customer_payload.get("email"), db):
        raise HTTPException(status_code=409, detail="Email already taken")

    if ELECTRICITY_USAGE_KWH in customer_payload.keys() and not isinstance(customer_payload.get("electricity_usage_kwh"), int):
        raise HTTPException(status_code=400, detail="electricity_usage_kwh should be number")

    if OLD_ROOF in customer_payload.keys() and not isinstance(customer_payload.get("old_roof"), bool):
        raise HTTPException(status_code=400, detail="old_roof should be boolean")

    # Create customer with the property address ID
    customer_db = CustomerModel(
        id=str(uuid.uuid4()),  # Generate a new UUID as the ID
        first_name=customer_payload.get("first_name"),
        last_name=customer_payload.get("last_name"),
        email=customer_payload.get("email"),
        electricity_usage_kwh=customer_payload.get("electricity_usage_kwh"),
        old_roof=customer_payload.get("old_roof"),
    )
    db.add(customer_db)
    db.flush()

    # Create property address with a new ID
    property_address_payload = customer_payload.get("property_address")
    
    if property_address_payload is not None:
        property_address_db = create_property_address_record(property_address_payload, customer_db.id, db)

    db.commit()
    db.flush()

    return get_customer_and_property_address(customer_db.id, db)

@router.get("/customer/{customer_id}", response_model=CustomerResponse)
def read_customer(customer_id: str, db: Session = Depends(get_db)):
    """
    Endpoint to read a customer by their ID.

    Args:
    - customer_id (str): ID of the customer to retrieve.
    - db (Session): SQLAlchemy database session.

    Returns:
    - CustomerResponse: Retrieved customer and property address details.
    """
    data = get_customer_and_property_address(customer_id, db)
    if data:
        return data
    raise HTTPException(status_code=404, detail="Customer not found")    


@router.get("/customers", response_model=List[Customer])
def read_customers(db: Session = Depends(get_db)):
    """
    Endpoint to read all customers.

    Args:
    - db (Session): SQLAlchemy database session.

    Returns:
    - List[Customer]: List of all customers.
    """
    
    customers_db = db.query(CustomerModel).all()
    return customers_db


@router.patch("/customer/{customer_id}", response_model=CustomerResponse)
def patch_customer(customer_id: str, updated_customer: dict, db: Session = Depends(get_db)):
    """
    Endpoint to partially update a customer's details.

    Args:
    - customer_id (str): ID of the customer to update.
    - updated_customer (dict): Payload containing updated customer details.
    - db (Session): SQLAlchemy database session.

    Returns:
    - CustomerResponse: Retrieved customer and property address details.
    """

    customer_db = db.query(CustomerModel).filter(CustomerModel.id == customer_id).first()
    # remove id if present in payload
    updated_customer.pop(ID)
    
    if customer_db is None:
        raise HTTPException(status_code=404, detail="Customer not found")

    if EMAIL in updated_customer.keys() and not check_if_email_unique(updated_customer.get("email"), db):
        raise HTTPException(status_code=409, detail="Email already taken")
    
    if ELECTRICITY_USAGE_KWH in updated_customer.keys() and not isinstance(updated_customer.get("electricity_usage_kwh"), int):
        raise HTTPException(status_code=400, detail="electricity_usage_kwh should be number")

    if OLD_ROOF in updated_customer.keys() and not isinstance(updated_customer.get("old_roof"), bool):
        raise HTTPException(status_code=400, detail="old_roof should be boolean")
    
    if PROPERTY_ADDRESS in updated_customer.keys():
        property_address_payload = updated_customer.get("property_address")

        if POSTAL_CODE in property_address_payload.keys() and not validate_postal_code(property_address_payload.get("postal_code")):
            raise HTTPException(status_code=400, detail="Invalid Postal Code. It should be a 5-digit number.")
        
    # Update customer data if the field is present in the request payload
    for field, value in updated_customer.items():
        if "property_address" not in field and hasattr(customer_db, field):
            setattr(customer_db, field, value)

    # Update property address data if the field is present in the request payload
    if "property_address" in updated_customer:
        property_address_db = db.query(PropertyAddressModel).filter(
            PropertyAddressModel.customer_id == customer_db.id).first()
        
        if property_address_db is None:
            property_address_db = create_property_address_record(updated_customer.get("property_address"), customer_db.id, db)

        else:
            for field, value in updated_customer.get("property_address").items():
                if hasattr(property_address_db, field):
                    setattr(property_address_db, field, value)

    db.commit()
    db.refresh(customer_db)

    return get_customer_and_property_address(customer_db.id, db)
