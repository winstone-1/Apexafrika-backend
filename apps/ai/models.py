from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class AIConversation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_conversations')
    title = models.CharField(max_length=255, blank=True, null=True)
    context = models.JSONField(default=dict)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"Conversation {self.id} - {self.user.username}"

class AIMessage(models.Model):
    class Role(models.TextChoices):
        USER = 'USER', 'User'
        ASSISTANT = 'ASSISTANT', 'Assistant'
        SYSTEM = 'SYSTEM', 'System'
    
    conversation = models.ForeignKey(AIConversation, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=10, choices=Role.choices)
    content = models.TextField()
    metadata = models.JSONField(default=dict)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.role}: {self.content[:50]}..."

class AIPrediction(models.Model):
    class Type(models.TextChoices):
        MATCH_WINNER = 'MATCH_WINNER', 'Match Winner'
        TOURNAMENT_WINNER = 'TOURNAMENT_WINNER', 'Tournament Winner'
        PLAYER_PERFORMANCE = 'PLAYER_PERFORMANCE', 'Player Performance'
        MATCH_SCORE = 'MATCH_SCORE', 'Match Score'
        TEAM_PERFORMANCE = 'TEAM_PERFORMANCE', 'Team Performance'
    
    type = models.CharField(max_length=20, choices=Type.choices)
    match = models.ForeignKey('tournaments.Match', on_delete=models.CASCADE, null=True, blank=True)
    tournament = models.ForeignKey('tournaments.Tournament', on_delete=models.CASCADE, null=True, blank=True)
    player = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='ai_predictions')
    team = models.ForeignKey('teams.Team', on_delete=models.CASCADE, null=True, blank=True)
    
    prediction = models.JSONField()
    confidence = models.FloatField(default=0.0)
    actual_result = models.JSONField(null=True, blank=True)
    is_accurate = models.BooleanField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['type']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"{self.type} - {self.created_at}"
