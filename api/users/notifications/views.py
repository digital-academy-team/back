"""In-app notification endpoints (any authenticated user).

* GET  /api/users/notifications/             – recent notifications + unread count.
* GET  /api/users/notifications/unread-count/ – just the unread count.
* POST /api/users/notifications/<id>/read/    – mark one as read.
* POST /api/users/notifications/read-all/     – mark all as read.

Every query is scoped to ``recipient=request.user`` so a user can never see
or mutate someone else's notifications.
"""

from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.notifications.models import Notification
from common.serializers.notifications.serializer import NotificationSerializer

RECENT_LIMIT = 50


class NotificationListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        base = Notification.objects.filter(recipient=request.user)
        unread = base.filter(is_read=False).count()
        rows = base.select_related("actor")[:RECENT_LIMIT]
        return Response(
            {
                "data": NotificationSerializer(rows, many=True).data,
                "extra": {"unread": unread},
            }
        )


class NotificationUnreadCountView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        unread = Notification.objects.filter(recipient=request.user, is_read=False).count()
        return Response({"unread": unread})


class NotificationMarkReadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
        notification.mark_read()
        return Response(NotificationSerializer(notification).data)


class NotificationMarkAllReadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        updated = Notification.objects.filter(
            recipient=request.user, is_read=False
        ).update(is_read=True, read_at=timezone.now())
        return Response({"updated": updated})
