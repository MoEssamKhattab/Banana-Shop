import os
import hashlib
from typing import Optional
from pathlib import Path

class ImageCache:
    def __init__(self, cache_dir: str = "static/generated/cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def get_cache_key(self, user_id: int, product_id: int) -> str:
        """Generate a unique cache key for user-product combination"""
        return f"user_{user_id}_product_{product_id}"
    
    def get_cache_path(self, user_id: int, product_id: int) -> Path:
        """Get the full path where the cached image should be stored"""
        cache_key = self.get_cache_key(user_id, product_id)
        return self.cache_dir / f"{cache_key}.png"
    
    def get_cache_url(self, user_id: int, product_id: int) -> str:
        """Get the URL path for the cached image"""
        cache_key = self.get_cache_key(user_id, product_id)
        return f"/static/generated/cache/{cache_key}.png"
    
    def is_cached(self, user_id: int, product_id: int) -> bool:
        """Check if a generated image exists in cache"""
        cache_path = self.get_cache_path(user_id, product_id)
        return cache_path.exists()
    
    def get_cached_image_url(self, user_id: int, product_id: int) -> Optional[str]:
        """Get cached image URL if it exists, None otherwise"""
        if self.is_cached(user_id, product_id):
            return self.get_cache_url(user_id, product_id)
        return None
    
    def save_generated_image(self, user_id: int, product_id: int, image_path: str) -> str:
        """Save a generated image to cache and return the cache URL"""
        cache_path = self.get_cache_path(user_id, product_id)
        
        # Copy the generated image to cache location
        import shutil
        shutil.copy2(image_path, cache_path)
        
        return self.get_cache_url(user_id, product_id)
    
    def clear_user_cache(self, user_id: int):
        """Clear all cached images for a specific user"""
        pattern = f"user_{user_id}_product_*.png"
        for cache_file in self.cache_dir.glob(pattern):
            cache_file.unlink()
    
    def clear_product_cache(self, product_id: int):
        """Clear all cached images for a specific product"""
        pattern = f"user_*_product_{product_id}.png"
        for cache_file in self.cache_dir.glob(pattern):
            cache_file.unlink()

# Global cache instance
image_cache = ImageCache()
