from cloudinary.utils import cloudinary_url

def get_optimized_image_url(image, width):
    """
    Generate an optimized Cloudinary image URL.

    Args:
        image: Django ImageField or FieldFile.
        width: Desired image width in pixels.
    """
    
    if not image:
        return None
    
    if not image.name:
        return None
    
    try:
        url, options = cloudinary_url(
            image.name,
            width=width,
            crop="limit",
            quality="auto",
            fetch_format="auto",
            secure=True,
        )
        return url
    
    except Exception:
        return image.url