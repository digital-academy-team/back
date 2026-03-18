from rest_framework import serializers

from apps.course.models.units import CourseUnit
from common.serializers.courses.lessons import LessonCreateSerializer, LessonUpdateSerializer




class CourseUnitListSerializer(serializers.ModelSerializer):

    lessons = LessonCreateSerializer(many=True)

    class Meta:
        model = CourseUnit
        fields = [
            "id",
            "title",
            "desc",
            "lessons",
        ]



class CourseUnitCreateSerializer(serializers.ModelSerializer):
    lessons = LessonCreateSerializer(many=True, write_only=True)

    class Meta:
        model = CourseUnit
        fields = [
            "title",
            "desc",
            "lessons",
        ]




class CourseUnitUpdateSerializer(serializers.ModelSerializer):
    lessons = LessonUpdateSerializer(many=True)

    class Meta:
        model = CourseUnit
        fields = [
            "title",
            "desc",
            "lessons",
        ]