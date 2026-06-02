from rest_framework import routers

from api.users.category.views import CategoryViewSet

router = routers.DefaultRouter()

router.register("", CategoryViewSet, basename="category")


urlpatterns = router.urls
