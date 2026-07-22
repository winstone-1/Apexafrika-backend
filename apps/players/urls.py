from django.urls import path

from .views import (LeaderboardView, MatchHistoryView, PlayerStatsView,
                    get_player_stats_detail)

app_name = "players"

urlpatterns = [
    path("stats/", PlayerStatsView.as_view(), name="player-stats"),
    path("leaderboard/", LeaderboardView.as_view(), name="leaderboard"),
    path("history/", MatchHistoryView.as_view(), name="match-history"),
    path(
        "stats/<int:user_id>/",
        get_player_stats_detail,
        name="player-stats-detail"),
]
