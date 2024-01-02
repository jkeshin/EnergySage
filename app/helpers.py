import re
import uuid
from fastapi import HTTPException
from app.models.customer import CustomerModel
from app.models.propertyAddress import PropertyAddressModel
from sqlalchemy.orm import Session
from app.schemas.propertyAddress import CustomerResponse, PropertyAddress



def validate_email(email: str) -> bool:
     """
     Validate an email address using a regular expression.

    Parameters:
    - email (str): The email address to be validated.

    Returns:
    - bool: True if the email address is valid, False otherwise.

    The function uses a regular expression to check if the provided email address
    adheres to a common pattern for valid email formats
    """
     regex = r'^[A-Za-z0-9]+[.-_]*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+$'
     return re.fullmatch(regex, email) is not None

def validate_postal_code(postal_code: str):
    if not (len(postal_code) == 5 and postal_code.isdigit()):
        return False
    return True

def check_if_email_unique(email: str, db: Session) -> bool:
    """
    Validate a postal code.

    Parameters:
    - postal_code (str): The postal code to be validated.

    Returns:
    - bool: True if the postal code is valid, False otherwise.

    The function checks whether the provided postal code adheres to the following criteria:
    - Consists of exactly five characters.
    - All characters are digits.
    """
    if db.query(CustomerModel).filter(CustomerModel.email == email).first():
        return False
    return True

def create_property_address_record(property_address_payload: dict, customer_id: str, db:Session) -> PropertyAddressModel:
    """
    Create a new property address record in the database.

    Parameters:
    - property_address_payload (dict): A dictionary containing the property address details.
    - customer_id (str): The ID of the customer associated with the property address.
    - db (Session): The database session.

    Returns:
    - PropertyAddressModel: The created PropertyAddressModel instance.

    Raises:
    - HTTPException: If the postal code in the property address payload is invalid.

    The function validates the postal code in the property address payload using the
    validate_postal_code function. If the postal code is invalid, it raises an HTTPException
    with a 400 status code and a corresponding detail message.

    If the postal code is valid, a new PropertyAddressModel instance is created with a new UUID
    as the ID, and the provided customer_id and property_address_payload details. The instance is
    then added to the database session, and the changes are flushed to ensure the ID is populated.
    """
    if not validate_postal_code(property_address_payload.get("postal_code")):
        raise HTTPException(status_code=400, detail="Invalid Postal Code. It should be a 5-digit number.")
    
    
    property_address_db = PropertyAddressModel(
        id=str(uuid.uuid4()),  # Generate a new UUID as the ID,
        customer_id = customer_id,
        **property_address_payload
    )
    db.add(property_address_db)
    db.flush()

    return property_address_db

def get_customer_and_property_address(customer_id: str, db: Session) -> CustomerResponse:
    """
    Retrieve a customer and their associated property address from the database.

    Parameters:
    - customer_id (str): The ID of the customer.
    - db (Session): The database session.

    Returns:
    - Union[CustomerResponse, None]: A CustomerResponse object if the customer is found,
      None if the customer is not found.

    The function queries the database for a customer with the specified customer_id.
    If the customer is found, it further queries for the associated property address.
    If a property address is found, a CustomerResponse object is created with the customer's
    details and the property address details. If no property address is found, the property_address
    field in CustomerResponse is set to None.

    If the customer is not found in the database, the function returns None.
    """
    
    customer = db.query(CustomerModel).filter(CustomerModel.id == customer_id).first()
    if customer:
        property_address = db.query(PropertyAddressModel).filter(
            PropertyAddressModel.customer_id == customer.id
        ).first()

        return CustomerResponse(
            id=customer.id,
            first_name=customer.first_name,
            last_name=customer.last_name,
            email=customer.email,
            electricity_usage_kwh=customer.electricity_usage_kwh,
            old_roof=customer.old_roof,
            property_address=PropertyAddress(
                customer_id=None,
                street=property_address.street,
                city=property_address.city,
                postal_code=property_address.postal_code,
                state_code=property_address.state_code
            ) if property_address else None
        )
    return None