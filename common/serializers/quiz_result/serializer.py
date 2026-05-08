from rest_framework import serializers

from apps.quiz.models import QuizResult


class QuizResultSerializer(serializers.ModelSerializer):

    quiz_title = serializers.CharField(source="quiz.title", read_only=True)
    class Meta:
        model = QuizResult
        fields = ["id",
                  "quiz_title",
                  "correct_answers",
                  "wrong_answers",
                  "total_questions",
                  "status",
                  "stars",
                  "total",
                  "attempt",
                  ]