from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NewsletterSubscriptionViewSet, NewsletterCampaignViewSet

router = DefaultRouter()
router.register(r'subscriptions', NewsletterSubscriptionViewSet, basename='newsletter-subscription')
router.register(r'campaigns', NewsletterCampaignViewSet, basename='newsletter-campaign')

app_name = 'newsletter'

urlpatterns = [
    path('', include(router.urls)),
]
