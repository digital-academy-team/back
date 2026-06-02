import random
from django.core.cache import cache
from django.contrib.auth.hashers import make_password

from apps.user.models import User


def generate_verification_code():
    return str(random.randint(100000, 999999))


def cache_register_data(username, email, password):
    code = generate_verification_code()

    cache.set(
        f"register_data:{email}",
        {
            "username": username,
            "email": email,
            "password": make_password(password),
            "code": code,
        },
        timeout=300,  # 5 minut
    )
    return code


def verify_register_code(email, code):
    data = cache.get(f"register_data:{email}")

    if not data:
        return None, "Code expired or not found."

    if data["code"] != code:
        return None, "Invalid code."

    if User.objects.filter(email=email).exists():
        return None, "User with this email already exists."

    user = User.objects.create(
        username=data["username"],
        email=data["email"],
        password=data["password"],
    )

    cache.delete(f"register_data:{email}")
    return user, None