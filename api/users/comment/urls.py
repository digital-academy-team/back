from rest_framework import routers

from api.users.comment.views import CommentViewSet

router = routers.DefaultRouter()

router.register('', CommentViewSet, basename='comment')


urlpatterns = router.urls