from django.shortcuts import redirect
from django.conf import settings
from django.contrib.auth import authenticate
from rest_framework import status, serializers, generics
from rest_framework.generics import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from drf_spectacular.utils import extend_schema
import requests
from urllib.parse import urlencode

from apps.user.models import User
from common.serializers.auth.serializer import generate_new_tokens, LoginSerializer, SetPasswordSerializer, \
    ProfileSerializer, ProfileUpdateSerializer


class GoogleLoginView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        auth_url = (
            "https://accounts.google.com/o/oauth2/v2/auth"
            f"?client_id={settings.GOOGLE_CLIENT_ID}"
            f"&redirect_uri={settings.GOOGLE_REDIRECT_URI}"
            f"&response_type=code"
            f"&scope=openid email profile"
            f"&access_type=offline"
            f"&prompt=consent"
        )
        return redirect(auth_url)


class GoogleAuthCallback(APIView):
    permission_classes = [AllowAny]

    @extend_schema(exclude=True)
    def get(self, request):
        code = request.GET.get("code")

        # 1. Google Token
        token_res = requests.post(settings.GOOGLE_TOKEN_URL, data={
            "code": code,
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code",
        })
        token_json = token_res.json()

        # 2. collecting user data
        userinfo_res = requests.get(
            settings.GOOGLE_USER_INFO_URL,
            headers={"Authorization": f"Bearer {token_json.get('access_token')}"}
        )
        userinfo = userinfo_res.json()
        email = userinfo.get("email")
        first_name = userinfo.get("given_name", "")
        last_name = userinfo.get("family_name", "")

        # 3. Create User
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'username': email,
                'first_name': first_name,
                'last_name': last_name,
                'is_active': True,
            }
        )

        # make password for temporary
        if created:
            user.set_unusable_password()
            user.save()

        # 4. Generate Token
        tokens = generate_new_tokens(user)

        # check password is_exist?
        has_password = user.has_usable_password() and not user.password.startswith('!')

        role = user.role  # yoki sizning role logikangizdan oling

        params = urlencode({
            "access": tokens["access_token"],
            "refresh": tokens["refresh_token"],
            "has_password": str(has_password).lower(),
            "user_id": str(user.id),
            "email": email or "",
            "role": role,
        })

        redirect_url = f"{settings.FRONTEND_URL}/auth/callback?{params}"
        return redirect(redirect_url)


class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(request=LoginSerializer)
    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.validated_data['user']
            tokens = generate_new_tokens(user)
            return Response({
                "access": tokens['access_token'],
                "refresh": tokens['refresh_token'],
                "user": {"email": user.email, "id": user.id, "role": user.role}
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SetInitialPasswordAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(request=SetPasswordSerializer)
    def patch(self, request, user_id):
        user = get_object_or_404(User, id=user_id)

        # checking password is_real?
        if user.has_usable_password() and not user.password.startswith('!'):
            return Response(
                {"error": "You already set up password"},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = SetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            new_password = serializer.validated_data.get('new_password1')
            user.set_password(new_password)
            user.save()

            return Response({"message": "Password Successfully set"}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class ProfileRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'patch',]

    def get_serializer_class(self):
        if self.request.method in ['PATCH']:
            return ProfileUpdateSerializer
        return ProfileSerializer

    def get_object(self):
        return self.request.user
