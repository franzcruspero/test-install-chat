import os
import uuid

from django.core.files.storage import FileSystemStorage


class UniqueFileStorage(FileSystemStorage):
    def get_available_name(self, name, max_length=None):
        ext = name.split(".")[-1]
        unique_name = f"{uuid.uuid4()}.{ext}"
        return os.path.join("profile_pictures", unique_name)
