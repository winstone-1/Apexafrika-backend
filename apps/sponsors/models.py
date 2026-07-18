from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Sponsor(models.Model):
    class Type(models.TextChoices):
        BRAND = 'BRAND', 'Brand'
        INDIVIDUAL = 'INDIVIDUAL', 'Individual'
        ORGANIZATION = 'ORGANIZATION', 'Organization'
    
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=20, choices=Type.choices)
    logo = models.ImageField(upload_to='sponsor_logos/', blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

class Sponsorship(models.Model):
    class Tier(models.TextChoices):
        TITLE = 'TITLE', 'Title'
        GOLD = 'GOLD', 'Gold'
        SILVER = 'SILVER', 'Silver'
        BRONZE = 'BRONZE', 'Bronze'
        PARTNER = 'PARTNER', 'Partner'
    
    sponsor = models.ForeignKey(Sponsor, on_delete=models.CASCADE, related_name='sponsorships')
    tournament = models.ForeignKey('tournaments.Tournament', on_delete=models.CASCADE, related_name='sponsorships')
    tier = models.CharField(max_length=20, choices=Tier.choices)
    
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='KES')
    
    benefits = models.JSONField(default=list)
    
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-amount']
    
    def __str__(self):
        return f"{self.sponsor.name} - {self.tournament.name} ({self.tier})"
