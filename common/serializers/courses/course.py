import json

from rest_framework import serializers

from apps.course.models.course import Course
from apps.course.models.lessons import Lessons
from apps.course.models.units import CourseUnit
from common.serializers.courses.units import CourseUnitCreateSerializer, CourseUnitUpdateSerializer, \
    CourseUnitListSerializer


class CourseUserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ["id", "title", "desc", "base_price", "discount_price"]



class CourseDetailSerializer(serializers.ModelSerializer):
    units = CourseUnitListSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = ["id", "title", "desc", "base_price", "discount_price", "units"]



class CourseCreateSerializer(serializers.ModelSerializer):
    units = serializers.ListField(write_only=True)  # JSON string yoki array

    class Meta:
        model = Course
        fields = ['title', 'desc', 'base_price', 'discount_price', 'units', 'category']


    def create(self, validated_data):
        request = self.context['request']
        files = request.FILES

        units_data = validated_data.pop('units')

        # 🔥 FIX
        if isinstance(units_data, list):
            units_data = units_data[0]

        if isinstance(units_data, str):
            units_data = json.loads(units_data)

        course = Course.objects.create(**validated_data)

        for u_idx, unit_data in enumerate(units_data):
            lessons_data = unit_data.pop('lessons', [])
            unit = CourseUnit.objects.create(course=course, **unit_data)

            for l_idx, lesson_data in enumerate(lessons_data):
                video_key = lesson_data.get('video')
                presentation_key = lesson_data.get('presentation')

                if video_key:
                    lesson_data['video'] = files.get(video_key)

                if presentation_key:
                    lesson_data['presentation'] = files.get(presentation_key)

                Lessons.objects.create(course_unit=unit, **lesson_data)

        return course


class CourseUpdateSerializer(serializers.ModelSerializer):
    units = CourseUnitUpdateSerializer(many=True)

    class Meta:
        model = Course
        fields = ["title", "desc", "base_price", "discount_price", "units"]


    def update(self, instance, validated_data):
        units_data = validated_data.pop("units", None)

        instance = super().update(instance, validated_data)

        if units_data is not None:
            instance.units.all().delete()

            for unit_data in units_data:
                lessons_data = unit_data.pop("lessons", [])
                unit = CourseUnit.objects.create(course=instance, **unit_data)

                for lesson_data in lessons_data:
                    Lessons.objects.create(course_unit=unit, **lesson_data)

        return instance
