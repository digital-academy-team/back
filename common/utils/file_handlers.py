# core/utils/files.py
import os
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from rest_framework.exceptions import ValidationError

def validate_image(value):
    if value:
        valid_extensions = {'.png', '.jpg', '.jpeg', '.webp'}
        ext = os.path.splitext(value.name)[1].lower()

        if ext not in valid_extensions:
            raise ValidationError("Invalid file type. Allowed: PNG, JPG, JPEG, WEBP.")

        max_size = 5 * 1024 * 1024  # 5MB
        if value.size > max_size:
            raise ValidationError("Image file size must be under 5MB.")
    return value

def delete_files(file_paths: list):
    """
    Delete files safely from MEDIA_ROOT.
    Accepts relative paths or full URLs.
    """
    for path in file_paths:
        try:
            # Normalize input (strip BASE_URL and MEDIA_URL if present)
            relative_path = path.replace(f"{settings.BASE_URL}{settings.MEDIA_URL}", "")
            relative_path = relative_path.replace(settings.MEDIA_URL, "").lstrip("/")

            full_path = os.path.join(default_storage.location, relative_path)

            if os.path.exists(full_path):
                os.remove(full_path)
                print(f"✅ Deleted: {relative_path}")
            else:
                print(f"⚠️ Not found: {relative_path}")

        except Exception as e:
            print(f"❗️Failed to delete {path} — {e}")



def save_unique_file(uploaded_file, folder: str) -> str:
    filename = os.path.join(folder, uploaded_file.name)

    if default_storage.exists(filename):
        default_storage.delete(filename)

    saved_path = default_storage.save(filename, ContentFile(uploaded_file.read()))

    full_url = f"{settings.MEDIA_URL}{saved_path}"
    if full_url.startswith("/"):
        full_url = f"{settings.BASE_URL}{full_url}"

    return full_url
