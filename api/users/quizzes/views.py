from django.db.models import Count
from django.template.context_processors import request
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from apps.course.models.student import CourseStudent
from apps.quiz.models import QuizResult
from apps.quiz.models.quiz import Quiz
from apps.quiz.services.quiz_result import submit_quiz
from common.serializers.quiz.serializer import QuizListSerializer, \
    QuizDetailSerializer, QuizSubmitSerializer


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
            try:
                question = quiz.questions.get(id=item["question"])
            except quiz.questions.model.DoesNotExist:
                raise ValidationError({"question": "Invalid question for this quiz."})

            try:
                variant = question.variants.get(id=item["variant"])
            except question.variants.model.DoesNotExist:
                raise ValidationError({"variant": "Invalid variant for this question."})

            answers.append({
                "question": question,
                "variant": variant,
            })

        result = submit_quiz(
            user=request.user,
            quiz=quiz,
            answers=answers,
        )

        # 🔥 COURSE PROGRESS LOGIC
        course = quiz.lesson.course_unit.course

        course_student = CourseStudent.objects.filter(
            user=request.user,
            course=course
        ).first()

        if course_student:
            # jami quizlar
            total_quizzes = Quiz.objects.filter(
                lesson__unit__course=course
            ).count()

            # user yechgan quizlar (Result modelga qarab o‘zgartir)
            completed_quizzes = QuizResult.objects.filter(
                user=request.user,
                quiz__lesson__unit__course=course
            ).values('quiz').distinct().count()

            if total_quizzes > 0:
                progress = (completed_quizzes / total_quizzes) * 100
            else:
                progress = 0

            course_student.progress = progress
            course_student.save()

        return Response(
            {
                "quiz": str(result.quiz.id),
                "user": result.user.username,
                "correct_answers": result.correct_answers,
                "wrong_answers": result.wrong_answers,
                "total_questions": result.total_questions,
                "total": str(result.total),
                "status": result.status,
            },
            status=status.HTTP_200_OK,
        )
