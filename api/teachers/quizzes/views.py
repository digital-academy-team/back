from django.db.models import Count
from rest_framework import viewsets

from apps.quiz.models.quiz import Quiz
from common.serializers.quiz.serializer import QuizCreateSerializer, QuizUpdateSerializer, QuizListSerializer, \
    QuizDetailSerializer


class QuizViewSet(viewsets.ModelViewSet):
    queryset = Quiz.objects.select_related('lesson').annotate(questions_count=Count("questions"))
    http_method_names = ['get', 'post', 'patch', 'delete']


    def get_serializer_class(self):
        if self.action == 'create':
            return QuizCreateSerializer

        elif self.action == 'retrieve':
            return QuizDetailSerializer

        elif self.action in ['update', 'partial_update']:
            return QuizUpdateSerializer

        return QuizListSerializer



    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user)



