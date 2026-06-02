from rest_framework.routers import DefaultRouter

from api.users.courses.views import CourseViewSet

router = DefaultRouter()


router.register('', CourseViewSet, basename='course_users')


urlpatterns = router.urls

