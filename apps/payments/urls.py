from django.urls import path
from .views import (
    PaystackInitializeView, PaystackVerifyView, PaystackWebhookView,
    PaymentHistoryView, PaymentMethodView, PaymentMethodDeleteView,
    withdraw_prize, get_banks
)

app_name = 'payments'

urlpatterns = [
    # Paystack
    path('initialize/', PaystackInitializeView.as_view(), name='paystack-init'),
    path('verify/<str:reference>/', PaystackVerifyView.as_view(), name='paystack-verify'),
    path('webhook/', PaystackWebhookView.as_view(), name='paystack-webhook'),
    
    # History
    path('history/', PaymentHistoryView.as_view(), name='payment-history'),
    
    # Methods
    path('methods/', PaymentMethodView.as_view(), name='payment-methods'),
    path('methods/<int:pk>/', PaymentMethodDeleteView.as_view(), name='payment-method-delete'),
    
    # Withdrawals
    path('withdraw/', withdraw_prize, name='withdraw-prize'),
    path('banks/', get_banks, name='get-banks'),
]
