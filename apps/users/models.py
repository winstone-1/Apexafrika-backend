from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from typing import Optional
from datetime import datetime

class User(AbstractUser):
    class Role(models.TextChoices):
        ORGANIZER = 'ORGANIZER', 'Tournament Organizer'
        PLAYER = 'PLAYER', 'Player'
        CREATOR = 'CREATOR', 'Content Creator'
        DEVELOPER = 'DEVELOPER', 'Developer'
        ADMIN = 'ADMIN', 'Admin'
    
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.PLAYER
    )
    
    # Profile fields
    bio = models.TextField(blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    
    # Gaming-specific fields
    gamer_tag = models.CharField(max_length=50, unique=True, blank=True, null=True)
    main_game = models.CharField(max_length=100, blank=True, null=True)
    
    # Social links
    twitter = models.URLField(blank=True, null=True)
    twitch = models.URLField(blank=True, null=True)
    youtube = models.URLField(blank=True, null=True)
    
    # Stats
    tournaments_participated = models.IntegerField(default=0)
    tournaments_won = models.IntegerField(default=0)
    total_matches = models.IntegerField(default=0)
    win_rate = models.FloatField(default=0.0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_active = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'users'
        ordering = ['-date_joined']
        indexes = [
            models.Index(fields=['gamer_tag']),
            models.Index(fields=['role']),
            models.Index(fields=['main_game']),
        ]
    
    def __str__(self) -> str:
        return f"{self.username} ({self.gamer_tag or 'No Tag'})"
    
    @property
    def is_organizer(self) -> bool:
        return self.role == self.Role.ORGANIZER
    
    @property
    def is_player(self) -> bool:
        return self.role == self.Role.PLAYER
    
    @property
    def is_creator(self) -> bool:
        return self.role == self.Role.CREATOR
    
    def update_win_rate(self) -> None:
        if self.total_matches > 0:
            self.win_rate = (self.tournaments_won / self.total_matches) * 100
        else:
            self.win_rate = 0.0
        self.save(update_fields=['win_rate'])
    
    def increment_matches(self, won: bool = False) -> None:
        self.total_matches += 1
        if won:
            self.tournaments_won += 1
        self.update_win_rate()
