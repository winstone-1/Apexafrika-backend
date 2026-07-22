from rest_framework import serializers

from .models import Notification, NotificationPreference


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = "__all__"
        read_only_fields = (
            "created_at",
            "is_read",
            "is_sent",
            "sent_at",
            "read_at")


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationPreference
        fields = "__all__"
        read_only_fields = ("user", "updated_at")
