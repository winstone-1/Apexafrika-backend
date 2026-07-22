import uuid

from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import (NewsletterCampaign, NewsletterSubscription)
from .serializers import (NewsletterCampaignSerializer,
                          NewsletterSubscriptionSerializer)


class NewsletterSubscriptionViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.AllowAny]
    serializer_class = NewsletterSubscriptionSerializer
    queryset = NewsletterSubscription.objects.filter(status="ACTIVE")

    def perform_create(self, serializer):
        token = str(uuid.uuid4())
        serializer.save(
            confirmation_token=token,
            user=self.request.user if self.request.user.is_authenticated else None,
        )

    @action(detail=False, methods=["post"])
    def confirm(self, request):
        token = request.data.get("token")
        if not token:
            return Response(
                {"error": "Token is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            subscription = NewsletterSubscription.objects.get(
                confirmation_token=token, status="PENDING"
            )
            subscription.status = "ACTIVE"
            subscription.confirmed_at = timezone.now()
            subscription.save()
            return Response({"message": "Subscription confirmed!"})
        except NewsletterSubscription.DoesNotExist:
            return Response(
                {"error": "Invalid or expired token"}, status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=["post"])
    def unsubscribe(self, request):
        email = request.data.get("email")
        if not email:
            return Response(
                {"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            subscription = NewsletterSubscription.objects.get(email=email)
            subscription.status = "UNSUBSCRIBED"
            subscription.unsubscribed_at = timezone.now()
            subscription.save()
            return Response({"message": "Unsubscribed successfully"})
        except NewsletterSubscription.DoesNotExist:
            return Response(
                {"error": "Email not found"}, status=status.HTTP_404_NOT_FOUND
            )


class NewsletterCampaignViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = NewsletterCampaignSerializer
    queryset = NewsletterCampaign.objects.all()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=["post"])
    def send(self, request, pk=None):
        campaign = self.get_object()

        if campaign.status not in ["DRAFT", "SCHEDULED"]:
            return Response(
                {"error": "Campaign cannot be sent"}, status=status.HTTP_400_BAD_REQUEST
            )

        subscribers = NewsletterSubscription.objects.filter(status="ACTIVE")
        campaign.status = "SENDING"
        campaign.save()

        # Send emails (simplified)
        sent_count = 0
        for subscriber in subscribers:
            try:
                # In production, use proper email sending with tracking
                send_mail(
                    campaign.subject,
                    campaign.content,
                    settings.DEFAULT_FROM_EMAIL,
                    [subscriber.email],
                    fail_silently=True,
                )
                sent_count += 1
            except BaseException:
                pass

        campaign.sent_count = sent_count
        campaign.status = "SENT"
        campaign.sent_at = timezone.now()
        campaign.save()

        return Response(
            {
                "message": f"Campaign sent to {sent_count} subscribers",
                "sent_count": sent_count,
            }
        )
