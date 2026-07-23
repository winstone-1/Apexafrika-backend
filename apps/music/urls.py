from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    MoodViewSet, PlaylistViewSet, GameMoodSessionViewSet,
    SoundEffectViewSet, SpotifyAuthView, SpotifyCallbackView,
    get_spotify_status, generate_mood_recommendations,
    generate_speech, get_elevenlabs_voices, get_elevenlabs_voice_by_id,
    generate_voice_clone
)

router = DefaultRouter()
router.register(r'moods', MoodViewSet, basename='mood')
router.register(r'playlists', PlaylistViewSet, basename='playlist')
router.register(r'sessions', GameMoodSessionViewSet, basename='mood-session')
router.register(r'sound-effects', SoundEffectViewSet, basename='sound-effect')

app_name = 'music'

urlpatterns = [
    path('', include(router.urls)),
    
    # Spotify
    path('spotify/auth/', SpotifyAuthView.as_view(), name='spotify-auth'),
    path('spotify/callback/', SpotifyCallbackView.as_view(), name='spotify-callback'),
    path('spotify/status/', get_spotify_status, name='spotify-status'),
    path('spotify/recommendations/', generate_mood_recommendations, name='spotify-recommendations'),
    
    # ElevenLabs
    path('speech/', generate_speech, name='generate-speech'),
    path('elevenlabs/voices/', get_elevenlabs_voices, name='elevenlabs-voices'),
    path('elevenlabs/voices/<str:voice_id>/', get_elevenlabs_voice_by_id, name='elevenlabs-voice-detail'),
    path('elevenlabs/clone/', generate_voice_clone, name='elevenlabs-clone'),
]
