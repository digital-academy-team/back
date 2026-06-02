from django.urls import path
from api.users.auth.views import (GoogleLoginView, GoogleAuthCallback, LoginAPIView, SetInitialPasswordAPIView,
                                  ProfileRetrieveUpdateAPIView)

urlpatterns = [
    path("google/login/", GoogleLoginView.as_view()),
    path("google/callback/", GoogleAuthCallback.as_view()),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('set-password/<uuid:user_id>/', SetInitialPasswordAPIView.as_view(), name='set-password'),
    path('profile/', ProfileRetrieveUpdateAPIView.as_view(), name='profile-detail-update'),
]