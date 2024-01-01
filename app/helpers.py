import re
import uuid
from fastapi import HTTPException
from app.models.customer import CustomerModel
from app.models.propertyAddress import PropertyAddressModel
from sqlalchemy.orm import Session



def validate_email(email: str):
     regex = r'^[A-Za-z0-9]+[.-_]*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+$'
     return re.fullmatch(regex, email) is not None

def validate_postal_code(postal_code: str):
    if not (len(postal_code) == 5 and postal_code.isdigit()):
        return False
    return True

def check_if_email_unique(email: str, db: Session):
    if db.query(CustomerModel).filter(CustomerModel.email == email).first():
        return False
    return True

def create_property_address_record(property_address_payload: dict, db:Session):
    validate_postal_code(property_address_payload.get('postal_code'))  # Validate postal code

    property_address_db = PropertyAddressModel(
        id=str(uuid.uuid4()),  # Generate a new UUID as the ID
        **property_address_payload
    )
    db.add(property_address_db)
    db.flush()

    return property_address_db