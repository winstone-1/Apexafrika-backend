from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.conf import settings
from .models import MPesaTransaction, PaymentMethod
from .serializers import MPesaTransactionSerializer, PaymentMethodSerializer
import requests
import base64
from datetime import datetime

class MPesaPaymentView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = MPesaTransactionSerializer
    
    def perform_create(self, serializer):
        # Get M-Pesa access token
        access_token = self.get_mpesa_access_token()
        
        # Generate timestamp
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        
        # Generate password
        password = base64.b64encode(
            f"{settings.MPESA['SHORTCODE']}{settings.MPESA['PASSKEY']}{timestamp}".encode()
        ).decode()
        
        # Prepare STK push request
        payload = {
            "BusinessShortCode": settings.MPESA['SHORTCODE'],
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": int(serializer.validated_data['amount']),
            "PartyA": serializer.validated_data['phone_number'],
            "PartyB": settings.MPESA['SHORTCODE'],
            "PhoneNumber": serializer.validated_data['phone_number'],
            "CallBackURL": "https://your-domain.com/api/v1/payments/callback/",
            "AccountReference": f"APEX{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "TransactionDesc": "ApexAfrika Payment"
        }
        
        # Send request to M-Pesa
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            f"{settings.MPESA['BASE_URL']}/mpesa/stkpush/v1/processrequest",
            json=payload,
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ResponseCode') == '0':
                serializer.save(
                    user=self.request.user,
                    transaction_id=data.get('CheckoutRequestID'),
                    checkout_request_id=data.get('CheckoutRequestID'),
                    status='PROCESSING'
                )
            else:
                raise serializers.ValidationError(data.get('ResponseDescription', 'M-Pesa request failed'))
        else:
            raise serializers.ValidationError('Failed to connect to M-Pesa')
    
    def get_mpesa_access_token(self):
        url = f"{settings.MPESA['BASE_URL']}/oauth/v1/generate?grant_type=client_credentials"
        
        credentials = base64.b64encode(
            f"{settings.MPESA['CONSUMER_KEY']}:{settings.MPESA['CONSUMER_SECRET']}".encode()
        ).decode()
        
        headers = {
            "Authorization": f"Basic {credentials}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            return response.json().get('access_token')
        raise Exception('Failed to get M-Pesa access token')

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def mpesa_callback(request):
    """Handle M-Pesa callback"""
    data = request.data
    
    # Process callback data
    # Update transaction status based on result
    # This would need to be implemented based on M-Pesa's callback structure
    
    return Response({'message': 'Callback received'}, status=status.HTTP_200_OK)

class PaymentHistoryView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = MPesaTransactionSerializer
    
    def get_queryset(self):
        return MPesaTransaction.objects.filter(user=self.request.user).order_by('-created_at')

class PaymentMethodView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PaymentMethodSerializer
    
    def get_queryset(self):
        return PaymentMethod.objects.filter(user=self.request.user, is_active=True)
    
    def perform_create(self, serializer):
        # If this is the first payment method, make it default
        if not PaymentMethod.objects.filter(user=self.request.user).exists():
            serializer.save(user=self.request.user, is_default=True)
        else:
            serializer.save(user=self.request.user)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def withdraw_prize(request):
    """Withdraw tournament prize money"""
    tournament_id = request.data.get('tournament_id')
    amount = request.data.get('amount')
    phone_number = request.data.get('phone_number')
    
    if not all([tournament_id, amount, phone_number]):
        return Response(
            {'error': 'tournament_id, amount, and phone_number are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Create prize payout transaction
    transaction = MPesaTransaction.objects.create(
        user=request.user,
        transaction_id=f"WTH{datetime.now().strftime('%Y%m%d%H%M%S')}",
        amount=amount,
        phone_number=phone_number,
        transaction_type='PRIZE',
        reference=f"Prize withdrawal for tournament {tournament_id}",
        status='PENDING'
    )
    
    return Response({
        'message': 'Withdrawal request initiated',
        'transaction_id': transaction.transaction_id
    })
