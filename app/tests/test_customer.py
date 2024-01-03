"""
Defines test cases for the Customer API endpoints.

This module contains test cases for the Customer API endpoints:
- Creating a customer
- Reading a customer
- Updating a customer
It includes fixture setups for database sessions and test customers, along with various test cases.
"""

import uuid
from fastapi import HTTPException
import pytest
from app.database import get_test_db
from app.routers.customer import create_customer, read_customer, patch_customer
from app.models.customer import CustomerModel
from app.models.propertyAddress import PropertyAddressModel
from app.schemas.propertyAddress import CustomerResponse

@pytest.fixture(scope="function")
def setup_db():
    # Set up the database session for the entire test file
    db = get_test_db()
    yield db  # Provide the database session as a fixture
    db.query(CustomerModel).delete()
    db.commit()
    db.close()  # Close the database session after all tests in the file complete


@pytest.fixture(scope="function")
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


@pytest.mark.parametrize("test_input, expected", [
    # Test case: Missing required fields
    ({}, HTTPException(status_code=400, detail="Missing Required Information")),
    # Test case: Invalid email
    ({'first_name': 'test', 'last_name':'customer', 'email': 'invalid_email'}, HTTPException(status_code=400, detail="Please enter correct email - abc@xyz.com")),
    # Test case: Non-unique email
    ({'first_name': 'test', 'last_name':'customer', 'email': 'test@example.com'}, HTTPException(status_code=409, detail="Email already taken")),
    # Test case: electricity_usage_kwh is not number
    ({'first_name': 'test', 'last_name':'customer', 'email': 'electricity@example.com', "electricity_usage_kwh": '12'}, HTTPException(status_code=409, detail="electricity_usage_kwh should be number")),
    # Test case: old_roof is not bool
    ({'first_name': 'test', 'last_name':'customer', 'email': 'old_roof@example.com', "electricity_usage_kwh": 12, "old_roof": 12}
    , HTTPException(status_code=409, detail="old_roof should be boolean")),
    # Test case: Property address provided with incorrect postal code
    ({'first_name': 'test', 'last_name': 'customer', 'email': 'omg@xyz.com', "electricity_usage_kwh": 12, "old_roof": True,
        'property_address': {'street': '112 test road', 'city': 'TestCity', 'state_code': 'AA', 'postal_code': '123456'}}, HTTPException(status_code=400, detail="Invalid Postal Code. It should be a 5-digit number")),
    # Test case: Property address provided
    ({'first_name': 'test', 'last_name': 'customer', 'email': 'omgitworks@xyz.com', "electricity_usage_kwh": 12, "old_roof": True,
        'property_address': {'street': '112 test road', 'city': 'TestCity', 'state_code': 'AA', 'postal_code': '12345'}}, None)
])
def test_create_customer(setup_db, setup_customer, test_input, expected):
    db = setup_db # Access the database session from the setup_db fixture

    # Call the function with the test database and payload
    if expected is None:
        customer_db = create_customer(test_input, db)
        assert isinstance(customer_db, CustomerResponse)
    else:
        with pytest.raises(HTTPException) as e:
            create_customer(test_input, db)
            assert e.value.status_code == expected.status_code
            assert e.value.detail == expected.detail


def test_read_customer(setup_db):
    customer_id = str(uuid.uuid4())
    customer_db = CustomerModel(id=customer_id, first_name='name', last_name='lastname', email='first@last.com')
    setup_db.add(customer_db)
    setup_db.commit()

    # Call the function with the test database and customer ID
    customer = read_customer(customer_id, setup_db)
    assert customer.id == customer_id
    assert customer.first_name == 'name'
    assert customer.last_name == 'lastname'
    assert customer.email == 'first@last.com'

def test_read_customer_not_found(setup_db, setup_customer):
    # Call the function with the test database and a non-existent customer ID
    with pytest.raises(HTTPException) as e:
        read_customer('non_existent_id', setup_db)

    # Assert that the function raised the correct exception
    assert e.value.status_code == 404
    assert e.value.detail == "Customer not found"


