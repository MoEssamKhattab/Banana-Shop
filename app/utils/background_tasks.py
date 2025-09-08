import asyncio
from fastapi import BackgroundTasks
from typing import Optional
from app.services.genai_service import generate_product_image, save_image
from app.utils.image_cache import image_cache
from app.models import User, Product
import tempfile
import os

class ImageGenerationTask:
    def __init__(self):
        self.active_generations = set()  # Track ongoing generations
    
    def is_generating(self, user_id: int, product_id: int) -> bool:
        """Check if image generation is already in progress for this user-product pair"""
        key = f"{user_id}_{product_id}"
        return key in self.active_generations
    
    def start_generation(self, user_id: int, product_id: int):
        """Mark generation as started"""
        key = f"{user_id}_{product_id}"
        self.active_generations.add(key)
    
    def finish_generation(self, user_id: int, product_id: int):
        """Mark generation as finished"""
        key = f"{user_id}_{product_id}"
        self.active_generations.discard(key)
    
    async def generate_user_product_image(
        self, 
        user_id: int, 
        product_id: int, 
        user_image_path: str, 
        product_image_path: str
    ):
        """Background task to generate and cache user-product image"""
        generation_key = f"{user_id}_{product_id}"
        
        try:
            print(f"Starting background image generation for user {user_id}, product {product_id}")
            
            # Mark as generating
            self.start_generation(user_id, product_id)
            
            # Check if already cached (double-check in case of race condition)
            if image_cache.is_cached(user_id, product_id):
                print(f"Image already cached for user {user_id}, product {product_id}")
                return
            
            # Convert relative paths to absolute paths
            import os
            
            # Convert user image path (remove leading slash and prepend with current directory)
            if user_image_path.startswith('/static/'):
                user_image_path = user_image_path[1:]  # Remove leading slash
            user_full_path = os.path.join(os.getcwd(), user_image_path)
            
            # Convert product image path
            if product_image_path.startswith('/static/'):
                product_image_path = product_image_path[1:]  # Remove leading slash
            product_full_path = os.path.join(os.getcwd(), product_image_path)
            
            print(f"User image full path: {user_full_path}")
            print(f"Product image full path: {product_full_path}")
            
            # Check if files exist
            if not os.path.exists(user_full_path):
                print(f"User image not found: {user_full_path}")
                return
            
            if not os.path.exists(product_full_path):
                print(f"Product image not found: {product_full_path}")
                return
            
            # Generate the image using asyncio to run in thread pool to prevent blocking
            import asyncio
            loop = asyncio.get_event_loop()
            
            # Add timeout to prevent hanging (60 seconds max)
            try:
                response = await asyncio.wait_for(
                    loop.run_in_executor(
                        None,  # Use default thread pool
                        generate_product_image,
                        product_full_path,
                        user_full_path
                    ),
                    timeout=60.0  # 60 second timeout
                )
            except asyncio.TimeoutError:
                print(f"Image generation timed out for user {user_id}, product {product_id}")
                return
            
            # Save to temporary location first
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                temp_path = temp_file.name
            
            save_image(response, temp_path)
            
            # Move to cache
            cache_url = image_cache.save_generated_image(user_id, product_id, temp_path)
            
            # Clean up temporary file
            os.unlink(temp_path)
            
            print(f"Successfully generated and cached image for user {user_id}, product {product_id}")
            print(f"Cache URL: {cache_url}")
            
        except Exception as e:
            print(f"Error generating image for user {user_id}, product {product_id}: {e}")
        finally:
            # Always mark as finished
            self.finish_generation(user_id, product_id)

# Global task manager
image_task_manager = ImageGenerationTask()


def trigger_image_generation(
    background_tasks: BackgroundTasks,
    user: User,
    product: Product
) -> Optional[str]:
    """
    Trigger image generation if needed and return cached image URL if available.
    Returns None if no cache exists and generation is starting.
    """
    if not user or not user.image:
        return None
    
    user_id = user.id
    product_id = product.id
    
    # Check cache first
    cached_url = image_cache.get_cached_image_url(user_id, product_id)
    if cached_url:
        print(f"Found cached image for user {user_id}, product {product_id}: {cached_url}")
        return cached_url
    
    # Check if generation is already in progress
    if image_task_manager.is_generating(user_id, product_id):
        print(f"Image generation already in progress for user {user_id}, product {product_id}")
        return None
    
    # Start background generation
    print(f"Starting background image generation for user {user_id}, product {product_id}")
    background_tasks.add_task(
        image_task_manager.generate_user_product_image,
        user_id=user_id,
        product_id=product_id,
        user_image_path=user.image,
        product_image_path=product.image
    )
    
    return None  # No cached image available yet
