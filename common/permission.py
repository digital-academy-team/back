from rest_framework import permissions
from apps.user.models import UserRoles


class IsCourseTeacherOrAdmin(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        return bool(
            request.user
            and request.user.is_authenticated
            and (
                request.user.is_staff
                or request.user.role in [UserRoles.ADMIN, UserRoles.TEACHER]
            )
        )

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.is_staff or request.user.role == UserRoles.ADMIN:
            return True

        return obj.created_by == request.user


class IsAdminOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        return bool(
            request.user
            and request.user.is_authenticated
            and (
                request.user.is_staff
                or request.user.role == UserRoles.ADMIN
            )
        )

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return bool(
            request.user
            and request.user.is_authenticated
            and (
                request.user.is_staff
                or request.user.role == UserRoles.ADMIN
            )
        )