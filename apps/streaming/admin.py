from django.contrib import admin

from .models import Stream, StreamAnalytics, StreamChat


@admin.register(Stream)
class StreamAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "streamer",
        "platform",
        "status",
        "scheduled_start")
    list_filter = ("platform", "status")
    search_fields = ("title", "description", "streamer__username")


@admin.register(StreamChat)
class StreamChatAdmin(admin.ModelAdmin):
    list_display = ("stream", "user", "message_preview", "created_at")
    search_fields = ("user__username", "message")

    def message_preview(self, obj):
        return obj.message[:50]

    message_preview.short_description = "Message"


@admin.register(StreamAnalytics)
class StreamAnalyticsAdmin(admin.ModelAdmin):
    list_display = ("stream", "total_viewers", "peak_viewers", "updated_at")
