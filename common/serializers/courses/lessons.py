import json

from rest_framework import serializers

from apps.course.models.lessons import Lessons
from common.serializers.quiz.serializer import QuizDetailSerializer


LESSON_FIELDS = [
    "id",
    "course_unit",
    "order",
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
]


def _strip_exercise_solution(exercise):
    """Remove the reference solution from an exercise JSON blob.

    Students must hit `POST /api/users/exercise/<lesson_id>/solution/`
    to see the solution — sending it inline lets anyone pull it from
    DevTools without ever clicking "Reveal".
    """
    if not isinstance(exercise, dict):
        return exercise
    clean = dict(exercise)
    if 'solution' in clean:
        clean['solution'] = ''
        clean['has_solution'] = bool(exercise.get('solution'))
    return clean


class LessonsSerializer(serializers.ModelSerializer):
    # Tutor-side: include the attached quiz so the lesson editor can pre-fill
    # the "follow-up quiz" toggle + inline editor when editing an existing
    # lesson (instead of silently dropping it and creating a duplicate).
    quizzes = QuizDetailSerializer(many=True, read_only=True)

    class Meta:
        model = Lessons
        fields = LESSON_FIELDS + ["quizzes"]
        read_only_fields = ["course_unit"]


class StudentLessonsSerializer(serializers.ModelSerializer):

    quizzes = QuizDetailSerializer(many=True, read_only=True)

    class Meta:
        model = Lessons
        fields = LESSON_FIELDS + ["quizzes"]
        read_only_fields = ["course_unit"]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['exercise'] = _strip_exercise_solution(data.get('exercise'))
        return data


DEFAULT_HINT_PENALTY_PERCENT = 5


def _normalize_hint(raw, fallback_penalty):
    """Accept either a legacy string hint or the new {text, penalty_percent} dict."""
    if isinstance(raw, str):
        text = raw.strip()
        if not text:
            return None
        return {"text": text, "penalty_percent": fallback_penalty}

    if isinstance(raw, dict):
        text = str(raw.get("text") or "").strip()
        if not text:
            return None
        try:
            penalty = int(raw.get("penalty_percent", fallback_penalty))
        except (TypeError, ValueError):
            penalty = fallback_penalty
        return {"text": text, "penalty_percent": max(0, min(100, penalty))}

    return None


class BaseLessonSerializer(serializers.ModelSerializer):
    def validate_exercise(self, value):
        if value in ("", None):
            return None

        if isinstance(value, str):
            try:
                value = json.loads(value)
            except json.JSONDecodeError as exc:
                raise serializers.ValidationError("Exercise must be valid JSON.") from exc

        if not isinstance(value, dict):
            raise serializers.ValidationError("Exercise must be an object.")

        hints_raw = value.get("hints", [])
        if hints_raw in ("", None):
            hints_raw = []
        if not isinstance(hints_raw, list):
            raise serializers.ValidationError("Exercise hints must be a list.")

        # Per-exercise default — kept for backwards compatibility with the
        # previous "one penalty for all hints" shape. The new model is
        # per-hint penalties, but if a hint comes in as a bare string we
        # apply this value.
        try:
            fallback_penalty = int(
                value.get("hint_penalty_percent")
                if value.get("hint_penalty_percent") is not None
                else DEFAULT_HINT_PENALTY_PERCENT
            )
        except (TypeError, ValueError):
            fallback_penalty = DEFAULT_HINT_PENALTY_PERCENT
        fallback_penalty = max(0, min(100, fallback_penalty))

        normalized_hints = []
        for hint in hints_raw:
            normalized = _normalize_hint(hint, fallback_penalty)
            if normalized:
                normalized_hints.append(normalized)

        return {
            "language": str(value.get("language") or "javascript"),
            "starter_code": str(value.get("starter_code") or ""),
            "solution": value.get("solution") or "",
            "hint_penalty_percent": fallback_penalty,
            "hints": normalized_hints,
        }


    def validate_captions(self, value):
        if not value:
            return value
        allowed_extensions = [".vtt", ".srt"]
        file_name = value.name.lower()
        if not any(file_name.endswith(ext) for ext in allowed_extensions):
            raise serializers.ValidationError("Captions file must be .vtt or .srt.")
        return value

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
        fields = LESSON_FIELDS




class LessonUpdateSerializer(BaseLessonSerializer):

    presentation = serializers.FileField(required=False)
    video = serializers.FileField(required=False)

    class Meta:
        model = Lessons
        fields = LESSON_FIELDS
