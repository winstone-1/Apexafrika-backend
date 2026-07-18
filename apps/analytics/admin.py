from django.contrib import admin
from .models import AnalyticsDashboard, ExportReport

@admin.register(AnalyticsDashboard)
class AnalyticsDashboardAdmin(admin.ModelAdmin):
    list_display = ('type', 'generated_at', 'cached_until')
    list_filter = ('type',)
    readonly_fields = ('generated_at',)

@admin.register(ExportReport)
class ExportReportAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'format', 'created_at', 'is_downloaded')
    list_filter = ('format', 'is_downloaded')
    search_fields = ('user__username', 'name')
