from rest_framework import routers

from api.teachers.courses.views import CourseViewSet

router = routers.DefaultRouter()

router.register('', CourseViewSet, basename='courses')


urlpatterns = router.urls
