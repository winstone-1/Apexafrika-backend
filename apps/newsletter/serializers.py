from rest_framework import serializers
from .models import NewsletterSubscription, NewsletterCampaign, NewsletterOpen, NewsletterClick

class NewsletterSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsletterSubscription
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'confirmation_token', 'confirmed_at')

class NewsletterCampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsletterCampaign
        fields = '__all__'
        read_only_fields = ('created_at', 'sent_at', 'sent_count', 'opened_count')

class NewsletterOpenSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsletterOpen
        fields = '__all__'

class NewsletterClickSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsletterClick
        fields = '__all__'
