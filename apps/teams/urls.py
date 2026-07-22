from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import TeamViewSet

router = DefaultRouter()
router.register(r"", TeamViewSet, basename="team")

app_name = "teams"

urlpatterns = [
    path("", include(router.urls)),
]
