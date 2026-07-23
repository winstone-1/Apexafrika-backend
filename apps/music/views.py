from rest_framework import viewsets, permissions, status, generics
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django.conf import settings
from django.utils import timezone
from django.shortcuts import get_object_or_404
import requests
import json
import base64
from datetime import datetime, timedelta
from .models import Mood, Playlist, GameMoodSession, SoundEffect, SpotifyToken
from .serializers import (
    MoodSerializer, PlaylistSerializer, GameMoodSessionSerializer,
    SoundEffectSerializer, SpotifyTokenSerializer
)

class MoodViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.AllowAny]
    serializer_class = MoodSerializer
    queryset = Mood.objects.filter(is_active=True)

class PlaylistViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PlaylistSerializer
    
    def get_queryset(self):
        return Playlist.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def sync_spotify(self, request, pk=None):
        playlist = self.get_object()
        token = get_spotify_token(request.user)
        
        if not token:
            return Response(
                {'error': 'Spotify not connected'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            headers = {'Authorization': f'Bearer {token.access_token}'}
            response = requests.get(
                f'https://api.spotify.com/v1/playlists/{playlist.external_id}/tracks',
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                tracks = []
                for item in data.get('items', []):
                    track = item.get('track', {})
                    tracks.append({
                        'id': track.get('id'),
                        'name': track.get('name'),
                        'artist': track.get('artists', [{}])[0].get('name'),
                        'album': track.get('album', {}).get('name'),
                        'duration_ms': track.get('duration_ms'),
                        'preview_url': track.get('preview_url'),
                        'external_url': track.get('external_urls', {}).get('spotify'),
                    })
                
                playlist.tracks = tracks
                playlist.track_count = len(tracks)
                playlist.save()
                
                return Response(PlaylistSerializer(playlist).data)
            else:
                return Response(
                    {'error': 'Failed to sync with Spotify'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class GameMoodSessionViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GameMoodSessionSerializer
    
    def get_queryset(self):
        return GameMoodSession.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def update_mood(self, request, pk=None):
        session = self.get_object()
        mood_id = request.data.get('mood_id')
        intensity = request.data.get('intensity', 0)
        game_stats = request.data.get('game_stats', {})
        
        if mood_id:
            mood = get_object_or_404(Mood, id=mood_id)
            session.mood = mood
        
        session.intensity = intensity
        if game_stats:
            session.game_stats = game_stats
        
        history_entry = {
            'timestamp': timezone.now().isoformat(),
            'mood': session.mood.name if session.mood else None,
            'intensity': intensity,
            'stats': game_stats
        }
        session.mood_history.append(history_entry)
        session.save()
        
        return Response(GameMoodSessionSerializer(session).data)
    
    @action(detail=True, methods=['post'])
    def end_session(self, request, pk=None):
        session = self.get_object()
        session.ended_at = timezone.now()
        session.save()
        return Response({'message': 'Session ended'})

class SoundEffectViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.AllowAny]
    serializer_class = SoundEffectSerializer
    queryset = SoundEffect.objects.filter(is_active=True)
    filterset_fields = ['type']

# ==================== SPOTIFY HELPERS ====================

def get_spotify_token(user):
    try:
        token = SpotifyToken.objects.get(user=user)
        if token.is_expired():
            refresh_spotify_token(token)
        return token
    except SpotifyToken.DoesNotExist:
        return None

def refresh_spotify_token(token):
    try:
        auth_str = f"{settings.SPOTIFY_CLIENT_ID}:{settings.SPOTIFY_CLIENT_SECRET}"
        auth_b64 = base64.b64encode(auth_str.encode()).decode()
        
        response = requests.post(
            'https://accounts.spotify.com/api/token',
            data={
                'grant_type': 'refresh_token',
                'refresh_token': token.refresh_token,
            },
            headers={
                'Authorization': f'Basic {auth_b64}',
                'Content-Type': 'application/x-www-form-urlencoded',
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            token.access_token = data['access_token']
            token.expires_at = timezone.now() + timedelta(seconds=data['expires_in'])
            token.save()
            return True
        return False
    except:
        return False

# ==================== SPOTIFY VIEWS ====================

class SpotifyAuthView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        scope = 'user-read-private user-read-email playlist-read-private playlist-modify-private'
        
        auth_url = (
            'https://accounts.spotify.com/authorize'
            f'?client_id={settings.SPOTIFY_CLIENT_ID}'
            f'&response_type=code'
            f'&redirect_uri={settings.SPOTIFY_REDIRECT_URI}'
            f'&scope={scope}'
            f'&state={request.user.id}'
        )
        
        return Response({'auth_url': auth_url})

class SpotifyCallbackView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        code = request.data.get('code')
        user_id = request.data.get('state')
        
        if not code:
            return Response(
                {'error': 'Authorization code required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            auth_str = f"{settings.SPOTIFY_CLIENT_ID}:{settings.SPOTIFY_CLIENT_SECRET}"
            auth_b64 = base64.b64encode(auth_str.encode()).decode()
            
            response = requests.post(
                'https://accounts.spotify.com/api/token',
                data={
                    'grant_type': 'authorization_code',
                    'code': code,
                    'redirect_uri': settings.SPOTIFY_REDIRECT_URI,
                },
                headers={
                    'Authorization': f'Basic {auth_b64}',
                    'Content-Type': 'application/x-www-form-urlencoded',
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                
                user = get_object_or_404(User, id=user_id)
                token, created = SpotifyToken.objects.update_or_create(
                    user=user,
                    defaults={
                        'access_token': data['access_token'],
                        'refresh_token': data.get('refresh_token', ''),
                        'expires_at': timezone.now() + timedelta(seconds=data['expires_in']),
                    }
                )
                
                return Response({
                    'message': 'Spotify connected successfully',
                    'expires_in': data['expires_in']
                })
            else:
                return Response(
                    {'error': 'Failed to exchange code'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_spotify_status(request):
    token = SpotifyToken.objects.filter(user=request.user).first()
    
    if token and not token.is_expired():
        return Response({'connected': True, 'expires_at': token.expires_at})
    elif token and token.is_expired():
        try:
            refreshed = refresh_spotify_token(token)
            if refreshed:
                return Response({'connected': True, 'refreshed': True})
        except:
            pass
        return Response({'connected': False, 'expired': True})
    
    return Response({'connected': False})

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def generate_mood_recommendations(request):
    mood = request.data.get('mood', 'NEUTRAL')
    limit = request.data.get('limit', 10)
    
    mood_playlists = {
        'HYPE': ['edm', 'drum and bass', 'trap'],
        'FOCUS': ['lo-fi', 'chillhop', 'ambient'],
        'VICTORY': ['pop', 'dance', 'happy'],
        'DEFEAT': ['sad', 'indie', 'acoustic'],
        'INTENSE': ['orchestral', 'epic', 'cinematic'],
        'NEUTRAL': ['chill', 'acoustic', 'jazz'],
    }
    
    genres = mood_playlists.get(mood, ['chill'])
    
    token = get_spotify_token(request.user)
    
    if not token:
        return Response({
            'error': 'Spotify not connected',
            'tracks': []
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        headers = {'Authorization': f'Bearer {token.access_token}'}
        
        response = requests.get(
            'https://api.spotify.com/v1/recommendations',
            params={
                'seed_genres': ','.join(genres[:2]),
                'limit': limit,
                'target_energy': 0.8 if mood == 'HYPE' else 0.5,
            },
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            tracks = []
            for track in data.get('tracks', []):
                tracks.append({
                    'id': track.get('id'),
                    'name': track.get('name'),
                    'artist': track.get('artists', [{}])[0].get('name'),
                    'album': track.get('album', {}).get('name'),
                    'preview_url': track.get('preview_url'),
                    'external_url': track.get('external_urls', {}).get('spotify'),
                })
            return Response({'tracks': tracks})
        else:
            return Response(
                {'error': 'Failed to get recommendations'},
                status=status.HTTP_400_BAD_REQUEST
            )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# ==================== ELEVENLABS VOICE VIEWS ====================

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def generate_speech(request):
    """Generate speech using ElevenLabs API"""
    text = request.data.get('text')
    voice_id = request.data.get('voice_id', settings.ELEVENLABS_DEFAULT_VOICE)
    model_id = request.data.get('model_id', settings.ELEVENLABS_MODEL)
    
    if not text:
        return Response(
            {'error': 'Text is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": settings.ELEVENLABS_API_KEY
        }
        
        data = {
            "text": text,
            "model_id": model_id,
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75
            }
        }
        
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code == 200:
            import base64
            audio_base64 = base64.b64encode(response.content).decode('utf-8')
            return Response({
                'success': True,
                'audio': audio_base64,
                'format': 'audio/mpeg'
            })
        else:
            return Response(
                {'error': f"ElevenLabs API error: {response.status_code}"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_elevenlabs_voices(request):
    """Get available ElevenLabs voices"""
    try:
        url = "https://api.elevenlabs.io/v1/voices"
        headers = {"xi-api-key": settings.ELEVENLABS_API_KEY}
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            voices = []
            for voice in data.get('voices', []):
                # Filter for African voices or all voices
                voices.append({
                    'id': voice.get('voice_id'),
                    'name': voice.get('name'),
                    'category': voice.get('category'),
                    'labels': voice.get('labels', {}),
                    'preview_url': voice.get('preview_url')
                })
            return Response({'voices': voices})
        else:
            return Response(
                {'error': 'Failed to fetch voices'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_elevenlabs_voice_by_id(request, voice_id):
    """Get specific ElevenLabs voice"""
    try:
        url = f"https://api.elevenlabs.io/v1/voices/{voice_id}"
        headers = {"xi-api-key": settings.ELEVENLABS_API_KEY}
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            return Response(response.json())
        else:
            return Response(
                {'error': 'Voice not found'},
                status=status.HTTP_404_NOT_FOUND
            )
            
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def generate_voice_clone(request):
    """Clone a voice using ElevenLabs"""
    name = request.data.get('name')
    description = request.data.get('description')
    audio_url = request.data.get('audio_url')
    
    if not name or not audio_url:
        return Response(
            {'error': 'Name and audio_url are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        url = "https://api.elevenlabs.io/v1/voices/add"
        
        headers = {"xi-api-key": settings.ELEVENLABS_API_KEY}
        
        # Download audio from URL
        audio_response = requests.get(audio_url)
        
        if audio_response.status_code != 200:
            return Response(
                {'error': 'Failed to download audio'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        files = {
            'files': ('voice_sample.mp3', audio_response.content, 'audio/mpeg')
        }
        
        data = {
            'name': name,
            'description': description,
            'labels': json.dumps({'source': 'apexafrika'})
        }
        
        response = requests.post(url, data=data, files=files, headers=headers)
        
        if response.status_code == 200:
            return Response({
                'success': True,
                'voice': response.json()
            })
        else:
            return Response(
                {'error': 'Failed to clone voice'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
