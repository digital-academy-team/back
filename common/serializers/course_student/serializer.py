from rest_framework import serializers
from apps.course.models.lessons import Lessons
from apps.course.models.student import CourseStudent, ProgressStatus
from common.serializers.courses.course import StudentCourseListSerializer


def _clamp_progress(value):
    try:
        return max(0, min(100, int(value or 0)))
    except (TypeError, ValueError):
        return 0


def _progress_from_completed_lectures(obj: CourseStudent):
    completed_lectures = obj.completed_lectures if isinstance(obj.completed_lectures, list) else []
    if not completed_lectures:
        return _clamp_progress(obj.progress)

    total_lessons = Lessons.objects.filter(course_unit__course=obj.course).count()
    if total_lessons <= 0:
        return _clamp_progress(obj.progress)

    completed_count = Lessons.objects.filter(
        course_unit__course=obj.course,
        id__in=[str(lesson_id) for lesson_id in completed_lectures],
    ).count()

    return _clamp_progress(round((completed_count / total_lessons) * 100))


def _status_from_progress(progress):
    return ProgressStatus.COMPLETED if progress >= 100 else ProgressStatus.IN_PROGRESS


class CourseStudentSerializer(serializers.ModelSerializer):

    class Meta:
        model = CourseStudent
        fields = ["id", "course", "progress", "completed_lectures", "status", "certificate_pdf"]

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        if "completed_lectures" in validated_data:
            instance.progress = _progress_from_completed_lectures(instance)
            instance.status = _status_from_progress(instance.progress)
            instance.save(update_fields=["progress", "status"])
        return instance

    def to_representation(self, instance):
        data = super().to_representation(instance)
        progress = _progress_from_completed_lectures(instance)
        data["progress"] = progress
        data["status"] = _status_from_progress(progress)
        return data




class CourseStudentDetailSerializer(serializers.ModelSerializer):

    course = StudentCourseListSerializer(read_only=True)

    class Meta:
        model = CourseStudent
        fields = ["id", "course", "progress", "completed_lectures", "status"]

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        if "completed_lectures" in validated_data:
            instance.progress = _progress_from_completed_lectures(instance)
            instance.status = _status_from_progress(instance.progress)
            instance.save(update_fields=["progress", "status"])
        return instance

    def to_representation(self, instance):
        data = super().to_representation(instance)
        progress = _progress_from_completed_lectures(instance)
        data["progress"] = progress
        data["status"] = _status_from_progress(progress)
        return data
