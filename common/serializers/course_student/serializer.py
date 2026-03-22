from rest_framework import serializers
from apps.course.models.student import CourseStudent
from common.serializers.courses.course import StudentCourseListSerializer


class CourseStudentSerializer(serializers.ModelSerializer):

    class Meta:
        model = CourseStudent
        fields = ["id", "course",  "progress", "status", "certificate_pdf"]




class CourseStudentDetailSerializer(serializers.ModelSerializer):

    course = StudentCourseListSerializer(read_only=True)

    class Meta:
        model = CourseStudent
        fields = ["id", "course", "progress", "status"]

