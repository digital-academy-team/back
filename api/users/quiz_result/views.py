from rest_framework import viewsets

from apps.quiz.models import QuizResult
from common.serializers.quiz_result.serializer import QuizResultSerializer


class QuizResultReadOnlyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = QuizResult.objects.all()
    serializer_class = QuizResultSerializer

