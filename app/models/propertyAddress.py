from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from app.database import Base

class PropertyAddressModel(Base):
    """Defines the SQLAlchemy model for Property Addresses.

    This module contains the SQLAlchemy model definition for the PropertyAddressModel.
    It defines a table 'property_addresses' to store property address information.

    Attributes:
    id (str): The primary key representing the property address ID.
    street (str): Represents the street address.
    city (str): Represents the city of the property address.
    postal_code (str): Represents the postal code of the property address.
    state_code (str): Represents the state code of the property address (maximum length of 5 characters).
    """
    __tablename__ = "property_address"

    id = Column(String(36), primary_key=True, index=True)
    customer_id = Column(String(36), ForeignKey('customer.id'))
    street = Column(String(255))
    city = Column(String(255))
    postal_code = Column(String(255))
    state_code = Column(String(255))

    # Relationship with CustomerModel
    customer = relationship("CustomerModel", back_populates='property_address')