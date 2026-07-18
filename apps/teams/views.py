from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from .models import Team, TeamInvitation
from .serializers import TeamSerializer, TeamInvitationSerializer

class TeamViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TeamSerializer
    
    def get_queryset(self):
        user = self.request.user
        return Team.objects.filter(Q(captain=user) | Q(members=user)).distinct()
    
    def perform_create(self, serializer):
        team = serializer.save(captain=self.request.user)
        team.members.add(self.request.user)
    
    @action(detail=True, methods=['post'])
    def invite(self, request, pk=None):
        team = self.get_object()
        
        if team.captain != request.user:
            return Response(
                {'error': 'Only the captain can invite players'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        user_id = request.data.get('user_id')
        message = request.data.get('message', '')
        
        if not user_id:
            return Response(
                {'error': 'user_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        try:
            invited_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if invited_user == request.user:
            return Response(
                {'error': 'Cannot invite yourself'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if team.members.filter(id=user_id).exists():
            return Response(
                {'error': 'User is already a member'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check for existing pending invitation
        existing = TeamInvitation.objects.filter(
            team=team,
            invited_user=invited_user,
            status='PENDING'
        ).first()
        
        if existing:
            return Response(
                {'error': 'Invitation already sent'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        invitation = TeamInvitation.objects.create(
            team=team,
            invited_by=request.user,
            invited_user=invited_user,
            message=message,
            expires_at=timezone.now() + timedelta(days=7)
        )
        
        serializer = TeamInvitationSerializer(invitation)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def invitations(self, request):
        """Get all invitations for the current user"""
        invitations = TeamInvitation.objects.filter(
            invited_user=request.user,
            status='PENDING'
        )
        serializer = TeamInvitationSerializer(invitations, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def respond_invitation(self, request):
        """Accept or decline a team invitation"""
        invitation_id = request.data.get('invitation_id')
        action = request.data.get('action')  # 'accept' or 'decline'
        
        if not invitation_id or action not in ['accept', 'decline']:
            return Response(
                {'error': 'invitation_id and action are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            invitation = TeamInvitation.objects.get(
                id=invitation_id,
                invited_user=request.user,
                status='PENDING'
            )
        except TeamInvitation.DoesNotExist:
            return Response(
                {'error': 'Invitation not found or already responded'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if invitation.is_expired():
            invitation.status = 'EXPIRED'
            invitation.save()
            return Response(
                {'error': 'Invitation has expired'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if action == 'accept':
            invitation.accept()
            return Response({'message': 'Invitation accepted'})
        else:
            invitation.decline()
            return Response({'message': 'Invitation declined'})
    
    @action(detail=False, methods=['get'])
    def leaderboard(self, request):
        """Get team leaderboard"""
        game = request.query_params.get('game')
        region = request.query_params.get('region')
        
        queryset = Team.objects.filter(is_active=True)
        
        if game:
            queryset = queryset.filter(game=game)
        if region:
            queryset = queryset.filter(region=region)
        
        queryset = queryset.order_by('-rating', '-wins')
        serializer = TeamSerializer(queryset[:20], many=True)
        return Response(serializer.data)
