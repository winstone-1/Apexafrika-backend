from rest_framework import serializers
from .models import Team, TeamInvitation
from apps.users.serializers import UserSerializer

class TeamSerializer(serializers.ModelSerializer):
    captain_details = UserSerializer(source='captain', read_only=True)
    members_details = UserSerializer(source='members', many=True, read_only=True)
    win_rate = serializers.FloatField(read_only=True)
    member_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Team
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'wins', 'losses', 'matches_played', 'tournaments_won')

class TeamInvitationSerializer(serializers.ModelSerializer):
    team_details = TeamSerializer(source='team', read_only=True)
    invited_by_details = UserSerializer(source='invited_by', read_only=True)
    invited_user_details = UserSerializer(source='invited_user', read_only=True)
    
    class Meta:
        model = TeamInvitation
        fields = '__all__'
        read_only_fields = ('created_at', 'responded_at')
