from django.contrib import admin
from .models import PlayerStats, PlayerMatchHistory

@admin.register(PlayerStats)
class PlayerStatsAdmin(admin.ModelAdmin):
    list_display = ('player', 'total_matches', 'total_wins', 'win_rate', 'tournaments_won')
    list_filter = ('region',)
    search_fields = ('player__username', 'player__gamer_tag')
    readonly_fields = ('updated_at',)

@admin.register(PlayerMatchHistory)
class PlayerMatchHistoryAdmin(admin.ModelAdmin):
    list_display = ('player', 'opponent', 'did_win', 'played_at')
    list_filter = ('did_win',)
    search_fields = ('player__username', 'opponent__username')
