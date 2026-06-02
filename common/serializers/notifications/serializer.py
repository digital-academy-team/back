from rest_framework import serializers

from apps.notifications.models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    actor_name = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = [
            "id",
            "type",
            "title",
            "message",
            "link",
            "meta",
            "is_read",
            "read_at",
            "actor",
            "actor_name",
            "created_at",
        ]
        read_only_fields = fields

    def get_actor_name(self, obj) -> str:
        if not obj.actor:
            return ""
        return (obj.actor.get_full_name() or obj.actor.username or "").strip()
