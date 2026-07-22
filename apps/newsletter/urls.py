from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import NewsletterCampaignViewSet, NewsletterSubscriptionViewSet

router = DefaultRouter()
router.register(
    r"subscriptions", NewsletterSubscriptionViewSet, basename="newsletter-subscription"
)
router.register(
    r"campaigns",
    NewsletterCampaignViewSet,
    basename="newsletter-campaign")

app_name = "newsletter"

urlpatterns = [
    path("", include(router.urls)),
]
