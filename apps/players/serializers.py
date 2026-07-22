from rest_framework import serializers

from apps.users.serializers import UserSerializer

from .models import PlayerMatchHistory, PlayerStats


class PlayerStatsSerializer(serializers.ModelSerializer):
    player_details = UserSerializer(source="player", read_only=True)

    class Meta:
        model = PlayerStats
        fields = "__all__"
        read_only_fields = ("updated_at",)


class PlayerMatchHistorySerializer(serializers.ModelSerializer):
    player_details = UserSerializer(source="player", read_only=True)
    opponent_details = UserSerializer(source="opponent", read_only=True)

    class Meta:
        model = PlayerMatchHistory
        fields = "__all__"
        read_only_fields = ("played_at",)
