from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from datetime import datetime

class UserSignup(BaseModel):
    name: str
    email: EmailStr
    password: str
    country: str
    gender: str
    image: Optional[str] = None
    
    @validator('gender')
    def validate_gender(cls, v):
        if v.lower() not in ['male', 'female']:
            raise ValueError('Gender must be either male or female')
        return v.lower()
    
    @validator('name')
    def validate_name(cls, v):
        if len(v.strip()) < 2:
            raise ValueError('Name must be at least 2 characters long')
        return v.strip()

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    country: str
    gender: str
    image: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class ProductResponse(BaseModel):
    id: int
    sku: str
    name: str
    price: str
    category: str
    image: str
    description: str
    sizes: List[str]
    colors: List[str]
    gender: str
    
    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: Optional[UserResponse] = None

class PasswordStrengthResponse(BaseModel):
    score: int
    strength: str
    feedback: List[str]
    is_strong: bool
