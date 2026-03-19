from rest_framework.routers import DefaultRouter

from api.users.enrolment.views import EnrolmentViewSet

router = DefaultRouter()



router.register("", EnrolmentViewSet, basename="enrolment")

urlpatterns = router.urls

