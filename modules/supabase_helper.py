import os
from supabase import create_client, Client
from flask import current_app

def get_supabase_client() -> Client:
    url = current_app.config.get('SUPABASE_URL')
    key = current_app.config.get('SUPABASE_KEY')
    
    # Check for common mistake: using a publishable key from another service (like Stripe/Clerk)
    if key and (key.startswith('sb_publishable_') or key.startswith('pk_')):
        print("\n" + "!"*60)
        print("CRITICAL CONFIG ERROR: INVALID SUPABASE_KEY DETECTED!")
        print(f"Current Key starts with: {key[:15]}...")
        print("Supabase 'anon' keys are long JWT strings starting with 'eyJ...'.")
        print("Please get the correct 'anon public' key from your Supabase Dashboard:")
        print("Settings -> API -> Project API keys -> anon public")
        print("!"*60 + "\n")
        return None
        
    if not url or not key:
        return None
        
    try:
        return create_client(url, key)
    except Exception as e:
        print(f"DEBUG: Failed to initialize Supabase client: {str(e)}")
        return None


def upload_file_to_supabase(bucket: str, file_obj, remote_path: str):
    """
    Uploads a file object to Supabase storage.
    Returns the public URL of the uploaded file.
    """
    supabase = get_supabase_client()
    if not supabase:
        return None

    try:
        # Reset file pointer before reading
        file_obj.seek(0)
        file_data = file_obj.read()
        
        # Reset pointer again so the caller can still use the file_obj if we fail
        file_obj.seek(0)
        
        print(f"DEBUG: Requesting upload to bucket '{bucket}' path '{remote_path}'...")
        
        # Determine content type
        content_type = "application/octet-stream"
        if remote_path.lower().endswith('.pdf'): content_type = "application/pdf"
        elif remote_path.lower().endswith('.png'): content_type = "image/png"
        elif remote_path.lower().endswith('.jpg') or remote_path.lower().endswith('.jpeg'): content_type = "image/jpeg"

        # PERFORM UPLOAD
        supabase.storage.from_(bucket).upload(
            path=remote_path,
            file=file_data,
            file_options={"content-type": content_type, "x-upsert": "true"}
        )
        
        # Get public URL
        url_res = supabase.storage.from_(bucket).get_public_url(remote_path)
        
        # Some versions return an object with public_url or publicUrl
        if hasattr(url_res, 'public_url'):
            return url_res.public_url
        if isinstance(url_res, dict) and 'publicUrl' in url_res:
            return url_res['publicUrl']
            
        return str(url_res)

    except Exception as e:
        import traceback
        print(f"DEBUG: Supabase upload failed: {str(e)}")
        traceback.print_exc()
        # Reset pointer one last time for safety
        file_obj.seek(0)
        return None

def delete_file_from_supabase(bucket: str, remote_path: str):
    """Deletes a file from Supabase storage."""
    supabase = get_supabase_client()
    if not supabase: return False
    try:
        supabase.storage.from_(bucket).remove([remote_path])
        print(f"DEBUG: Deleted {remote_path} from Supabase bucket '{bucket}'.")
        return True
    except Exception as e:
        print(f"DEBUG: Supabase delete failed: {str(e)}")
        return False
