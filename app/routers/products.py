from fastapi import APIRouter, Depends, HTTPException, Query, Body, BackgroundTasks
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Product, User
from app.schemas import ProductResponse
from app.utils.auth import get_current_user_optional
from typing import List, Optional, Dict, Any

router = APIRouter(prefix="/api/products", tags=["products"])

@router.get("/", response_model=List[ProductResponse])
async def get_products(
    gender: Optional[str] = Query(None, description="Filter by gender (men/women)"),
    category: Optional[str] = Query(None, description="Filter by category"),
    db: Session = Depends(get_db)
):
    """Get all products with optional filters"""
    query = db.query(Product).filter(Product.is_active == True)
    
    if gender:
        query = query.filter(Product.gender == gender.lower())
    
    if category:
        query = query.filter(Product.category.ilike(f"%{category}%"))
    
    products = query.all()
    return products

@router.get("/men", response_model=List[ProductResponse])
async def get_men_products(db: Session = Depends(get_db)):
    """Get all men's products"""
    products = db.query(Product).filter(
        Product.gender == "men",
        Product.is_active == True
    ).all()
    return products

@router.get("/women", response_model=List[ProductResponse])
async def get_women_products(db: Session = Depends(get_db)):
    """Get all women's products"""
    products = db.query(Product).filter(
        Product.gender == "women",
        Product.is_active == True
    ).all()
    return products

###############

@router.get("/{product_id}/personalized-image")
async def get_personalized_image(
    product_id: int, 
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Check if a personalized image exists for the current user and product"""
    
    # Verify product exists
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # If no user is logged in, return original image info
    if not current_user:
        return {
            "has_personalized_image": False,
            "personalized_image_url": None,
            "is_generating": False,
            "original_image_url": product.image,
            "authentication_required": True
        }
    
    # Check if user has profile image for personalization
    if not current_user.image:
        return {
            "has_personalized_image": False,
            "personalized_image_url": None,
            "is_generating": False,
            "original_image_url": product.image,
            "profile_image_required": True
        }
    
    # Check for cached personalized image
    try:
        from app.utils.image_cache import image_cache
        cached_url = image_cache.get_cached_image_url(current_user.id, product_id)
        
        if cached_url:
            return {
                "has_personalized_image": True,
                "personalized_image_url": cached_url,
                "is_generating": False,
                "original_image_url": product.image,
                "ready_for_personalization": True
            }
    except Exception as e:
        print(f"Cache check error: {e}")
    
    # No cached image found
    return {
        "has_personalized_image": False,
        "personalized_image_url": None,
        "is_generating": False,
        "original_image_url": product.image,
        "ready_for_personalization": True
    }

@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int, 
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Get a specific product by ID"""
    
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.is_active == True
    ).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return product

@router.get("/sku/{sku}", response_model=ProductResponse)
async def get_product_by_sku(sku: str, db: Session = Depends(get_db)):
    """Get a specific product by SKU"""
    product = db.query(Product).filter(
        Product.sku == sku,
        Product.is_active == True
    ).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return product

@router.post("/{product_id}/generate-personalized-image")
async def generate_personalized_image(
    product_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Trigger generation of a personalized image for the current user and product"""
    
    # Verify product exists first
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # If user not logged in, skip generation gracefully
    if not current_user:
        return {
            "status": "skipped",
            "message": "User not logged in - personalized image generation skipped",
            "original_image_url": product.image
        }
    
    # Check if user has profile image
    if not current_user.image:
        return {
            "status": "skipped", 
            "message": "Profile image required for personalization",
            "original_image_url": product.image
        }
    
    # Check if already cached
    try:
        from app.utils.image_cache import image_cache
        cached_url = image_cache.get_cached_image_url(current_user.id, product_id)
        
        if cached_url:
            return {
                "status": "already_exists",
                "personalized_image_url": cached_url,
                "message": "Personalized image already exists"
            }
    except Exception as e:
        print(f"Cache check error: {e}")
    
    # Trigger background generation
    try:
        from app.utils.background_tasks import trigger_image_generation
        
        print(f"Attempting to generate personalized image for user {current_user.id}, product {product_id}")
        print(f"User image path: {current_user.image}")
        print(f"Product image path: {product.image}")
        
        result = trigger_image_generation(
            background_tasks=background_tasks,
            user=current_user,
            product=product
        )
        
        print(f"Generation trigger result: {result}")
        
        return {
            "status": "generation_started",
            "message": "Personalized image generation started",
            "estimated_time": "30-60 seconds"
        }
        
    except Exception as e:
        print(f"Generation trigger error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to start image generation: {str(e)}")


@router.get("/categories/list")
async def get_categories(db: Session = Depends(get_db)):
    """Get all unique categories"""
    categories = db.query(Product.category).distinct().all()
    return {"categories": [cat[0] for cat in categories]}

