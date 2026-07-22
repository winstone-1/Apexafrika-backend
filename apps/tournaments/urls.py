from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import TournamentViewSet

router = DefaultRouter()
router.register(r"", TournamentViewSet, basename="tournament")

app_name = "tournaments"

urlpatterns = [
    path("", include(router.urls)),
]
