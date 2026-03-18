from rest_framework import routers

from api.teachers.lessons.views import LessonViewSet

router = routers.DefaultRouter()



router.register("", LessonViewSet, basename="lessons_teacher")


urlpatterns = router.urls
