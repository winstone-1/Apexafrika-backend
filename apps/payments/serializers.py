from rest_framework import serializers

from apps.users.serializers import UserSerializer

from .models import PaymentMethod, PaystackTransaction


class PaystackTransactionSerializer(serializers.ModelSerializer):
    user_details = UserSerializer(source="user", read_only=True)

    class Meta:
        model = PaystackTransaction
        fields = "__all__"
        read_only_fields = (
            "reference",
            "transaction_id",
            "authorization_code",
            "status",
            "gateway_response",
            "payment_data",
            "result_code",
            "result_description",
            "created_at",
            "completed_at",
        )


class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = "__all__"
        read_only_fields = ("created_at",)
