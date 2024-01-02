"""
Defines test cases for database operations and helper functions.

This module contains test cases for various helper functions and database operations:
- Validating email addresses
- Validating postal codes
- Checking email uniqueness
- Creating property address records
It includes fixtures for setting up a database session and a test customer, along with parametrized tests for validation and checking email uniqueness.
"""

import uuid
import pytest
from app.database import get_test_db
from app.helpers import validate_email, validate_postal_code, check_if_email_unique, create_property_address_record
from app.models.customer import CustomerModel


@pytest.fixture(scope="module")
def setup_db():
    # Set up the database session for the entire test file
    db = get_test_db()
    yield db  # Provide the database session as a fixture
    db.close()  # Close the database session after all tests in the file complete


@pytest.fixture(scope="module")
def setup_customer(setup_db):
    # Set up a test customer for the entire test file
    db = setup_db  # Access the database session from the setup_db fixture

    # Create a CustomerModel with the test email
    customer = CustomerModel(id=str(uuid.uuid4()), email="test@example.com", first_name='test', last_name='customer')
    db.add(customer)
    db.commit()

    yield customer  # Provide the created customer as a fixture

    # Clean up: Delete the added customer after all tests in the file complete
    try:
        db.delete(customer)
        db.commit()
    except Exception as e:
        # Handle exceptions during cleanup (log/print the exception)
        print(f"Error during cleanup: {e}")
        db.rollback()  # Rollback changes to maintain the database state


@pytest.mark.parametrize("test_input,expected", [
    ("test@example.com", True),
    ("invalid_email", False),
])
def test_validate_email(test_input, expected):
    assert validate_email(test_input) == expected


@pytest.mark.parametrize("test_input,expected", [
    ("12345", True),
    ("1234", False),
    ("123456", False),
    ("1234a", False),
])
def test_validate_postal_code(test_input, expected):
    assert validate_postal_code(test_input) == expected


@pytest.mark.parametrize("test_input,expected", [
    ("test@example.com", False),
    ("unique@xyz.com", True),
])
def test_check_if_email_unique(setup_db, setup_customer, test_input, expected):
    db = setup_db
    # Assert that the function returned the expected result
    assert check_if_email_unique(test_input, db) == expected


def test_create_property_address_record(setup_db, setup_customer):
    db = setup_db # Access the database session from the setup_db fixture

    # Create a test property_address_payload
    property_address_payload = {
        "street": "hola 1178 bored",
        "city": "Boston",
        "state_code": "MA",
        "postal_code": "05678"
    }

    # Call the function with the test database and payload
    property_address_db = create_property_address_record(property_address_payload, str(uuid.uuid4()), db)

    # Assert that the returned PropertyAddressModel has the expected attributes
    assert property_address_db.postal_code == property_address_payload['postal_code']
    assert property_address_db.city == property_address_payload['city']