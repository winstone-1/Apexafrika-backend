from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator

User = get_user_model()

class PaystackTransaction(models.Model):
    """Paystack payment transactions"""
    
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        PROCESSING = 'PROCESSING', 'Processing'
        COMPLETED = 'COMPLETED', 'Completed'
        FAILED = 'FAILED', 'Failed'
        CANCELLED = 'CANCELLED', 'Cancelled'
        REFUNDED = 'REFUNDED', 'Refunded'
    
    class TransactionType(models.TextChoices):
        PAYMENT = 'PAYMENT', 'Payment'
        WITHDRAWAL = 'WITHDRAWAL', 'Withdrawal'
        REFUND = 'REFUND', 'Refund'
        PRIZE = 'PRIZE', 'Prize Payout'
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='paystack_transactions')
    
    # Paystack specific fields
    reference = models.CharField(max_length=255, unique=True)
    transaction_id = models.CharField(max_length=255, null=True, blank=True)
    authorization_code = models.CharField(max_length=255, null=True, blank=True)
    
    # Amount and currency
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    currency = models.CharField(max_length=10, default='NGN')  # NGN for Paystack
    
    # Status and type
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    transaction_type = models.CharField(max_length=20, choices=TransactionType.choices, default=TransactionType.PAYMENT)
    
    # Reference
    description = models.CharField(max_length=255, null=True, blank=True)
    tournament = models.ForeignKey('tournaments.Tournament', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Paystack response data
    gateway_response = models.JSONField(null=True, blank=True)
    payment_data = models.JSONField(null=True, blank=True)
    result_code = models.CharField(max_length=10, null=True, blank=True)
    result_description = models.TextField(null=True, blank=True)
    
    # Customer details
    customer_email = models.EmailField(null=True, blank=True)
    customer_phone = models.CharField(max_length=20, null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['reference']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.reference} - {self.user.username} - {self.amount} {self.currency}"
    
    @property
    def is_completed(self):
        return self.status == self.Status.COMPLETED
    
    @property
    def is_failed(self):
        return self.status in [self.Status.FAILED, self.Status.CANCELLED]

class PaymentMethod(models.Model):
    """Saved payment methods for users (Paystack)"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payment_methods')
    
    class MethodType(models.TextChoices):
        CARD = 'CARD', 'Card'
        BANK = 'BANK', 'Bank Transfer'
        USSD = 'USSD', 'USSD'
        QR = 'QR', 'QR Code'
    
    method_type = models.CharField(max_length=10, choices=MethodType.choices, default=MethodType.CARD)
    
    # Card details (tokenized)
    authorization_code = models.CharField(max_length=255, blank=True, null=True)
    card_type = models.CharField(max_length=20, blank=True, null=True)
    last_four = models.CharField(max_length=4, blank=True, null=True)
    expiry_month = models.CharField(max_length=2, blank=True, null=True)
    expiry_year = models.CharField(max_length=4, blank=True, null=True)
    bank = models.CharField(max_length=100, blank=True, null=True)
    account_name = models.CharField(max_length=255, blank=True, null=True)
    
    # Reusable token for recurring payments
    reusable = models.BooleanField(default=True)
    
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-is_default', '-created_at']
    
    def __str__(self):
        if self.method_type == self.MethodType.CARD:
            return f"Card: ****{self.last_four} ({self.card_type})"
        return f"{self.method_type}: {self.account_name or 'No details'}"
