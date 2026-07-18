from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AuditLogViewSet, SystemLogViewSet

router = DefaultRouter()
router.register(r'logs', AuditLogViewSet, basename='audit-log')
router.register(r'system', SystemLogViewSet, basename='system-log')

app_name = 'audit'

urlpatterns = [
    path('', include(router.urls)),
]
