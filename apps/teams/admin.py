from django.contrib import admin

from .models import Team, TeamInvitation


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "tag",
        "game",
        "region",
        "is_verified",
        "is_active")
    list_filter = ("game", "region", "is_verified", "is_active")
    search_fields = ("name", "tag", "description")


@admin.register(TeamInvitation)
class TeamInvitationAdmin(admin.ModelAdmin):
    list_display = ("team", "invited_user", "status", "created_at")
    list_filter = ("status",)
