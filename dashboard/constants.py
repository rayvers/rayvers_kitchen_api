import cloudinary.uploader

def upload_to_cloudinary(file):
    """Uploads a file to Cloudinary and returns the URL."""
    if not file:
        return None

    try:
        response = cloudinary.uploader.upload(file)
        return response.get("secure_url")  # Get the URL from Cloudinary response
    except Exception as e:
        print(f"Cloudinary upload failed: {e}")
        return None
    

