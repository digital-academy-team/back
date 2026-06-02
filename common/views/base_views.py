from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.permissions import IsAuthenticated
from apps.admins.authentication import AdminJWTAuthentication
from apps.users.authentication import UserJWTAuthentication


# USER
class BaseUserModelViewSet(ModelViewSet):
    authentication_classes = [UserJWTAuthentication]


class BaseUserGenericViewSet(GenericViewSet):
    authentication_classes = [UserJWTAuthentication]


# ADMIN
class BaseAdminModelViewSet(ModelViewSet):
    authentication_classes = [AdminJWTAuthentication]
    permission_classes = [IsAuthenticated]


class BaseAdminGenericViewSet(GenericViewSet):
    authentication_classes = [AdminJWTAuthentication]
    permission_classes = [IsAuthenticated]
