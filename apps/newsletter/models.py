from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class NewsletterSubscription(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        UNSUBSCRIBED = "UNSUBSCRIBED", "Unsubscribed"
        BOUNCED = "BOUNCED", "Bounced"
        PENDING = "PENDING", "Pending Confirmation"

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="newsletter_subscriptions",
    )
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255, blank=True, null=True)

    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )
    preferences = models.JSONField(default=dict)

    confirmation_token = models.CharField(
        max_length=100, blank=True, null=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    unsubscribed_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.email} - {self.status}"


class NewsletterCampaign(models.Model):
    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        SCHEDULED = "SCHEDULED", "Scheduled"
        SENDING = "SENDING", "Sending"
        SENT = "SENT", "Sent"
        FAILED = "FAILED", "Failed"

    subject = models.CharField(max_length=255)
    content = models.TextField()
    html_content = models.TextField(blank=True, null=True)

    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.DRAFT
    )

    target_audience = models.JSONField(default=dict)

    sent_count = models.IntegerField(default=0)
    opened_count = models.IntegerField(default=0)
    clicked_count = models.IntegerField(default=0)
    bounced_count = models.IntegerField(default=0)
    unsubscribed_count = models.IntegerField(default=0)

    scheduled_for = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)

    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="created_campaigns"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.subject} - {self.status}"


class NewsletterOpen(models.Model):
    campaign = models.ForeignKey(
        NewsletterCampaign, on_delete=models.CASCADE, related_name="opens"
    )
    subscription = models.ForeignKey(
        NewsletterSubscription, on_delete=models.CASCADE, related_name="opens"
    )

    opened_at = models.DateTimeField(auto_now_add=True)
    user_agent = models.TextField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        unique_together = ["campaign", "subscription"]

    def __str__(self):
        return f"{self.subscription.email} - {self.campaign.subject}"


class NewsletterClick(models.Model):
    campaign = models.ForeignKey(
        NewsletterCampaign, on_delete=models.CASCADE, related_name="clicks"
    )
    subscription = models.ForeignKey(
        NewsletterSubscription, on_delete=models.CASCADE, related_name="clicks"
    )

    url = models.URLField()
    clicked_at = models.DateTimeField(auto_now_add=True)
    user_agent = models.TextField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    def __str__(self):
        return f"{self.subscription.email} - {self.url}"
