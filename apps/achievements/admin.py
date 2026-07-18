from django.contrib import admin
from .models import Achievement, UserAchievement

@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'tier', 'points', 'is_active')
    list_filter = ('category', 'tier', 'is_active')
    search_fields = ('name', 'description')

@admin.register(UserAchievement)
class UserAchievementAdmin(admin.ModelAdmin):
    list_display = ('user', 'achievement', 'is_equipped', 'unlocked_at')
    list_filter = ('is_equipped',)
    search_fields = ('user__username', 'achievement__name')
