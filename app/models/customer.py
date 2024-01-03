from sqlalchemy import Column, String, Integer, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class CustomerModel(Base):
    """
    Represents a customer in the database.

    Attributes:
    - id: Primary key for the CustomerModel - uuid
    - first_name: Customer's first name
    - last_name: Customer's last name
    - email: Customer's email address (unique)
    - electricity_usage_kwh: Customer's electricity usage in kilowatt-hours
    - old_roof: Boolean indicating whether the customer has an old roof
    - property_address_id: Foreign key referencing the property address of the customer
    - property_address: Relationship with PropertyAddressModel
    """
    __tablename__ = "customer"

    id = Column(String(255), primary_key=True, index=True)
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    electricity_usage_kwh = Column(Integer)
    old_roof = Column(Boolean)

    property_address = relationship('PropertyAddressModel', back_populates='customer')

