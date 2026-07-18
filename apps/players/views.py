from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.db.models import F, Q, Count, Avg
from django.contrib.auth import get_user_model
from .models import PlayerStats, PlayerMatchHistory
from .serializers import PlayerStatsSerializer, PlayerMatchHistorySerializer

User = get_user_model()

class PlayerStatsView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PlayerStatsSerializer
    
    def get_object(self):
        stats, created = PlayerStats.objects.get_or_create(player=self.request.user)
        return stats

class LeaderboardView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = PlayerStatsSerializer
    
    def get_queryset(self):
        queryset = PlayerStats.objects.select_related('player').all()
        
        # Filter by region
        region = self.request.query_params.get('region')
        if region:
            queryset = queryset.filter(region=region)
        
        # Filter by game
        game = self.request.query_params.get('game')
        if game:
            queryset = queryset.filter(player__main_game=game)
        
        # Order by win_rate, total_wins, or tournaments_won
        order_by = self.request.query_params.get('order_by', '-win_rate')
        if order_by in ['win_rate', 'total_wins', 'tournaments_won', 'total_matches']:
            queryset = queryset.order_by(f'-{order_by}')
        else:
            queryset = queryset.order_by('-win_rate')
        
        return queryset

class MatchHistoryView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PlayerMatchHistorySerializer
    
    def get_queryset(self):
        return PlayerMatchHistory.objects.filter(player=self.request.user).order_by('-played_at')

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def get_player_stats_detail(request, user_id):
    try:
        stats = PlayerStats.objects.get(player_id=user_id)
        serializer = PlayerStatsSerializer(stats)
        return Response(serializer.data)
    except PlayerStats.DoesNotExist:
        return Response({'error': 'Player stats not found'}, status=status.HTTP_404_NOT_FOUND)
