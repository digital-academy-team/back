from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

from apps.user.models import User


def generate_new_tokens(user):
    refresh = RefreshToken.for_user(user)
    return {
        "access_token": str(refresh.access_token),
        "refresh_token": str(refresh)
    }

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=False, allow_blank=True, write_only=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        user = User.objects.filter(email=email).first()
        if not user:
            raise serializers.ValidationError({"email": "User not Found."})


        if password:
            authenticated_user = authenticate(username=email, password=password)
            if authenticated_user:
                data["user"] = authenticated_user
                return data


        if not user.has_usable_password() or user.password.startswith('!'):
            raise serializers.ValidationError({
                "set_password_required": True,
                "message": "After registered sign up with google please set password!.",
                "user_id": user.id
            })


        raise serializers.ValidationError({"password": "Invalid Credentials."})


class SetPasswordSerializer(serializers.Serializer):
    new_password1 = serializers.CharField(required=True, write_only=True, validators=[validate_password])
    new_password2 = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        if data['new_password1'] != data['new_password2']:
            raise serializers.ValidationError({"new_password1": "code is not match"})
        return data