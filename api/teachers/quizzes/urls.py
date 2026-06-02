from rest_framework.routers import DefaultRouter

from api.teachers.quizzes.views import QuizViewSet

router = DefaultRouter()


router.register("", QuizViewSet, basename="quiz_teachers")

urlpatterns = router.urls