from django.utils import timezone
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Stream, StreamAnalytics, StreamChat
from .serializers import (StreamAnalyticsSerializer, StreamChatSerializer,
                          StreamSerializer)


class StreamViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.AllowAny]
    serializer_class = StreamSerializer
    queryset = Stream.objects.all()
    filterset_fields = ["status", "platform", "tournament"]
    search_fields = ["title", "description"]

    def get_queryset(self):
        queryset = super().get_queryset()

        # Only show public streams to non-authenticated users
        if not self.request.user.is_authenticated:
            queryset = queryset.filter(is_public=True)
        else:
            # Show all streams to authenticated users
            pass

        # Filter by live status
        live = self.request.query_params.get("live")
        if live == "true":
            queryset = queryset.filter(status="LIVE")

        return queryset

    @action(detail=True, methods=["post"])
    def start(self, request, pk=None):
        stream = self.get_object()
        if stream.status == "LIVE":
            return Response(
                {"error": "Stream is already live"}, status=status.HTTP_400_BAD_REQUEST
            )

        stream.status = "LIVE"
        stream.actual_start = timezone.now()
        stream.save()

        return Response({"message": "Stream started"})

    @action(detail=True, methods=["post"])
    def end(self, request, pk=None):
        stream = self.get_object()
        if stream.status != "LIVE":
            return Response(
                {"error": "Stream is not live"}, status=status.HTTP_400_BAD_REQUEST
            )

        stream.status = "ENDED"
        stream.actual_end = timezone.now()
        stream.save()

        return Response({"message": "Stream ended"})

    @action(detail=True, methods=["post"])
    def chat(self, request, pk=None):
        stream = self.get_object()
        message = request.data.get("message")

        if not message:
            return Response(
                {"error": "Message is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        if not request.user.is_authenticated:
            return Response(
                {"error": "Authentication required"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        chat = StreamChat.objects.create(
            stream=stream, user=request.user, message=message
        )

        serializer = StreamChatSerializer(chat)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["get"])
    def live(self, request):
        """Get all live streams"""
        streams = Stream.objects.filter(status="LIVE")
        serializer = StreamSerializer(streams, many=True)
        return Response(serializer.data)


class StreamChatViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = StreamChatSerializer

    def get_queryset(self):
        return StreamChat.objects.filter(user=self.request.user)


class StreamAnalyticsViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = StreamAnalyticsSerializer
    queryset = StreamAnalytics.objects.all()
