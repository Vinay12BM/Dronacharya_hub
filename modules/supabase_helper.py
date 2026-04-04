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
        return None

    try:
        # Seek to start of file to ensure full upload
        file_obj.seek(0)
        file_data = file_obj.read()
        
        # Create a unique filename if it doesn't have one
        import uuid
        ext = file_obj.filename.split('.')[-1] if '.' in file_obj.filename else 'bin'
        filename = f"{folder}/{uuid.uuid4().hex}.{ext}"
        
        # Upload
        res = supabase.storage.from_(bucket).upload(
            path=filename,
            file=file_data,
            file_options={"content-type": file_obj.content_type if hasattr(file_obj, 'content_type') else "application/octet-stream"}
        )
        
        # Get public URL
        # URL format: {SUPABASE_URL}/storage/v1/object/public/{bucket}/{filename}
        public_url = f"{current_app.config['SUPABASE_URL']}/storage/v1/object/public/{bucket}/{filename}"
        return public_url
    except Exception as e:
        print(f"Supabase Storage Error: {e}")
        return None
