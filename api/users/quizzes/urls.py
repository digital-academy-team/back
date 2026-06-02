from rest_framework.routers import DefaultRouter

from api.users.quizzes.views import QuizViewSet

router = DefaultRouter()


router.register("", QuizViewSet, basename="quiz")

urlpatterns = router.urls