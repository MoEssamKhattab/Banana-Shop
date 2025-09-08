from sqlalchemy import Column, Integer, String, Float, JSON, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password = Column(String(100), nullable=False)
    country = Column(String(100), nullable=False)
    gender = Column(String(10), nullable=False)  # male or female
    image = Column(String(200), nullable=True)  # Optional image path
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    additional_data = Column(JSON, nullable=True)  # Additional JSON column
    
class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String(50), unique=True, index=True, nullable=False)  # Product SKU from data.json
    name = Column(String(200), nullable=False)
    price = Column(String(20), nullable=False)  # Keeping as string to match data format
    category = Column(String(100), nullable=False)
    image = Column(String(500), nullable=False)
    description = Column(String(1000), nullable=False)
    sizes = Column(JSON, nullable=False)  # Array of sizes
    colors = Column(JSON, nullable=False)  # Array of colors
    gender = Column(String(10), nullable=False)  # men or women section
    additional_data = Column(JSON, nullable=True)  # Additional JSON column
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
