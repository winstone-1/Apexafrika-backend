from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AchievementViewSet, UserAchievementViewSet

router = DefaultRouter()
router.register(r"all", AchievementViewSet, basename="achievement")
router.register(r"user", UserAchievementViewSet, basename="user-achievement")

app_name = "achievements"

urlpatterns = [
    path("", include(router.urls)),
]
