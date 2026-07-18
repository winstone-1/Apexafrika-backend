from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LegalDocumentViewSet, UserConsentView, CookieConsentView, AcceptTermsView

router = DefaultRouter()
router.register(r'documents', LegalDocumentViewSet, basename='legal-document')

app_name = 'legal'

urlpatterns = [
    path('', include(router.urls)),
    path('consent/', UserConsentView.as_view(), name='user-consent'),
    path('cookie-consent/', CookieConsentView.as_view(), name='cookie-consent'),
    path('accept-terms/', AcceptTermsView.as_view(), name='accept-terms'),
]
