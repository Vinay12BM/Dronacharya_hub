import os
from supabase import create_client, Client
from flask import current_app

def get_supabase_client() -> Client:
    url = current_app.config.get('SUPABASE_URL')
    key = current_app.config.get('SUPABASE_KEY')
    if not url or not key:
        return None
    return create_client(url, key)

def upload_file_to_supabase(file_obj, folder="uploads", bucket="dronacharya-hub"):
    """
    Uploads a file object to Supabase Storage and returns the public URL.
    """
    supabase = get_supabase_client()
    if not supabase:
        print("ERROR: Supabase client could not be initialized.")
        return None

    try:
        # Seek to start of file to ensure full upload
        file_obj.seek(0)
        file_data = file_obj.read()
        
        # Create a unique filename
        import uuid
        ext = 'png'
        if hasattr(file_obj, 'filename') and '.' in file_obj.filename:
            ext = file_obj.filename.split('.')[-1]
        
        filename = f"{folder}/{uuid.uuid4().hex}.{ext}"
        
        # Upload
        content_type = getattr(file_obj, 'content_type', 'image/png')
        
        print(f"DEBUG: Attempting upload to bucket '{bucket}', path '{filename}'")
        res = supabase.storage.from_(bucket).upload(
            path=filename,
            file=file_data,
            file_options={"content-type": content_type}
        )
        
        # In some SDK versions, check if it's an error response
        if hasattr(res, 'error') and res.error:
            print(f"ERROR: Supabase upload failed for {filename}: {res.error}")
            return None
            
        # Success - Get public URL using official SDK method
        try:
            public_url_res = supabase.storage.from_(bucket).get_public_url(filename)
            # Depending on version it might be a string or a response object with 'public_url'
            if isinstance(public_url_res, str):
                public_url = public_url_res
            else:
                # Some versions return an object with a public_url attribute or key
                public_url = getattr(public_url_res, 'public_url', str(public_url_res))
            
            print(f"DEBUG: Upload SUCCESS. Public URL: {public_url}")
            return public_url
        except Exception as url_err:
            # Fallback to manual construction if get_public_url fails
            print(f"DEBUG: get_public_url failed, using manual construction: {url_err}")
            base_url = current_app.config['SUPABASE_URL'].rstrip('/')
            return f"{base_url}/storage/v1/object/public/{bucket}/{filename}"
            
    except Exception as e:
        print(f"EXCEPTION: Supabase Storage Error during upload: {e}")
        return None
