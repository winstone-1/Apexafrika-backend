from rest_framework import serializers
from .models import MPesaTransaction, PaymentMethod
from apps.users.serializers import UserSerializer

class MPesaTransactionSerializer(serializers.ModelSerializer):
    user_details = UserSerializer(source='user', read_only=True)
    
    class Meta:
        model = MPesaTransaction
        fields = '__all__'
        read_only_fields = ('transaction_id', 'checkout_request_id', 'merchant_request_id', 
                           'status', 'mpesa_response', 'result_code', 'result_description', 
                           'created_at', 'completed_at')

class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = '__all__'
        read_only_fields = ('created_at',)
