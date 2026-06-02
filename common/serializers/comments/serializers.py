from rest_framework import serializers

from apps.comments.models import Comment


class CommentSerializer(serializers.ModelSerializer):

    first_name = serializers.CharField(source='user.first_name', read_only=True)
    avatar_url = serializers.CharField(source='user.avatar', read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "avatar_url", "first_name", "comment", "likes", "created_at"]





class CommentCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = ["course", "comment", "likes"]


    def validate_likes(self, value):
        if value > 5:
            raise serializers.ValidationError("likes cannot be greater than 5")
        return value
