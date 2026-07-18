from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class Stream(models.Model):
    class Platform(models.TextChoices):
        TWITCH = 'TWITCH', 'Twitch'
        YOUTUBE = 'YOUTUBE', 'YouTube'
        FACEBOOK = 'FACEBOOK', 'Facebook Gaming'
        AFREECATV = 'AFREECATV', 'AfreecaTV'
        OTHER = 'OTHER', 'Other'
    
    class Status(models.TextChoices):
        SCHEDULED = 'SCHEDULED', 'Scheduled'
        LIVE = 'LIVE', 'Live'
        OFFLINE = 'OFFLINE', 'Offline'
        ENDED = 'ENDED', 'Ended'
    
    streamer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='streams')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    
    platform = models.CharField(max_length=20, choices=Platform.choices, default=Platform.TWITCH)
    stream_url = models.URLField()
    embed_url = models.URLField(blank=True, null=True)
    
    thumbnail = models.ImageField(upload_to='stream_thumbnails/', blank=True, null=True)
    
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.SCHEDULED)
    
    scheduled_start = models.DateTimeField()
    actual_start = models.DateTimeField(null=True, blank=True)
    actual_end = models.DateTimeField(null=True, blank=True)
    
    viewer_count = models.IntegerField(default=0)
    peak_viewers = models.IntegerField(default=0)
    total_views = models.IntegerField(default=0)
    
    tournament = models.ForeignKey('tournaments.Tournament', on_delete=models.SET_NULL, null=True, blank=True, related_name='streams')
    match = models.ForeignKey('tournaments.Match', on_delete=models.SET_NULL, null=True, blank=True, related_name='streams')
    
    chat_url = models.URLField(blank=True, null=True)
    recording_url = models.URLField(blank=True, null=True)
    
    is_featured = models.BooleanField(default=False)
    is_public = models.BooleanField(default=True)
    
    tags = models.JSONField(default=list)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-scheduled_start']
        indexes = [
            models.Index(fields=['status', 'scheduled_start']),
            models.Index(fields=['platform']),
            models.Index(fields=['tournament']),
        ]
    
    def __str__(self):
        return f"{self.streamer.username} - {self.title}"

class StreamChat(models.Model):
    stream = models.ForeignKey(Stream, on_delete=models.CASCADE, related_name='chats')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='stream_chats')
    message = models.TextField()
    is_pinned = models.BooleanField(default=False)
    is_flagged = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.user.username}: {self.message[:50]}..."

class StreamAnalytics(models.Model):
    stream = models.OneToOneField(Stream, on_delete=models.CASCADE, related_name='analytics')
    
    total_viewers = models.IntegerField(default=0)
    average_viewers = models.IntegerField(default=0)
    peak_viewers = models.IntegerField(default=0)
    
    chat_messages = models.IntegerField(default=0)
    unique_chatters = models.IntegerField(default=0)
    
    follows_gained = models.IntegerField(default=0)
    subscribers_gained = models.IntegerField(default=0)
    
    bitrate = models.IntegerField(default=0)
    resolution = models.CharField(max_length=50, blank=True, null=True)
    fps = models.IntegerField(default=0)
    
    duration_minutes = models.IntegerField(default=0)
    
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Analytics for {self.stream.title}"
