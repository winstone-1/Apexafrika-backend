from django.db.models import Count
from django.utils import timezone
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import AuditLog, SystemLog
from .serializers import AuditLogSerializer, SystemLogSerializer


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = AuditLogSerializer
    queryset = AuditLog.objects.all()
    filterset_fields = ["action", "module", "user"]
    search_fields = ["object_id", "object_type"]

    def get_queryset(self):
        queryset = super().get_queryset()

        start_date = self.request.query_params.get("start_date")
        end_date = self.request.query_params.get("end_date")

        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)

        return queryset

    @action(detail=False, methods=["get"])
    def stats(self, request):
        total = AuditLog.objects.count()
        recent = AuditLog.objects.filter(
            created_at__gte=timezone.now() - timezone.timedelta(days=7)
        ).count()

        actions = list(
            AuditLog.objects.values("action")
            .annotate(count=Count("id"))
            .order_by("-count")
        )
        modules = list(
            AuditLog.objects.values("module")
            .annotate(count=Count("id"))
            .order_by("-count")
        )

        return Response(
            {
                "total": total,
                "recent_7_days": recent,
                "actions": actions,
                "modules": modules,
            }
        )


class SystemLogViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = SystemLogSerializer
    queryset = SystemLog.objects.all()
    filterset_fields = ["severity", "source"]
    search_fields = ["message"]
