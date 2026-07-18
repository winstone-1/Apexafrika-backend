from django.urls import path
from .views import MPesaPaymentView, mpesa_callback, PaymentHistoryView, PaymentMethodView, withdraw_prize

app_name = 'payments'

urlpatterns = [
    path('pay/', MPesaPaymentView.as_view(), name='mpesa-pay'),
    path('callback/', mpesa_callback, name='mpesa-callback'),
    path('history/', PaymentHistoryView.as_view(), name='payment-history'),
    path('methods/', PaymentMethodView.as_view(), name='payment-methods'),
    path('withdraw/', withdraw_prize, name='withdraw-prize'),
]
