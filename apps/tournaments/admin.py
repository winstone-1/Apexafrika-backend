from django.contrib import admin

from .models import Match, Tournament, TournamentParticipant


@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "game",
        "status",
        "organizer",
        "start_date",
        "current_players",
        "max_players",
    )
    list_filter = ("status", "game", "format")
    search_fields = ("name", "description", "organizer__username")
    readonly_fields = ("created_at", "updated_at")


@admin.register(TournamentParticipant)
class TournamentParticipantAdmin(admin.ModelAdmin):
    list_display = ("tournament", "player", "status", "registered_at")
    list_filter = ("status", "tournament")
    search_fields = ("player__username", "player__gamer_tag")


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = (
        "tournament",
        "round_number",
        "player1",
        "player2",
        "status",
        "scheduled_time",
    )
    list_filter = ("status", "round_number", "tournament")
    search_fields = ("player1__username", "player2__username")
