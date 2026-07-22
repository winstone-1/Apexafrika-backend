from rest_framework import serializers

from apps.users.serializers import UserSerializer

from .models import Match, Tournament, TournamentParticipant


class TournamentSerializer(serializers.ModelSerializer):
    organizer_details = UserSerializer(source="organizer", read_only=True)
    spots_remaining = serializers.IntegerField(read_only=True)
    is_registration_open = serializers.BooleanField(read_only=True)

    class Meta:
        model = Tournament
        fields = "__all__"
        read_only_fields = (
            "organizer",
            "current_players",
            "total_matches",
            "total_viewers",
            "created_at",
            "updated_at",
        )


class TournamentParticipantSerializer(serializers.ModelSerializer):
    player_details = UserSerializer(source="player", read_only=True)

    class Meta:
        model = TournamentParticipant
        fields = "__all__"
        read_only_fields = (
            "registered_at",
            "checked_in_at",
            "wins",
            "losses",
            "draws",
            "points",
            "rank",
        )


class MatchSerializer(serializers.ModelSerializer):
    player1_details = UserSerializer(source="player1", read_only=True)
    player2_details = UserSerializer(source="player2", read_only=True)
    winner_details = UserSerializer(source="winner", read_only=True)
    is_completed = serializers.BooleanField(read_only=True)

    class Meta:
        model = Match
        fields = "__all__"
        read_only_fields = ("winner", "status", "actual_time")
