from rest_framework import routers

from api.users.quiz_result.views import QuizResultReadOnlyViewSet

router = routers.DefaultRouter()


router.register("", QuizResultReadOnlyViewSet, basename='quiz-result')

urlpatterns = router.urls
