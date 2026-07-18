from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class AnalyticsDashboard(models.Model):
    class DashboardType(models.TextChoices):
        TOURNAMENT = 'TOURNAMENT', 'Tournament Analytics'
        PLAYER = 'PLAYER', 'Player Analytics'
        PLATFORM = 'PLATFORM', 'Platform Analytics'
        REVENUE = 'REVENUE', 'Revenue Analytics'
    
    type = models.CharField(max_length=20, choices=DashboardType.choices)
    
    data = models.JSONField()
    
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    
    generated_at = models.DateTimeField(auto_now_add=True)
    cached_until = models.DateTimeField()
    
    class Meta:
        ordering = ['-generated_at']
    
    @property
    def is_valid(self):
        from django.utils import timezone
        return timezone.now() <= self.cached_until

class ExportReport(models.Model):
    class Format(models.TextChoices):
        CSV = 'CSV', 'CSV'
        PDF = 'PDF', 'PDF'
        EXCEL = 'EXCEL', 'Excel'
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports')
    name = models.CharField(max_length=255)
    format = models.CharField(max_length=10, choices=Format.choices)
    file = models.FileField(upload_to='reports/')
    
    parameters = models.JSONField(default=dict)
    
    created_at = models.DateTimeField(auto_now_add=True)
    is_downloaded = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
