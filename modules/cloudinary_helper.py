import cloudinary
import cloudinary.uploader
import cloudinary.api
from flask import current_app

def upload_file_to_cloudinary(file_obj, folder="dronacharya_hub"):
    """
    Uploads a file object to Cloudinary and returns the secure URL.
    """
    if not current_app.config.get('CLOUDINARY_URL'):
        # Fallback to local storage if Cloudinary is not configured yet
        return None

    try:
        result = cloudinary.uploader.upload(
            file_obj,
            folder=folder,
            resource_type="auto"
        )
        return result.get('secure_url')
    except Exception as e:
        print(f"Cloudinary Upload Error: {e}")
        return None
