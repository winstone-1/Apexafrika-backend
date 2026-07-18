from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

User = get_user_model()

class Tournament(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Draft'
        REGISTRATION = 'REGISTRATION', 'Registration Open'
        LIVE = 'LIVE', 'Live'
        COMPLETED = 'COMPLETED', 'Completed'
        CANCELLED = 'CANCELLED', 'Cancelled'
    
    class Format(models.TextChoices):
        SINGLE_ELIM = 'SINGLE_ELIM', 'Single Elimination'
        DOUBLE_ELIM = 'DOUBLE_ELIM', 'Double Elimination'
        ROUND_ROBIN = 'ROUND_ROBIN', 'Round Robin'
        SWISS = 'SWISS', 'Swiss System'
    
    name = models.CharField(max_length=255)
    description = models.TextField()
    game = models.CharField(max_length=100)
    format = models.CharField(max_length=20, choices=Format.choices, default=Format.SINGLE_ELIM)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organized_tournaments')
    
    registration_start = models.DateTimeField()
    registration_end = models.DateTimeField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    max_players = models.IntegerField(default=16)
    min_players = models.IntegerField(default=4)
    current_players = models.IntegerField(default=0)
    
    prize_pool = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    currency = models.CharField(max_length=10, default='KES')
    prize_distribution = models.JSONField(default=list)
    
    banner_image = models.ImageField(upload_to='tournament_banners/', blank=True, null=True)
    rules = models.TextField(blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    is_public = models.BooleanField(default=True)
    
    total_matches = models.IntegerField(default=0)
    total_viewers = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['status', 'start_date']),
            models.Index(fields=['game']),
            models.Index(fields=['organizer']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.game}"
    
    @property
    def is_registration_open(self):
        now = timezone.now()
        return (self.status == self.Status.REGISTRATION and 
                self.registration_start <= now <= self.registration_end)
    
    @property
    def spots_remaining(self):
        return self.max_players - self.current_players
    
    def update_current_players(self):
        self.current_players = self.participants.count()
        self.save(update_fields=['current_players'])

class TournamentParticipant(models.Model):
    class Status(models.TextChoices):
        REGISTERED = 'REGISTERED', 'Registered'
        CONFIRMED = 'CONFIRMED', 'Confirmed'
        CHECKED_IN = 'CHECKED_IN', 'Checked In'
        DROPPED = 'DROPPED', 'Dropped'
        DISQUALIFIED = 'DISQUALIFIED', 'Disqualified'
    
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='participants')
    player = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tournament_registrations')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.REGISTERED)
    registered_at = models.DateTimeField(auto_now_add=True)
    checked_in_at = models.DateTimeField(null=True, blank=True)
    seed = models.IntegerField(null=True, blank=True)
    
    wins = models.IntegerField(default=0)
    losses = models.IntegerField(default=0)
    draws = models.IntegerField(default=0)
    points = models.IntegerField(default=0)
    rank = models.IntegerField(null=True, blank=True)
    
    class Meta:
        unique_together = ['tournament', 'player']
        ordering = ['-points', 'wins']
    
    def __str__(self):
        return f"{self.player.gamer_tag} - {self.tournament.name}"

class Match(models.Model):
    class Status(models.TextChoices):
        SCHEDULED = 'SCHEDULED', 'Scheduled'
        LIVE = 'LIVE', 'Live'
        COMPLETED = 'COMPLETED', 'Completed'
        CANCELLED = 'CANCELLED', 'Cancelled'
    
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='matches')
    round_number = models.IntegerField()
    match_number = models.IntegerField()
    
    player1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='matches_as_player1', null=True, blank=True)
    player2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='matches_as_player2', null=True, blank=True)
    winner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='matches_won', null=True, blank=True)
    
    player1_score = models.IntegerField(default=0)
    player2_score = models.IntegerField(default=0)
    
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.SCHEDULED)
    
    scheduled_time = models.DateTimeField()
    actual_time = models.DateTimeField(null=True, blank=True)
    
    bracket_position = models.IntegerField(null=True, blank=True)
    
    class Meta:
        ordering = ['round_number', 'match_number']
        indexes = [
            models.Index(fields=['tournament', 'status']),
            models.Index(fields=['round_number']),
        ]
    
    def __str__(self):
        p1 = self.player1.gamer_tag if self.player1 else "TBD"
        p2 = self.player2.gamer_tag if self.player2 else "TBD"
        return f"{p1} vs {p2} - Round {self.round_number}"
    
    @property
    def is_completed(self):
        return self.status == self.Status.COMPLETED
