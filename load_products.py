import json
import os
from sqlalchemy.orm import sessionmaker
from app.database import engine, create_tables
from app.models import Product, Base

def reset_database():
    """Completely reset the database by dropping and recreating all tables"""
    print("Resetting database...")
    
    # Drop all tables
    Base.metadata.drop_all(bind=engine)
    print("All tables dropped.")
    
    # Recreate all tables
    Base.metadata.create_all(bind=engine)
    print("All tables recreated.")

def load_products_from_json():
    """Load products from data.json file into the database"""
    
    # Reset the database completely
    reset_database()
    
    # Create session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Check if data.json exists
        if not os.path.exists("data.json"):
            print("Error: data.json file not found!")
            return
            
        # Read the JSON file
        with open("data.json", "r", encoding="utf-8") as file:
            products_data = json.load(file)
        
        print(f"Found {len(products_data)} products in data.json")
        
        # No need to clear existing products since we reset the database
        
        # Add products to database
        for sku, product_info in products_data.items():
            # Determine gender based on product name and category (basic logic)
            # You can adjust this logic based on your data
            gender = "men"  # Default to men for now, as the sample data appears to be men's clothing
            
            # If you want to add women's products, you can modify this logic
            # For now, we'll create all as men's products since the data seems to be men's fashion
            
            product = Product(
                sku=sku,
                name=product_info["name"],
                price=product_info["price"],
                category=product_info["category"],
                image=product_info["image"],
                description=product_info["description"],
                sizes=product_info["sizes"],
                colors=product_info["colors"],
                gender=gender
            )
            
            db.add(product)
        
        db.commit()
        print(f"Successfully loaded {len(products_data)} products into the database")
        
        # Print some stats
        men_count = db.query(Product).filter(Product.gender == "men").count()
        women_count = db.query(Product).filter(Product.gender == "women").count()
        print(f"Men's products: {men_count}")
        print(f"Women's products: {women_count}")
        
    except Exception as e:
        print(f"Error loading products: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    load_products_from_json()
