import json

from django.db import transaction
from django.db.models.functions import Coalesce
from django.db.models import Avg, Count, Value
from rest_framework import serializers
from apps.course.models.course import Course
from apps.course.models.lessons import Lessons
from apps.course.models.units import CourseUnit
from apps.quiz.models.questions import Questions
from apps.quiz.models.quiz import Quiz
from apps.quiz.models.variants import Variant
from common.serializers.comments.serializers import CommentSerializer
from common.serializers.courses.lessons import DEFAULT_HINT_PENALTY_PERCENT, _normalize_hint
from common.serializers.courses.units import CourseUnitUpdateSerializer, \
    CourseUnitListSerializer, StudentCourseUnitListSerializer


LESSON_WRITABLE_FIELDS = {
    "kind",
    "title",
    "desc",
    "content_md",
    "duration_min",
    "video",
    "captions",
    "presentation",
    "additional_task",
    "external_url",
    "assignment_instructions",
    "assignment_due_at",
    "allow_multiple_files",
    "exercise",
}


def _normalize_exercise_hints(exercise):
    """Convert legacy string hints into {text, penalty_percent} dicts.

    Mirrors ``BaseLessonSerializer.validate_exercise`` so the nested
    course-create path stores the same dict-shaped hints as the
    single-lesson path.
    """
    if not isinstance(exercise, dict):
        return exercise

    hints_raw = exercise.get("hints", [])
    if hints_raw in ("", None):
        hints_raw = []
    if not isinstance(hints_raw, list):
        return exercise

    try:
        fallback_penalty = int(
            exercise.get("hint_penalty_percent")
            if exercise.get("hint_penalty_percent") is not None
            else DEFAULT_HINT_PENALTY_PERCENT
        )
    except (TypeError, ValueError):
        fallback_penalty = DEFAULT_HINT_PENALTY_PERCENT
    fallback_penalty = max(0, min(100, fallback_penalty))

    exercise["hints"] = [
        normalized
        for hint in hints_raw
        if (normalized := _normalize_hint(hint, fallback_penalty))
    ]
    return exercise


def normalize_lesson_payload(lesson_data):
    normalized = {key: value for key, value in lesson_data.items() if key in LESSON_WRITABLE_FIELDS}

    if normalized.get("assignment_due_at") == "":
        normalized["assignment_due_at"] = None

    if normalized.get("exercise") in ("", None):
        normalized["exercise"] = None
    elif isinstance(normalized.get("exercise"), str):
        normalized["exercise"] = json.loads(normalized["exercise"])

    if isinstance(normalized.get("exercise"), dict):
        normalized["exercise"] = _normalize_exercise_hints(normalized["exercise"])

    if not normalized.get("kind"):
        normalized["kind"] = "VIDEO"

    return normalized


def create_attached_quiz(*, lesson, teacher, quiz_data):
    if not quiz_data:
        return None

    questions_data = quiz_data.get("questions") or []
    try:
        time_limit_min = max(0, int(quiz_data.get("time_limit_min") or 0))
    except (TypeError, ValueError):
        time_limit_min = 0

    show_timer = quiz_data.get("show_timer", True)
    if isinstance(show_timer, str):
        show_timer = show_timer.strip().lower() not in {"0", "false", "no", "off"}

    quiz = Quiz.objects.create(
        lesson=lesson,
        teacher=teacher,
        title=quiz_data.get("title") or f"{lesson.title} quiz",
        description=quiz_data.get("description") or "",
        time_limit_min=time_limit_min,
        show_timer=bool(show_timer),
    )

    for question_data in questions_data:
        variants_data = question_data.get("variants") or []
        question = Questions.objects.create(
            quiz=quiz,
            question_text=question_data.get("question_text") or "",
            points=question_data.get("points") or 1,
        )
        for variant_data in variants_data:
            Variant.objects.create(
                question=question,
                text=variant_data.get("text") or "",
                is_correct=bool(variant_data.get("is_correct")),
            )

    return quiz


class CourseUserListSerializer(serializers.ModelSerializer):
    avg_rating = serializers.FloatField(read_only=True)
    students_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Course
        fields = [
            "id",
            "cover_img",
            "title",
            "desc",
            "base_price",
            "discount_price",
            "slug",
            "avg_rating",
            "students_count",
        ]


class CourseDetailSerializer(serializers.ModelSerializer):
    units = CourseUnitListSerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    similar_courses = serializers.SerializerMethodField()

    avg_rating = serializers.FloatField(read_only=True)
    comments_count = serializers.IntegerField(read_only=True)
    students_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Course
        fields = [
            "id",
            "title",
            "cover_img",
            "desc",
            "base_price",
            "discount_price",
            "units",
            "slug",
            "similar_courses",
            "comments",
            "avg_rating",
            "comments_count",
            "students_count",
        ]

    def get_similar_courses(self, obj):
        qs = Course.objects.filter(category=obj.category)\
            .exclude(id=obj.id)\
            .annotate(
                avg_rating=Coalesce(Avg("comments__likes"), Value(0.0)),
                students_count=Count("enrollments", distinct=True)
            )[:5]
        return CourseUserListSerializer(qs, many=True).data




class StudentCourseListSerializer(serializers.ModelSerializer):
    units = StudentCourseUnitListSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = ["id", "units"]


class CourseCreateSerializer(serializers.ModelSerializer):
    units = serializers.ListField(write_only=True)
    cover_img = serializers.ImageField(required=False)

    class Meta:
        model = Course
        fields = ['cover_img', 'title', 'desc', 'base_price', 'discount_price', 'units', 'category']


    def create(self, validated_data):
        request = self.context['request']
        files = request.FILES

        units_data = validated_data.pop('units')


        if isinstance(units_data, list):
            units_data = units_data[0]

        if isinstance(units_data, str):
            units_data = json.loads(units_data)

        with transaction.atomic():
            course = Course.objects.create(**validated_data)

            for u_idx, unit_data in enumerate(units_data):
                lessons_data = unit_data.pop('lessons', [])
                unit = CourseUnit.objects.create(course=course, **unit_data)

                for l_idx, lesson_data in enumerate(lessons_data):
                    attached_quiz = lesson_data.pop('attached_quiz', None)
                    video_key = lesson_data.get('video')
                    presentation_key = lesson_data.get('presentation')
                    captions_key = lesson_data.get('captions')

                    if video_key:
                        lesson_data['video'] = files.get(video_key)

                    if presentation_key:
                        lesson_data['presentation'] = files.get(presentation_key)

                    if captions_key:
                        lesson_data['captions'] = files.get(captions_key)

                    lesson = Lessons.objects.create(course_unit=unit, **normalize_lesson_payload(lesson_data))
                    create_attached_quiz(
                        lesson=lesson,
                        teacher=request.user,
                        quiz_data=attached_quiz,
                    )

        return course



class CourseUpdateSerializer(serializers.ModelSerializer):
    units = CourseUnitUpdateSerializer(many=True, required=False)
    cover_img = serializers.ImageField(required=False)

    class Meta:
        model = Course
        fields = ["title", "desc", "base_price", "discount_price", "cover_img", "units"]


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
