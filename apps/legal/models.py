from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class LegalDocument(models.Model):
    class Type(models.TextChoices):
        TERMS = "TERMS", "Terms of Service"
        PRIVACY = "PRIVACY", "Privacy Policy"
        COOKIE = "COOKIE", "Cookie Policy"
        COMMUNITY = "COMMUNITY", "Community Guidelines"
        GDPR = "GDPR", "GDPR Compliance"
        CCPA = "CCPA", "CCPA Compliance"

    class Language(models.TextChoices):
        ENGLISH = "en", "English"
        SWAHILI = "sw", "Swahili"
        FRENCH = "fr", "French"
        ARABIC = "ar", "Arabic"

    type = models.CharField(max_length=20, choices=Type.choices)
    language = models.CharField(
        max_length=10, choices=Language.choices, default=Language.ENGLISH
    )
    version = models.CharField(max_length=20)

    title = models.CharField(max_length=255)
    content = models.TextField()
    summary = models.TextField(blank=True, null=True)

    is_active = models.BooleanField(default=True)
    is_required = models.BooleanField(default=True)

    effective_date = models.DateTimeField()
    expiry_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-effective_date"]
        unique_together = ["type", "language", "version"]

    def __str__(self):
        return f"{self.type} - {self.language} - v{self.version}"


class UserConsent(models.Model):
    class ConsentType(models.TextChoices):
        TERMS = "TERMS", "Terms of Service"
        PRIVACY = "PRIVACY", "Privacy Policy"
        COOKIE = "COOKIE", "Cookie Policy"
        MARKETING = "MARKETING", "Marketing"
        DATA_PROCESSING = "DATA_PROCESSING", "Data Processing"
        COMMUNITY = "COMMUNITY", "Community Guidelines"

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="consents")
    document = models.ForeignKey(
        LegalDocument, on_delete=models.CASCADE, related_name="consents"
    )
    consent_type = models.CharField(max_length=20, choices=ConsentType.choices)

    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)

    consented_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-consented_at"]
        unique_together = ["user", "document"]

    def __str__(self):
        return f"{self.user.username} - {self.consent_type} - {self.consented_at}"


class CookieConsent(models.Model):
    class CookieType(models.TextChoices):
        ESSENTIAL = "ESSENTIAL", "Essential"
        ANALYTICS = "ANALYTICS", "Analytics"
        MARKETING = "MARKETING", "Marketing"
        PREFERENCE = "PREFERENCE", "Preference"

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="cookie_consents",
    )
    cookie_type = models.CharField(max_length=20, choices=CookieType.choices)
    consent_given = models.BooleanField(default=False)
    consent_id = models.CharField(max_length=100, unique=True)

    ip_address = models.GenericIPAddressField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.cookie_type} - {self.consent_given} - {self.consent_id}"
