from rest_framework import routers

from api.users.course_student.views import CourseStudentViewSet

router = routers.DefaultRouter()


router.register("", CourseStudentViewSet, basename="courses_user")
urlpatterns = router.urls