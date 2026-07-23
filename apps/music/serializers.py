from rest_framework import serializers
from .models import Mood, Playlist, GameMoodSession, SoundEffect, SpotifyToken

class MoodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mood
        fields = '__all__'

class PlaylistSerializer(serializers.ModelSerializer):
    mood_details = MoodSerializer(source='mood', read_only=True)
    
    class Meta:
        model = Playlist
        fields = '__all__'
        read_only_fields = ('user', 'created_at', 'updated_at')

class GameMoodSessionSerializer(serializers.ModelSerializer):
    mood_details = MoodSerializer(source='mood', read_only=True)
    
    class Meta:
        model = GameMoodSession
        fields = '__all__'
        read_only_fields = ('user', 'started_at')

class SoundEffectSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()
    
    class Meta:
        model = SoundEffect
        fields = '__all__'
    
    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return None

class SpotifyTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpotifyToken
        fields = '__all__'
        read_only_fields = ('user', 'created_at', 'updated_at')
