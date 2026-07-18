from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class AuditLog(models.Model):
    class Action(models.TextChoices):
        CREATE = 'CREATE', 'Create'
        UPDATE = 'UPDATE', 'Update'
        DELETE = 'DELETE', 'Delete'
        VIEW = 'VIEW', 'View'
        LOGIN = 'LOGIN', 'Login'
        LOGOUT = 'LOGOUT', 'Logout'
        REGISTER = 'REGISTER', 'Register'
        PAYMENT = 'PAYMENT', 'Payment'
        PERMISSION = 'PERMISSION', 'Permission Change'
        EXPORT = 'EXPORT', 'Export'
        IMPORT = 'IMPORT', 'Import'
        SYSTEM = 'SYSTEM', 'System'
        ERROR = 'ERROR', 'Error'
    
    class Module(models.TextChoices):
        AUTH = 'AUTH', 'Authentication'
        TOURNAMENT = 'TOURNAMENT', 'Tournament'
        PLAYER = 'PLAYER', 'Player'
        PAYMENT = 'PAYMENT', 'Payment'
        COMMUNITY = 'COMMUNITY', 'Community'
        TEAM = 'TEAM', 'Team'
        ANALYTICS = 'ANALYTICS', 'Analytics'
        SYSTEM = 'SYSTEM', 'System'
        ADMIN = 'ADMIN', 'Admin'
        AI = 'AI', 'AI'
        CONTENT = 'CONTENT', 'Content'
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='audit_logs')
    action = models.CharField(max_length=20, choices=Action.choices)
    module = models.CharField(max_length=20, choices=Module.choices)
    
    object_id = models.CharField(max_length=100, blank=True, null=True)
    object_type = models.CharField(max_length=100, blank=True, null=True)
    
    changes = models.JSONField(default=dict)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)
    referer = models.URLField(blank=True, null=True)
    
    status_code = models.IntegerField(null=True, blank=True)
    error_message = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['action', 'module']),
            models.Index(fields=['-created_at']),
            models.Index(fields=['object_type', 'object_id']),
        ]
    
    def __str__(self):
        return f"{self.user.username if self.user else 'Anonymous'} - {self.action} - {self.module}"

class SystemLog(models.Model):
    class Severity(models.TextChoices):
        INFO = 'INFO', 'Info'
        WARNING = 'WARNING', 'Warning'
        ERROR = 'ERROR', 'Error'
        CRITICAL = 'CRITICAL', 'Critical'
        DEBUG = 'DEBUG', 'Debug'
    
    severity = models.CharField(max_length=10, choices=Severity.choices)
    message = models.TextField()
    source = models.CharField(max_length=255)
    stack_trace = models.TextField(blank=True, null=True)
    
    metadata = models.JSONField(default=dict)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.severity} - {self.message[:50]}..."
