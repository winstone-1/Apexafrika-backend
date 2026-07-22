from rest_framework import serializers

from .models import AuditLog, SystemLog


class AuditLogSerializer(serializers.ModelSerializer):
    user_details = serializers.StringRelatedField(source="user.username")

    class Meta:
        model = AuditLog
        fields = "__all__"
        read_only_fields = ("created_at",)


class SystemLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemLog
        fields = "__all__"
        read_only_fields = ("created_at",)
