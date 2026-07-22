from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

User = get_user_model()


class PlayerStats(models.Model):
    player = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="stats")

    total_matches = models.IntegerField(default=0)
    total_wins = models.IntegerField(default=0)
    total_losses = models.IntegerField(default=0)
    win_rate = models.FloatField(
        default=0.0, validators=[MinValueValidator(0), MaxValueValidator(100)]
    )

    tournaments_played = models.IntegerField(default=0)
    tournaments_won = models.IntegerField(default=0)
    top_3_finishes = models.IntegerField(default=0)

    game_stats = models.JSONField(default=dict)

    current_win_streak = models.IntegerField(default=0)
    longest_win_streak = models.IntegerField(default=0)

    global_rank = models.IntegerField(null=True, blank=True)
    regional_rank = models.IntegerField(null=True, blank=True)
    region = models.CharField(max_length=50, blank=True, null=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-win_rate", "-total_wins"]
        indexes = [
            models.Index(fields=["-win_rate"]),
            models.Index(fields=["region"]),
        ]

    def __str__(self):
        return f"Stats for {self.player.username}"

    def calculate_win_rate(self):
        if self.total_matches > 0:
            self.win_rate = (self.total_wins / self.total_matches) * 100
        else:
            self.win_rate = 0.0
        self.save(update_fields=["win_rate"])


class PlayerMatchHistory(models.Model):
    player = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="match_history"
    )
    opponent = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="match_history_as_opponent"
    )

    score = models.IntegerField()
    opponent_score = models.IntegerField()
    did_win = models.BooleanField()

    kills = models.IntegerField(default=0)
    deaths = models.IntegerField(default=0)
    assists = models.IntegerField(default=0)
    headshots = models.IntegerField(default=0)
    accuracy = models.FloatField(default=0.0)
    damage_done = models.IntegerField(default=0)

    performance_metrics = models.JSONField(default=dict)

    played_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-played_at"]
        indexes = [
            models.Index(fields=["player", "-played_at"]),
        ]

    def __str__(self):
        return f"{self.player.username} vs {self.opponent.username}"
