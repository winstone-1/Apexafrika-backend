from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/auth/', include('apps.users.urls')),
    path('api/v1/tournaments/', include('apps.tournaments.urls')),
    path('api/v1/players/', include('apps.players.urls')),
    path('api/v1/analytics/', include('apps.analytics.urls')),
    path('api/v1/community/', include('apps.community.urls')),
    path('api/v1/payments/', include('apps.payments.urls')),
    path('api/v1/notifications/', include('apps.notifications.urls')),
    path('api/v1/chat/', include('apps.chat.urls')),
    path('api/v1/ai/', include('apps.ai.urls')),
    path('api/v1/teams/', include('apps.teams.urls')),
    path('api/v1/sponsors/', include('apps.sponsors.urls')),
    path('api/v1/achievements/', include('apps.achievements.urls')),
    path('api/v1/schedules/', include('apps.schedules.urls')),
    path('api/v1/streaming/', include('apps.streaming.urls')),
    path('api/v1/content/', include('apps.content.urls')),
    path('api/v1/newsletter/', include('apps.newsletter.urls')),
    path('api/v1/feedback/', include('apps.feedback.urls')),
    path('api/v1/audit/', include('apps.audit.urls')),
    path('api/v1/legal/', include('apps.legal.urls')),
    path('health/', include('apps.health.urls')),
    
    # API Schema and Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(
        template_name='swagger-ui.html',
        url_name='schema'
    ), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
