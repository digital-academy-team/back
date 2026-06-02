from rest_framework import serializers

from apps.course.models.student_activity import DiscussionPost, ExerciseSubmission


def _display_name(user) -> str:
    if not user:
        return 'Student'
    name = (user.get_full_name() or '').strip()
    return name or user.username or user.email or 'Student'


class DiscussionPostSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()

    class Meta:
        model = DiscussionPost
        fields = ['id', 'author', 'author_name', 'text', 'created_at']
        read_only_fields = ['id', 'author', 'author_name', 'created_at']

    def get_author_name(self, obj) -> str:
        return _display_name(obj.author)


class DiscussionPostWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscussionPost
        fields = ['text']


class ExerciseSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExerciseSubmission
        fields = ['id', 'code', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