@pytest.mark.parametrize("customer_id, customer_email, updated_customer, expected",
    [
        # Test case: Email already taken
        (str(uuid.uuid4()), 'b.b@x.com', {'email': 'test@example.com'}, HTTPException(status_code=409, detail="Email already taken")),
        # Test case: electricity_usage_kwh is not number
        (str(uuid.uuid4()), 'new.mail@check.com', {'electricity_usage_kwh': 'invalid'}, HTTPException(status_code=409, detail="electricity_usage_kwh should be number")),
        # Test case: old_roof is not boolean
        (str(uuid.uuid4()), 'new.mail@check.com', {'old_roof': 'invalid'}, HTTPException(status_code=409, detail="old_roof should be boolean")),
        # Test case: postal_code is not a 5 digit number
        (str(uuid.uuid4()), 'new.mail@check.com', {'property_address': {'postal_code': 'invalid'}}, HTTPException(status_code=400, detail="Invalid Postal Code. It should be a 5-digit number.")),
        # Test case: Customer updated successfully
        (str(uuid.uuid4()), 'new.mail@check.com', {'first_name': 'new_name'}, 'first_name'),
        # Test case: Property Address updated successfully
        (str(uuid.uuid4()), 'new.mail@check.com', { "property_address": { "street": "110 Beacon St", "city": "Boston", "postal_code": "12345", "state_code": "MA" } }, 'new_property_address'),
        # Test case: Partial Property Address updated successfully
        (str(uuid.uuid4()), 'new.mail@check.com', { "property_address": { "state_code": "PA" } }, 'update_property_address')
    ]
)

     
def test_patch_customer(customer_id, customer_email, updated_customer, expected, setup_db, setup_customer):
    # Add a customer to the test database
    customer_db = CustomerModel(id=customer_id, first_name='test', last_name='customer', email=customer_email)
    setup_db.add(customer_db)
    setup_db.commit()

    # Call the function with the test database, customer ID, and updated customer
    if expected == 'first_name':
        customer = patch_customer(customer_id, updated_customer, setup_db)
        assert customer.first_name == updated_customer.get('first_name')

    elif expected == 'new_property_address':
        patch_customer(customer_id, updated_customer, setup_db)
        property_address = setup_db.query(PropertyAddressModel).filter(PropertyAddressModel.customer_id == customer_id).first()

        assert property_address.street == "110 Beacon St"
        assert property_address.city == "Boston"
        assert property_address.postal_code == "12345"
        assert property_address.state_code == "MA"
 
    elif expected == 'update_property_address':
        customer_record = setup_db.query(CustomerModel).filter(CustomerModel.email == customer_email).first()
        property_address_id = str(uuid.uuid4())
        setup_db.add(customer_record)

        property_address_record = PropertyAddressModel(id=property_address_id, customer_id=customer_record.id,street="110 Beacon St", postal_code="Boston", state_code="MA")
        setup_db.add(property_address_record)
        setup_db.commit()

        patch_customer(customer_id, updated_customer, setup_db)
        updated_property_address = setup_db.query(PropertyAddressModel).filter(PropertyAddressModel.customer_id == customer_id).first()

        assert updated_property_address.state_code == 'PA'

    else:
        with pytest.raises(HTTPException) as e:
            patch_customer(customer_id, updated_customer, setup_db)
            assert e.value.status_code == expected.status_code
            assert e.value.detail == expected.detail


def test_patch_customer_not_found(setup_db):
    # Call the function with the test database and a non-existent customer ID
    with pytest.raises(HTTPException) as e:
        patch_customer('abcs', {'first_name': 'new_name'}, setup_db)

    # Assert that the function raised the correct exception
    assert e.value.status_code == 404
    assert e.value.detail == "Customer not found"