from rest_framework import viewsets
from apps.leaderboard.models import Leaderboard
from common.serializers.leaderboard.serializer import LeaderboardSerializer


class LeaderBoardReadOnlyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Leaderboard.objects.select_related("user").order_by("position")
    serializer_class = LeaderboardSerializer


