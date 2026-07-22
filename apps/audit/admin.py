from django.contrib import admin

from .models import AuditLog, SystemLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("user", "action", "module", "object_type", "created_at")
    list_filter = ("action", "module")
    search_fields = ("user__username", "object_id", "object_type")
    readonly_fields = ("created_at",)


@admin.register(SystemLog)
class SystemLogAdmin(admin.ModelAdmin):
    list_display = ("severity", "source", "message", "created_at")
    list_filter = ("severity", "source")
    search_fields = ("message",)
