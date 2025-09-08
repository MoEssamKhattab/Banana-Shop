from dotenv import load_dotenv
import os
from google import genai
from google.genai import types
from PIL import Image
import pathlib

load_dotenv()
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

TEXT_MODEL = "gemini-2.5-flash"
IMAGE_MODEL = "gemini-2.5-flash-image-preview"


# IMAGE_PROMPT = (
# """You are provided with two images:
# - one contains a person.
# - the other contains an item of clothing.

# Your task is to:
# Generate a new, photorealistic image where the person is wearing the clothing item from the other image.
# Dress the person in the clothing item from the other image.

# The final image must adhere to the following requirements:
# - Clothing Preservation: The design, color, and texture of the clothing item from the second image must also remain identical.
# - Setting: The person should be depicted as a model in an indoor photoshoot with professional, soft lighting.
# - Styling: Complete the outfit with other complementary clothing pieces and accessories that stylistically and color-wise match the provided item from the second image. The overall look should be cohesive, fashionable, and natural.
# - Aesthetic: The final image should have a high-fashion, professional, and naturalistic aesthetic.
# """
# )

IMAGE_PROMPT = (
"Generate a photorealistic, high-resolution image of the person from [person_image] "
"wearing the clothing item from [clothing_image]. The image should be a full-body shot "
"of the person in a dynamic pose, set against the backdrop of an indoor fashion shoot. "
"The lighting should be professional and dramatic, typical of a high-fashion magazine editorial. "
"The final image should be of editorial quality, with sharp focus and  white background with "
"professional lightening. Keep the person details."
)

def save_image(response, path):
    # Ensure the directory exists
    path_obj = pathlib.Path(path)
    path_obj.parent.mkdir(parents=True, exist_ok=True)
    
    saved = False
    for i, part in enumerate(response.parts):
        if image := part.as_image():
            image.save(path)
            print(f"Image saved to: {path}")
            saved = True
            break
    
    if not saved:
        print("No image found in response parts")
        print(f"Response has {len(response.parts)} parts")
        for i, part in enumerate(response.parts):
            if hasattr(part, 'inline_data'):
                print(f"Part {i} has inline_data with mime_type: {getattr(part.inline_data, 'mime_type', 'unknown')}")
            else:
                print(f"Part {i} type: {type(part)}")


def generate_product_image(
        product_image_path: str,
        user_image_path: str,
        prompt: str = IMAGE_PROMPT):
    """Generate a new product image using GenAI"""
    
    try:
        # Check if files exist
        if not os.path.exists(product_image_path):
            raise FileNotFoundError(f"Product image not found: {product_image_path}")
        if not os.path.exists(user_image_path):
            raise FileNotFoundError(f"User image not found: {user_image_path}")
        
        contents = [
            prompt,
            Image.open(product_image_path),
            Image.open(user_image_path)
        ]
        response = client.models.generate_content(
            model=IMAGE_MODEL,
            contents=contents,
            config=types.GenerateContentConfig(
                response_modalities=['Text', 'Image']
            )
        )
        print(response)
        return response
    except Exception as e:
        print(f"Error generating product image: {e}")
        raise


if __name__ == "__main__":
    try:
        print("Generating product image...")
        response = generate_product_image(
            product_image_path="static/products/04302340500-e1.jpg",
            user_image_path="static/uploads/profile_images/620fca22-a0da-485c-ad43-4c71cca08809.png"
        )
        save_image(response, "static/generated/generated_image.png")
        print("Image generation completed successfully!")
    except Exception as e:
        print(f"Error in main execution: {e}")
        import traceback
        traceback.print_exc()