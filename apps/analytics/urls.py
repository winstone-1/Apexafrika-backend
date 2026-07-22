from django.urls import path

from .views import platform_analytics, tournament_analytics

app_name = "analytics"

urlpatterns = [
    path("platform/", platform_analytics, name="platform-analytics"),
    path(
        "tournament/<int:tournament_id>/",
        tournament_analytics,
        name="tournament-analytics",
    ),
]
