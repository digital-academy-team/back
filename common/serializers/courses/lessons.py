from rest_framework import serializers

from apps.course.models.lessons import Lessons
from common.serializers.quiz.serializer import QuizDetailSerializer


class LessonsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Lessons
        fields = ["id", "title", "video", "presentation", "additional_task"]


class StudentLessonsSerializer(serializers.ModelSerializer):

    quizzes = QuizDetailSerializer(many=True, read_only=True)

    class Meta:
        model = Lessons
        fields = ["id", "title", "video", "presentation", "additional_task", "quizzes"]


class BaseLessonSerializer(serializers.ModelSerializer):


    def validate_video(self, value):
        if not value:
            return value

        allowed_extensions = [".mp4", ".mov", ".avi", ".mkv", ".webm"]
        file_name = value.name.lower()

        if not any(file_name.endswith(ext) for ext in allowed_extensions):
            raise serializers.ValidationError(
                "File type must be: mp4, avi, mkv, or webm."
            )

        if value.content_type and not value.content_type.startswith("video/"):
            raise serializers.ValidationError("File must be video.")

        return value

    def validate_presentation(self, value):
        if not value:
            return value

        allowed_extensions = [
            ".pdf",
            ".ppt",
            ".pptx",
            ".doc",
            ".docx",
        ]
        allowed_content_types = [
            "application/pdf",
            "application/vnd.ms-powerpoint",
            "application/vnd.openxmlformats-officedocument.presentationml.presentation",
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ]

        file_name = value.name.lower()

        if not any(file_name.endswith(ext) for ext in allowed_extensions):
            raise serializers.ValidationError(
                "Presentation type must be: pdf, ppt, pptx, doc yoki docx"
            )

        if value.content_type and value.content_type not in allowed_content_types:
            raise serializers.ValidationError(
                "Presentation type must be: pdf, ppt, pptx, doc yoki docx"
            )

        return value



class LessonCreateSerializer(BaseLessonSerializer):

    class Meta:
        model = Lessons
        fields = ["title", "desc", "presentation", "video", "additional_task"]




class LessonUpdateSerializer(BaseLessonSerializer):

    presentation = serializers.FileField(required=False)
    video = serializers.FileField(required=False)

    class Meta:
        model = Lessons
        fields = ["title", "desc", "presentation", "video", "additional_task"]