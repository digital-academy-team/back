from rest_framework import routers

from api.users.leaderboard.views import LeaderBoardReadOnlyViewSet

router = routers.DefaultRouter()



router.register("", LeaderBoardReadOnlyViewSet, basename='leaderboard')


urlpatterns = router.urls