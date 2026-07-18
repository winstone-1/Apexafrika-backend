from django.contrib import admin
from .models import LegalDocument, UserConsent, CookieConsent

@admin.register(LegalDocument)
class LegalDocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'type', 'language', 'version', 'is_active', 'effective_date')
    list_filter = ('type', 'language', 'is_active')
    search_fields = ('title', 'content')

@admin.register(UserConsent)
class UserConsentAdmin(admin.ModelAdmin):
    list_display = ('user', 'consent_type', 'consented_at', 'is_active')
    list_filter = ('consent_type', 'is_active')
    search_fields = ('user__username',)

@admin.register(CookieConsent)
class CookieConsentAdmin(admin.ModelAdmin):
    list_display = ('cookie_type', 'consent_given', 'created_at')
    list_filter = ('cookie_type', 'consent_given')
