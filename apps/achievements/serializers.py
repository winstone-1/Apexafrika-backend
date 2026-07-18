from rest_framework import serializers
from .models import Achievement, UserAchievement

class AchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Achievement
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

class UserAchievementSerializer(serializers.ModelSerializer):
    achievement_details = AchievementSerializer(source='achievement', read_only=True)
    unlocked_time = serializers.DateTimeField(source='unlocked_at', read_only=True)
    
    class Meta:
        model = UserAchievement
        fields = '__all__'
        read_only_fields = ('user', 'unlocked_at', 'progress')
