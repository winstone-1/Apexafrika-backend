from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StreamViewSet, StreamChatViewSet, StreamAnalyticsViewSet

router = DefaultRouter()
router.register(r'streams', StreamViewSet, basename='stream')
router.register(r'chats', StreamChatViewSet, basename='stream-chat')
router.register(r'analytics', StreamAnalyticsViewSet, basename='stream-analytics')

app_name = 'streaming'

urlpatterns = [
    path('', include(router.urls)),
]
