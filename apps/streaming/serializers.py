from rest_framework import serializers

from .models import Stream, StreamAnalytics, StreamChat


class StreamSerializer(serializers.ModelSerializer):
    streamer_details = serializers.StringRelatedField(
        source="streamer.username")

    class Meta:
        model = Stream
        fields = "__all__"
        read_only_fields = (
            "created_at",
            "updated_at",
            "actual_start",
            "actual_end")


class StreamChatSerializer(serializers.ModelSerializer):
    user_details = serializers.StringRelatedField(source="user.username")

    class Meta:
        model = StreamChat
        fields = "__all__"
        read_only_fields = ("created_at",)


class StreamAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = StreamAnalytics
        fields = "__all__"
        read_only_fields = ("updated_at",)
