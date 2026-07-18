from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator

User = get_user_model()

class MPesaTransaction(models.Model):
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
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mpesa_transactions')
    
    transaction_id = models.CharField(max_length=50, unique=True)
    checkout_request_id = models.CharField(max_length=50, null=True, blank=True)
    merchant_request_id = models.CharField(max_length=50, null=True, blank=True)
    
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    currency = models.CharField(max_length=10, default='KES')
    
    phone_number = models.CharField(max_length=15)
    
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    transaction_type = models.CharField(max_length=20, choices=TransactionType.choices, default=TransactionType.PAYMENT)
    
    reference = models.CharField(max_length=255, null=True, blank=True)
    tournament = models.ForeignKey('tournaments.Tournament', on_delete=models.SET_NULL, null=True, blank=True)
    
    mpesa_response = models.JSONField(null=True, blank=True)
    result_code = models.CharField(max_length=10, null=True, blank=True)
    result_description = models.TextField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['transaction_id']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.transaction_id} - {self.user.username}"

class PaymentMethod(models.Model):
    class MethodType(models.TextChoices):
        MPESA = 'MPESA', 'M-Pesa'
        CARD = 'CARD', 'Credit/Debit Card'
        BANK = 'BANK', 'Bank Transfer'
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payment_methods')
    
    method_type = models.CharField(max_length=10, choices=MethodType.choices, default=MethodType.MPESA)
    
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    
    last_four = models.CharField(max_length=4, blank=True, null=True)
    card_type = models.CharField(max_length=20, blank=True, null=True)
    expiry_date = models.DateField(null=True, blank=True)
    
    bank_name = models.CharField(max_length=100, blank=True, null=True)
    account_number = models.CharField(max_length=50, blank=True, null=True)
    
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-is_default', '-created_at']
    
    def __str__(self):
        if self.method_type == self.MethodType.MPESA:
            return f"M-Pesa: {self.phone_number}"
        return f"{self.method_type}: {self.last_four or self.account_number or 'No details'}"
