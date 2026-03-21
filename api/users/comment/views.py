from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated

from apps.comments.models import Comment
from common.serializers.comments.serializers import CommentCreateSerializer, CommentSerializer


class CommentViewSet(mixins.ListModelMixin,
                     mixins.CreateModelMixin,
                     viewsets.GenericViewSet):

    queryset = Comment.objects.select_related("user", "course")
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "create":
            return CommentCreateSerializer

        return CommentSerializer


    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
