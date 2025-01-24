import random
import string

from django.contrib.auth import get_user_model

User = get_user_model()


def generate_unique_username(length=10):
    """Generate a random unique username of specified length using letters"""
    while True:
        random_string = "".join(random.choices(string.ascii_letters, k=length))
        username = f"deleted_{random_string}"

        if not User.objects.filter(username=username).exists():
            return username
