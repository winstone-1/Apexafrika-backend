from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AIConversationViewSet, AIPredictionViewSet

router = DefaultRouter()
router.register(r'conversations', AIConversationViewSet, basename='ai-conversation')
router.register(r'predictions', AIPredictionViewSet, basename='ai-prediction')

app_name = 'ai'

urlpatterns = [
    path('', include(router.urls)),
]
