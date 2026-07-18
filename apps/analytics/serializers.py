from rest_framework import serializers
from .models import AnalyticsDashboard, ExportReport

class AnalyticsDashboardSerializer(serializers.ModelSerializer):
    is_valid = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = AnalyticsDashboard
        fields = '__all__'
        read_only_fields = ('generated_at',)

class ExportReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExportReport
        fields = '__all__'
        read_only_fields = ('created_at', 'file')
