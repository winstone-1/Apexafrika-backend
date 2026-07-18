from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

User = get_user_model()

class Team(models.Model):
    name = models.CharField(max_length=255)
    tag = models.CharField(max_length=10, unique=True)
    logo = models.ImageField(upload_to='team_logos/', blank=True, null=True)
    banner = models.ImageField(upload_to='team_banners/', blank=True, null=True)
    
    captain = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='captained_teams')
    members = models.ManyToManyField(User, related_name='teams')
    
    game = models.CharField(max_length=100)
    region = models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    
    wins = models.IntegerField(default=0)
    losses = models.IntegerField(default=0)
    matches_played = models.IntegerField(default=0)
    tournaments_won = models.IntegerField(default=0)
    
    rank = models.IntegerField(default=0)
    rating = models.FloatField(default=0.0)
    
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    is_professional = models.BooleanField(default=False)
    
    social_links = models.JSONField(default=dict)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-rating', '-wins']
        indexes = [
            models.Index(fields=['game']),
            models.Index(fields=['region']),
            models.Index(fields=['is_verified']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.tag})"
    
    @property
    def win_rate(self):
        if self.matches_played > 0:
            return (self.wins / self.matches_played) * 100
        return 0.0
    
    @property
    def member_count(self):
        return self.members.count()

class TeamInvitation(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        ACCEPTED = 'ACCEPTED', 'Accepted'
        DECLINED = 'DECLINED', 'Declined'
        EXPIRED = 'EXPIRED', 'Expired'
    
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='invitations')
    invited_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_invitations')
    invited_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_invitations')
    
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    message = models.TextField(blank=True, null=True)
    
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['team', 'invited_user']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.invited_user.username} -> {self.team.name}"
    
    def accept(self):
        self.status = self.Status.ACCEPTED
        self.responded_at = timezone.now()
        self.team.members.add(self.invited_user)
        self.save()
    
    def decline(self):
        self.status = self.Status.DECLINED
        self.responded_at = timezone.now()
        self.save()
    
    def is_expired(self):
        return timezone.now() > self.expires_at
