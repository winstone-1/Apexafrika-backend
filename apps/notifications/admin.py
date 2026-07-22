from django.contrib import admin

from .models import Notification, NotificationPreference


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("user", "title", "type", "is_read", "created_at")
    list_filter = ("type", "is_read", "channel")
    search_fields = ("user__username", "title", "message")
    readonly_fields = ("created_at",)


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ("user", "updated_at")
    search_fields = ("user__username",)
