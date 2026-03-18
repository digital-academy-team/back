from rest_framework import serializers

from apps.course.models.lessons import Lessons


class LessonsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Lessons
        fields = ["id", "title", "video", "presentation", "additional_task"]



class BaseLessonSerializer(serializers.ModelSerializer):


    def validate_video(self, value):
        if not value:
            return value

        allowed_extensions = [".mp4", ".mov", ".avi", ".mkv", ".webm"]
        file_name = value.name.lower()

        if not any(file_name.endswith(ext) for ext in allowed_extensions):
            raise serializers.ValidationError(
                "Video fayl quyidagi formatlardan biri bo‘lishi kerak: mp4, mov, avi, mkv, webm."
            )

        if value.content_type and not value.content_type.startswith("video/"):
            raise serializers.ValidationError("Yuklangan fayl video bo‘lishi kerak.")

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
                "Presentation fayli pdf, ppt, pptx, doc yoki docx formatda bo‘lishi kerak."
            )

        if value.content_type and value.content_type not in allowed_content_types:
            raise serializers.ValidationError(
                "Presentation fayli faqat pdf, ppt, pptx, doc yoki docx bo‘lishi kerak."
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