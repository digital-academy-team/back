from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

def save_uploaded_file_keep_name(uploaded_file, folder='uploads'):

    path = f"{folder}/{uploaded_file.name}"

    # Delete existing file if same name exists
    if default_storage.exists(path):
        default_storage.delete(path)

    # Save file
    saved_path = default_storage.save(path, ContentFile(uploaded_file.read()))
    return saved_path


def delete_files(paths: list):
    """
    Delete multiple files from MEDIA_ROOT given a list of relative paths.
    """
    for path in paths:
        try:
            if default_storage.exists(path):
                default_storage.delete(path)
        except Exception as e:
            print(f"❗️Error deleting file {path}: {e}")
