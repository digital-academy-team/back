# apps/quiz/views.py

from django.db.models import Count
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.quiz.models.quiz import Quiz
from apps.quiz.models import QuizResult
from apps.quiz.services.quiz_result import submit_quiz
from common.serializers.quiz.serializer import QuizListSerializer, QuizDetailSerializer, QuizSubmitSerializer


class QuizViewSet(mixins.ListModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.CreateModelMixin,
                  viewsets.GenericViewSet):

    queryset = Quiz.objects.select_related('lesson').annotate(questions_count=Count("questions"))
    http_method_names = ['get', 'post']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return QuizDetailSerializer
        elif self.action == 'submit':
            return QuizSubmitSerializer
        return QuizListSerializer

    @action(detail=True, methods=["post"], url_path="submit")
    def submit(self, request, pk=None):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        quiz = self.get_object()
        answers = []

        for item in serializer.validated_data["answers"]:
            question = quiz.questions.get(id=item["question"])
            variant = question.variants.get(id=item["variant"])
            answers.append({
                "question": question,
                "variant": variant
            })

        result = submit_quiz(user=request.user, quiz=quiz, answers=answers)

        return Response({
            "quiz": str(result.quiz.id),
            "user": result.user.username,
            "correct_answers": result.correct_answers,
            "wrong_answers": result.wrong_answers,
            "total_questions": result.total_questions,
            "total": str(result.total),
            "status": result.status,
            "course_progress": result.course_progress,
        }, status=status.HTTP_200_OK)