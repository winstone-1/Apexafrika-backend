from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class ChatRoom(models.Model):
    class Type(models.TextChoices):
        DIRECT = 'DIRECT', 'Direct'
        GROUP = 'GROUP', 'Group'
        TOURNAMENT = 'TOURNAMENT', 'Tournament'
        TEAM = 'TEAM', 'Team'
    
    type = models.CharField(max_length=20, choices=Type.choices)
    name = models.CharField(max_length=255, blank=True, null=True)
    participants = models.ManyToManyField(User, related_name='chat_rooms')
    tournament = models.ForeignKey('tournaments.Tournament', on_delete=models.CASCADE, null=True, blank=True)
    team = models.ForeignKey('teams.Team', on_delete=models.CASCADE, null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['type']),
            models.Index(fields=['updated_at']),
        ]
    
    def __str__(self):
        return self.name or f"Chat {self.id}"

class ChatMessage(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    attachment = models.FileField(upload_to='chat_attachments/', blank=True, null=True)
    attachment_type = models.CharField(max_length=50, blank=True, null=True)
    
    is_read = models.BooleanField(default=False)
    read_by = models.ManyToManyField(User, related_name='read_messages', blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['room', '-created_at']),
            models.Index(fields=['sender']),
        ]
    
    def __str__(self):
        return f"{self.sender.username}: {self.content[:50]}..."
