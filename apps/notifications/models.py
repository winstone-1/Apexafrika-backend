from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class Notification(models.Model):
    class Type(models.TextChoices):
        TOURNAMENT = 'TOURNAMENT', 'Tournament'
        MATCH = 'MATCH', 'Match'
        PAYMENT = 'PAYMENT', 'Payment'
        COMMUNITY = 'COMMUNITY', 'Community'
        SYSTEM = 'SYSTEM', 'System'
        ACHIEVEMENT = 'ACHIEVEMENT', 'Achievement'
        REMINDER = 'REMINDER', 'Reminder'
    
    class Channel(models.TextChoices):
        PUSH = 'PUSH', 'Push'
        EMAIL = 'EMAIL', 'Email'
        SMS = 'SMS', 'SMS'
        IN_APP = 'IN_APP', 'In-App'
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(max_length=20, choices=Type.choices)
    channel = models.CharField(max_length=10, choices=Channel.choices, default=Channel.IN_APP)
    
    title = models.CharField(max_length=255)
    message = models.TextField()
    data = models.JSONField(default=dict)
    
    is_read = models.BooleanField(default=False)
    is_sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['is_read']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"

class NotificationPreference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_preferences')
    
    # Tournament notifications
    tournament_reminders = models.BooleanField(default=True)
    match_updates = models.BooleanField(default=True)
    registration_alerts = models.BooleanField(default=True)
    
    # Community notifications
    post_comments = models.BooleanField(default=True)
    post_likes = models.BooleanField(default=True)
    mentions = models.BooleanField(default=True)
    
    # Payment notifications
    payment_confirmation = models.BooleanField(default=True)
    prize_notifications = models.BooleanField(default=True)
    
    # System notifications
    system_updates = models.BooleanField(default=True)
    security_alerts = models.BooleanField(default=True)
    
    # Channels
    push_enabled = models.BooleanField(default=True)
    email_enabled = models.BooleanField(default=True)
    sms_enabled = models.BooleanField(default=False)
    
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Preferences for {self.user.username}"
