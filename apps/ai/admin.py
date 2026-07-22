from django.contrib import admin

from .models import AIConversation, AIMessage, AIPrediction


@admin.register(AIConversation)
class AIConversationAdmin(admin.ModelAdmin):
    list_display = ("user", "title", "created_at")
    search_fields = ("user__username", "title")


@admin.register(AIMessage)
class AIMessageAdmin(admin.ModelAdmin):
    list_display = ("conversation", "role", "created_at")
    list_filter = ("role",)


@admin.register(AIPrediction)
class AIPredictionAdmin(admin.ModelAdmin):
    list_display = ("type", "confidence", "is_accurate", "created_at")
    list_filter = ("type", "is_accurate")
