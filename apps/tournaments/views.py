from rest_framework import viewsets, permissions, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from django.utils import timezone
from .models import Tournament, TournamentParticipant, Match
from .serializers import TournamentSerializer, TournamentParticipantSerializer, MatchSerializer

class TournamentViewSet(viewsets.ModelViewSet):
    queryset = Tournament.objects.all()
    serializer_class = TournamentSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]
    
    def perform_create(self, serializer):
        serializer.save(organizer=self.request.user)
    
    @action(detail=True, methods=['post'])
    def register(self, request, pk=None):
        tournament = self.get_object()
        
        if not tournament.is_registration_open:
            return Response(
                {'error': 'Registration is not open for this tournament'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if TournamentParticipant.objects.filter(tournament=tournament, player=request.user).exists():
            return Response(
                {'error': 'You are already registered for this tournament'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if tournament.spots_remaining <= 0:
            return Response(
                {'error': 'Tournament is full'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        participant = TournamentParticipant.objects.create(
            tournament=tournament,
            player=request.user
        )
        tournament.update_current_players()
        
        serializer = TournamentParticipantSerializer(participant)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        tournament = self.get_object()
        
        if tournament.status != tournament.Status.REGISTRATION:
            return Response(
                {'error': 'Tournament must be in registration phase'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if tournament.current_players < tournament.min_players:
            return Response(
                {'error': f'Need at least {tournament.min_players} players'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Simple single elimination bracket generation
        participants = tournament.participants.filter(status='REGISTERED')
        participant_list = list(participants)
        import random
        random.shuffle(participant_list)
        
        matches = []
        round_number = 1
        for i in range(0, len(participant_list), 2):
            if i + 1 < len(participant_list):
                match = Match.objects.create(
                    tournament=tournament,
                    round_number=round_number,
                    match_number=i//2 + 1,
                    player1=participant_list[i].player,
                    player2=participant_list[i+1].player,
                    scheduled_time=timezone.now() + timezone.timedelta(days=1)
                )
                matches.append(match)
        
        tournament.status = tournament.Status.LIVE
        tournament.save()
        
        return Response({
            'message': f'Tournament started with {len(matches)} matches',
            'matches': MatchSerializer(matches, many=True).data
        })
    
    @action(detail=True, methods=['get'])
    def brackets(self, request, pk=None):
        tournament = self.get_object()
        matches = tournament.matches.all()
        serializer = MatchSerializer(matches, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def participants(self, request, pk=None):
        tournament = self.get_object()
        participants = tournament.participants.all()
        serializer = TournamentParticipantSerializer(participants, many=True)
        return Response(serializer.data)
