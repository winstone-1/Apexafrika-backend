from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class Mood(models.Model):
    class MoodType(models.TextChoices):
        HYPE = 'HYPE', 'Hype'
        FOCUS = 'FOCUS', 'Focus'
        VICTORY = 'VICTORY', 'Victory'
        DEFEAT = 'DEFEAT', 'Defeat'
        NEUTRAL = 'NEUTRAL', 'Neutral'
        INTENSE = 'INTENSE', 'Intense'
    
    name = models.CharField(max_length=20, choices=MoodType.choices, unique=True)
    description = models.TextField(blank=True, null=True)
    color = models.CharField(max_length=7, default='#FFB300')
    icon = models.CharField(max_length=50, blank=True, null=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.get_name_display()

class Playlist(models.Model):
    class Platform(models.TextChoices):
        SPOTIFY = 'SPOTIFY', 'Spotify'
        LOCAL = 'LOCAL', 'Local'
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='playlists')
    mood = models.ForeignKey(Mood, on_delete=models.SET_NULL, null=True, related_name='playlists')
    platform = models.CharField(max_length=10, choices=Platform.choices, default=Platform.LOCAL)
    
    name = models.CharField(max_length=255)
    external_id = models.CharField(max_length=255, blank=True, null=True)
    external_url = models.URLField(blank=True, null=True)
    
    cover_image = models.URLField(blank=True, null=True)
    tracks = models.JSONField(default=list)
    track_count = models.IntegerField(default=0)
    
    is_active = models.BooleanField(default=True)
    is_public = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'mood']),
            models.Index(fields=['platform']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.user.username}"

class GameMoodSession(models.Model):
    """Track mood during a game/tournament"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mood_sessions')
    tournament = models.ForeignKey('tournaments.Tournament', on_delete=models.SET_NULL, null=True, blank=True)
    match = models.ForeignKey('tournaments.Match', on_delete=models.SET_NULL, null=True, blank=True)
    
    mood = models.ForeignKey(Mood, on_delete=models.SET_NULL, null=True)
    intensity = models.IntegerField(default=0, help_text="0-100 intensity score")
    
    game_stats = models.JSONField(default=dict)
    mood_history = models.JSONField(default=list)
    
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['user', '-started_at']),
            models.Index(fields=['tournament']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.mood} - {self.started_at}"

class SoundEffect(models.Model):
    class EffectType(models.TextChoices):
        CHEER = 'CHEER', 'Crowd Cheer'
        TENSION = 'TENSION', 'Tension Build'
        VICTORY = 'VICTORY', 'Victory'
        DEFEAT = 'DEFEAT', 'Defeat'
        GOAL = 'GOAL', 'Goal/Score'
        EPIC = 'EPIC', 'Epic Moment'
        COUNTDOWN = 'COUNTDOWN', 'Countdown'
    
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=EffectType.choices)
    file = models.FileField(upload_to='sound_effects/')
    duration = models.FloatField(default=0.0)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.get_type_display()} - {self.name}"

class SpotifyToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='spotify_token')
    access_token = models.TextField()
    refresh_token = models.TextField()
    expires_at = models.DateTimeField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def is_expired(self):
        return timezone.now() >= self.expires_at
    
    def __str__(self):
        return f"Spotify token for {self.user.username}"
