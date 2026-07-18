from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Achievement(models.Model):
    class Category(models.TextChoices):
        TOURNAMENT = 'TOURNAMENT', 'Tournament'
        MATCH = 'MATCH', 'Match'
        COMMUNITY = 'COMMUNITY', 'Community'
        STREAK = 'STREAK', 'Streak'
        MILESTONE = 'MILESTONE', 'Milestone'
        SPECIAL = 'SPECIAL', 'Special'
    
    class Tier(models.TextChoices):
        BRONZE = 'BRONZE', 'Bronze'
        SILVER = 'SILVER', 'Silver'
        GOLD = 'GOLD', 'Gold'
        PLATINUM = 'PLATINUM', 'Platinum'
        DIAMOND = 'DIAMOND', 'Diamond'
    
    name = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=Category.choices)
    tier = models.CharField(max_length=20, choices=Tier.choices, default=Tier.BRONZE)
    
    icon = models.ImageField(upload_to='achievement_icons/', blank=True, null=True)
    points = models.IntegerField(default=10)
    
    # Conditions for unlocking
    required_wins = models.IntegerField(default=0)
    required_matches = models.IntegerField(default=0)
    required_tournaments = models.IntegerField(default=0)
    required_streak = models.IntegerField(default=0)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} ({self.tier})"

class UserAchievement(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='achievements')
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    unlocked_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'achievement']
        ordering = ['-unlocked_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.achievement.name}"
