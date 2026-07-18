from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'gamer_tag', 'role', 'is_active', 'date_joined')
    list_filter = ('role', 'is_active', 'is_staff', 'main_game')
    search_fields = ('username', 'email', 'gamer_tag', 'phone_number')
    ordering = ('-date_joined',)
    
    fieldsets = UserAdmin.fieldsets + (
        ('Gaming Profile', {
            'fields': ('gamer_tag', 'main_game', 'role', 'bio', 'avatar', 'phone_number')
        }),
        ('Social Links', {
            'fields': ('twitter', 'twitch', 'youtube')
        }),
        ('Stats', {
            'fields': ('tournaments_participated', 'tournaments_won', 'total_matches', 'win_rate')
        }),
        ('Activity', {
            'fields': ('last_active',)
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Gaming Profile', {
            'fields': ('gamer_tag', 'role')
        }),
    )

admin.site.register(User, CustomUserAdmin)
