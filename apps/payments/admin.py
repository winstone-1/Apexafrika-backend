from django.contrib import admin
from .models import MPesaTransaction, PaymentMethod

@admin.register(MPesaTransaction)
class MPesaTransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'user', 'amount', 'status', 'transaction_type', 'created_at')
    list_filter = ('status', 'transaction_type')
    search_fields = ('transaction_id', 'user__username', 'phone_number')
    readonly_fields = ('created_at',)

@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ('user', 'method_type', 'phone_number', 'is_default', 'is_active')
    list_filter = ('method_type', 'is_default', 'is_active')
    search_fields = ('user__username', 'phone_number')
