from django.contrib import admin
from .models import NewsletterSubscription, NewsletterCampaign, NewsletterOpen, NewsletterClick

@admin.register(NewsletterSubscription)
class NewsletterSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('email', 'status', 'confirmed_at', 'created_at')
    list_filter = ('status',)
    search_fields = ('email', 'name')

@admin.register(NewsletterCampaign)
class NewsletterCampaignAdmin(admin.ModelAdmin):
    list_display = ('subject', 'status', 'sent_count', 'opened_count', 'created_at')
    list_filter = ('status',)
    search_fields = ('subject',)

@admin.register(NewsletterOpen)
class NewsletterOpenAdmin(admin.ModelAdmin):
    list_display = ('campaign', 'subscription', 'opened_at')

@admin.register(NewsletterClick)
class NewsletterClickAdmin(admin.ModelAdmin):
    list_display = ('campaign', 'subscription', 'url', 'clicked_at')
