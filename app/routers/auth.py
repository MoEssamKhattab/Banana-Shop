from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas import UserSignup, UserLogin, UserResponse, TokenResponse, PasswordStrengthResponse
from app.utils.auth import hash_password, verify_password, create_access_token, check_password_strength
from app.utils.countries import COUNTRIES
from datetime import timedelta
import os
import uuid
from typing import Optional

router = APIRouter(prefix="/api/auth", tags=["authentication"])

@router.post("/signup", response_model=TokenResponse)
async def signup(
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    country: str = Form(...),
    gender: str = Form(...),
    profile_image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """Register a new user and return access token"""
    
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Validate country
    if country not in COUNTRIES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid country"
        )
    
    # Validate gender
    if gender.lower() not in ['male', 'female']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Gender must be either male or female"
        )
    
    # Validate name
    if len(name.strip()) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Name must be at least 2 characters long"
        )
    
    # Check password strength
    password_check = check_password_strength(password)
    if not password_check["is_strong"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Password is not strong enough: {', '.join(password_check['feedback'])}"
        )
    
    # Handle profile image upload
    image_path = None
    if profile_image and profile_image.content_type and profile_image.content_type.startswith('image/'):
        # Create uploads directory if it doesn't exist
        upload_dir = "static/uploads/profile_images"
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generate unique filename
        file_extension = profile_image.filename.split('.')[-1] if '.' in profile_image.filename else 'jpg'
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = os.path.join(upload_dir, unique_filename)
        
        # Save the file
        try:
            with open(file_path, "wb") as buffer:
                content = await profile_image.read()
                buffer.write(content)
            image_path = f"/static/uploads/profile_images/{unique_filename}"
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save profile image"
            )
    
    # Hash password
    hashed_password = hash_password(password)
    
    # Create new user
    new_user = User(
        name=name.strip(),
        email=email,
        password=hashed_password,
        country=country,
        gender=gender.lower(),
        image=image_path
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create access token for auto-login
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": new_user.email, "user_id": new_user.id},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": new_user.id,
            "name": new_user.name,
            "email": new_user.email,
            "country": new_user.country,
            "gender": new_user.gender,
            "image": new_user.image,
            "created_at": new_user.created_at
        }
    }

@router.post("/login", response_model=TokenResponse)
async def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """Login user and return access token"""
    
    # Find user by email
    user = db.query(User).filter(User.email == user_credentials.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Verify password
    if not verify_password(user_credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.email, "user_id": user.id},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "country": user.country,
            "gender": user.gender,
            "image": user.image,
            "created_at": user.created_at
        }
    }

@router.post("/check-password", response_model=PasswordStrengthResponse)
async def check_password_endpoint(password: str = Form(...)):
    """Check password strength"""
    return check_password_strength(password)

@router.get("/countries")
async def get_countries():
    """Get list of all countries"""
    return {"countries": COUNTRIES}
