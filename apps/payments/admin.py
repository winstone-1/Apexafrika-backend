from django.contrib import admin

from .models import PaymentMethod, PaystackTransaction


@admin.register(PaystackTransaction)
class PaystackTransactionAdmin(admin.ModelAdmin):
    list_display = (
        "reference",
        "user",
        "amount",
        "status",
        "transaction_type",
        "created_at",
    )
    list_filter = ("status", "transaction_type")
    search_fields = ("reference", "user__username", "transaction_id")
    readonly_fields = ("created_at", "completed_at")


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "method_type",
        "last_four",
        "card_type",
        "is_default",
        "is_active",
    )
    list_filter = ("method_type", "is_default", "is_active")
    search_fields = ("user__username", "last_four", "bank")
