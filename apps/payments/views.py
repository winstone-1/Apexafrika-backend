from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.conf import settings
from django.shortcuts import get_object_or_404
from .models import PaystackTransaction, PaymentMethod
from .serializers import PaystackTransactionSerializer, PaymentMethodSerializer
import requests
import json
import uuid
from datetime import datetime

class PaystackInitializeView(generics.CreateAPIView):
    """Initialize a Paystack payment"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PaystackTransactionSerializer
    
    def perform_create(self, serializer):
        # Generate unique reference
        reference = f"APEX-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:8]}"
        
        amount = int(float(serializer.validated_data['amount']) * 100)  # Convert to kobo/cents
        
        # Prepare Paystack initialization data
        payload = {
            "email": self.request.user.email or settings.PAYSTACK.get('MERCHANT_EMAIL', ''),
            "amount": amount,
            "reference": reference,
            "callback_url": f"{settings.FRONTEND_URL}/payment/callback",
            "metadata": {
                "username": self.request.user.username,
                "user_id": self.request.user.id,
                "transaction_type": serializer.validated_data.get('transaction_type', 'PAYMENT'),
                "tournament_id": str(serializer.validated_data.get('tournament', {}).id) if serializer.validated_data.get('tournament') else None,
            }
        }
        
        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK['SECRET_KEY']}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(
                settings.PAYSTACK['INITIALIZE_URL'],
                json=payload,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('status'):
                    payment_data = data.get('data', {})
                    
                    # Create transaction record
                    transaction_obj = serializer.save(
                        user=self.request.user,
                        reference=reference,
                        status='PENDING',
                        payment_data=payment_data,
                        customer_email=self.request.user.email,
                        gateway_response=payment_data.get('gateway_response', '')
                    )
                    
                    self.response_data = {
                        'transaction': PaystackTransactionSerializer(transaction_obj).data,
                        'authorization_url': payment_data.get('authorization_url'),
                        'reference': reference,
                        'access_code': payment_data.get('access_code')
                    }
                else:
                    raise serializers.ValidationError(data.get('message', 'Paystack initialization failed'))
            else:
                raise serializers.ValidationError(f"Paystack API error: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            raise serializers.ValidationError(f"Payment service error: {str(e)}")
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(self.response_data, status=status.HTTP_200_OK)

class PaystackVerifyView(generics.GenericAPIView):
    """Verify a Paystack payment"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, reference):
        try:
            transaction_obj = get_object_or_404(PaystackTransaction, reference=reference, user=request.user)
            
            headers = {
                "Authorization": f"Bearer {settings.PAYSTACK['SECRET_KEY']}",
                "Content-Type": "application/json"
            }
            
            verify_url = f"{settings.PAYSTACK['VERIFY_URL']}{reference}"
            response = requests.get(verify_url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('status'):
                    payment_data = data.get('data', {})
                    
                    # Update transaction
                    transaction_obj.status = 'COMPLETED'
                    transaction_obj.transaction_id = str(payment_data.get('id'))
                    
                    # Handle authorization data safely
                    auth_data = payment_data.get('authorization', {})
                    if isinstance(auth_data, dict):
                        transaction_obj.authorization_code = auth_data.get('authorization_code', '')
                    
                    transaction_obj.gateway_response = payment_data
                    transaction_obj.completed_at = datetime.now()
                    transaction_obj.save()
                    
                    # Save payment method for future use
                    if isinstance(auth_data, dict) and auth_data.get('authorization_code'):
                        PaymentMethod.objects.get_or_create(
                            user=request.user,
                            authorization_code=auth_data.get('authorization_code', ''),
                            defaults={
                                'method_type': 'CARD',
                                'last_four': auth_data.get('last4', ''),
                                'card_type': auth_data.get('card_type', ''),
                                'expiry_month': auth_data.get('exp_month', ''),
                                'expiry_year': auth_data.get('exp_year', ''),
                                'bank': auth_data.get('bank', ''),
                                'account_name': auth_data.get('account_name', ''),
                                'reusable': auth_data.get('reusable', False),
                                'is_active': True
                            }
                        )
                    
                    return Response({
                        'status': 'success',
                        'message': 'Payment verified successfully',
                        'transaction': PaystackTransactionSerializer(transaction_obj).data
                    })
                else:
                    transaction_obj.status = 'FAILED'
                    transaction_obj.result_description = data.get('message', 'Verification failed')
                    transaction_obj.save()
                    return Response({
                        'status': 'failed',
                        'message': data.get('message', 'Payment verification failed')
                    }, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({
                    'error': f"Verification API error: {response.status_code}"
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except requests.exceptions.RequestException as e:
            return Response({
                'error': f"Verification service error: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PaystackWebhookView(generics.GenericAPIView):
    """Handle Paystack webhooks"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        payload = request.data
        event = payload.get('event')
        data = payload.get('data')
        
        if event == 'charge.success':
            reference = data.get('reference')
            try:
                transaction_obj = PaystackTransaction.objects.get(reference=reference)
                if transaction_obj.status == 'PENDING':
                    transaction_obj.status = 'COMPLETED'
                    transaction_obj.transaction_id = str(data.get('id'))
                    
                    # Handle authorization data safely
                    auth_data = data.get('authorization', {})
                    if isinstance(auth_data, dict):
                        transaction_obj.authorization_code = auth_data.get('authorization_code', '')
                    
                    transaction_obj.gateway_response = data
                    transaction_obj.completed_at = datetime.now()
                    transaction_obj.save()
                    
                    # Handle tournament registration
                    if transaction_obj.transaction_type == 'PAYMENT' and transaction_obj.tournament:
                        from apps.tournaments.models import TournamentParticipant
                        participant, created = TournamentParticipant.objects.get_or_create(
                            tournament=transaction_obj.tournament,
                            player=transaction_obj.user,
                            defaults={'status': 'REGISTERED'}
                        )
                        
                    return Response({'status': 'success'}, status=status.HTTP_200_OK)
            except PaystackTransaction.DoesNotExist:
                return Response({'error': 'Transaction not found'}, status=status.HTTP_404_NOT_FOUND)
        
        return Response({'status': 'ignored'}, status=status.HTTP_200_OK)

class PaymentHistoryView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PaystackTransactionSerializer
    
    def get_queryset(self):
        return PaystackTransaction.objects.filter(user=self.request.user).order_by('-created_at')

class PaymentMethodView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PaymentMethodSerializer
    
    def get_queryset(self):
        return PaymentMethod.objects.filter(user=self.request.user, is_active=True)
    
    def perform_create(self, serializer):
        if not PaymentMethod.objects.filter(user=self.request.user).exists():
            serializer.save(user=self.request.user, is_default=True)
        else:
            serializer.save(user=self.request.user)

class PaymentMethodDeleteView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = PaymentMethod.objects.all()
    
    def get_queryset(self):
        return PaymentMethod.objects.filter(user=self.request.user)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def withdraw_prize(request):
    """Withdraw tournament prize money via Paystack"""
    tournament_id = request.data.get('tournament_id')
    amount = request.data.get('amount')
    account_number = request.data.get('account_number')
    bank_code = request.data.get('bank_code')
    account_name = request.data.get('account_name')
    
    if not all([tournament_id, amount, account_number, bank_code]):
        return Response(
            {'error': 'tournament_id, amount, account_number, and bank_code are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    reference = f"PRIZE-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:8]}"
    
    transaction_obj = PaystackTransaction.objects.create(
        user=request.user,
        reference=reference,
        amount=amount,
        currency='NGN',
        transaction_type='PRIZE',
        description=f"Prize withdrawal for tournament {tournament_id}",
        status='PROCESSING'
    )
    
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK['SECRET_KEY']}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "source": "balance",
        "amount": int(float(amount) * 100),
        "recipient": {
            "type": "nuban",
            "name": account_name,
            "account_number": account_number,
            "bank_code": bank_code,
            "currency": "NGN"
        },
        "reason": f"Prize payout for tournament {tournament_id}"
    }
    
    try:
        response = requests.post(
            f"{settings.PAYSTACK['BASE_URL']}/transfer",
            json=payload,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status'):
                transaction_obj.status = 'COMPLETED'
                transaction_obj.transaction_id = str(data.get('data', {}).get('id'))
                transaction_obj.completed_at = datetime.now()
                transaction_obj.save()
                
                return Response({
                    'message': 'Withdrawal initiated successfully',
                    'transaction_id': transaction_obj.transaction_id,
                    'reference': reference
                })
            else:
                transaction_obj.status = 'FAILED'
                transaction_obj.result_description = data.get('message', 'Withdrawal failed')
                transaction_obj.save()
                return Response({
                    'error': data.get('message', 'Withdrawal failed')
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                'error': f"Paystack API error: {response.status_code}"
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except requests.exceptions.RequestException as e:
        return Response({
            'error': f"Payment service error: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_banks(request):
    """Get list of Nigerian banks for transfers"""
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK['SECRET_KEY']}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(
            f"{settings.PAYSTACK['BASE_URL']}/bank",
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status'):
                return Response(data.get('data', []))
            else:
                return Response({
                    'error': data.get('message', 'Failed to fetch banks')
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                'error': f"Paystack API error: {response.status_code}"
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except requests.exceptions.RequestException as e:
        return Response({
            'error': f"Service error: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
