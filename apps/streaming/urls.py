from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import StreamAnalyticsViewSet, StreamChatViewSet, StreamViewSet

router = DefaultRouter()
router.register(r"streams", StreamViewSet, basename="stream")
router.register(r"chats", StreamChatViewSet, basename="stream-chat")
router.register(
    r"analytics",
    StreamAnalyticsViewSet,
    basename="stream-analytics")

app_name = "streaming"

urlpatterns = [
    path("", include(router.urls)),
]
