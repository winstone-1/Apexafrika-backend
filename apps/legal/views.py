from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.shortcuts import get_object_or_404
from .models import LegalDocument, UserConsent, CookieConsent
from .serializers import (
    LegalDocumentSerializer, UserConsentSerializer, CookieConsentSerializer
)
import uuid

class LegalDocumentViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.AllowAny]
    serializer_class = LegalDocumentSerializer
    queryset = LegalDocument.objects.filter(is_active=True)
    filterset_fields = ['type', 'language']

class UserConsentView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserConsentSerializer
    
    def perform_create(self, serializer):
        document_id = self.request.data.get('document_id')
        document = get_object_or_404(LegalDocument, id=document_id, is_active=True)
        
        existing = UserConsent.objects.filter(
            user=self.request.user,
            document=document
        ).first()
        
        if existing:
            existing.is_active = True
            existing.consented_at = timezone.now()
            existing.save()
            serializer.instance = existing
            return
        
        serializer.save(
            user=self.request.user,
            document=document,
            consent_type=document.type,
            ip_address=self.request.META.get('REMOTE_ADDR'),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )

class CookieConsentView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = CookieConsentSerializer
    
    def perform_create(self, serializer):
        consent_id = str(uuid.uuid4())
        serializer.save(
            consent_id=consent_id,
            ip_address=self.request.META.get('REMOTE_ADDR'),
            user=self.request.user if self.request.user.is_authenticated else None
        )

class AcceptTermsView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        terms_id = request.data.get('terms_id')
        privacy_id = request.data.get('privacy_id')
        
        if not terms_id or not privacy_id:
            return Response(
                {'error': 'Both terms_id and privacy_id are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        terms = get_object_or_404(LegalDocument, id=terms_id, type='TERMS', is_active=True)
        privacy = get_object_or_404(LegalDocument, id=privacy_id, type='PRIVACY', is_active=True)
        
        UserConsent.objects.update_or_create(
            user=request.user,
            document=terms,
            defaults={
                'consent_type': 'TERMS',
                'is_active': True,
                'ip_address': request.META.get('REMOTE_ADDR'),
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                'consented_at': timezone.now()
            }
        )
        
        UserConsent.objects.update_or_create(
            user=request.user,
            document=privacy,
            defaults={
                'consent_type': 'PRIVACY',
                'is_active': True,
                'ip_address': request.META.get('REMOTE_ADDR'),
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                'consented_at': timezone.now()
            }
        )
        
        return Response({
            'message': 'Terms and Privacy accepted successfully',
            'user': request.user.username,
            'accepted_at': timezone.now()
        })
