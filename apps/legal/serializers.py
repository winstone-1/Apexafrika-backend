from rest_framework import serializers

from .models import CookieConsent, LegalDocument, UserConsent


class LegalDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = LegalDocument
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at")


class UserConsentSerializer(serializers.ModelSerializer):
    document_details = LegalDocumentSerializer(
        source="document", read_only=True)

    class Meta:
        model = UserConsent
        fields = "__all__"
        read_only_fields = ("user", "consented_at", "ip_address", "user_agent")


class CookieConsentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CookieConsent
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at")
