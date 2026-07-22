from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.db import connections
from django.db.utils import OperationalError
from django.core.cache import cache
import datetime
import shutil

@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """Health check endpoint for Docker and monitoring"""
    
    status = {
        'status': 'healthy',
        'timestamp': datetime.datetime.now().isoformat(),
        'services': {}
    }
    
    # Check database
    try:
        db_conn = connections['default']
        db_conn.cursor()
        status['services']['database'] = {'status': 'healthy'}
    except OperationalError:
        status['status'] = 'unhealthy'
        status['services']['database'] = {'status': 'unhealthy', 'error': 'Cannot connect to database'}
    
    # Check Redis
    try:
        cache.set('health_check', 'ok', 5)
        if cache.get('health_check') == 'ok':
            status['services']['redis'] = {'status': 'healthy'}
        else:
            status['services']['redis'] = {'status': 'unhealthy', 'error': 'Redis cache test failed'}
    except Exception as e:
        status['status'] = 'unhealthy'
        status['services']['redis'] = {'status': 'unhealthy', 'error': str(e)}
    
    # Check disk space
    disk_usage = shutil.disk_usage('/')
    status['services']['disk'] = {
        'status': 'healthy' if disk_usage.free > 1000000000 else 'warning',
        'free_gb': round(disk_usage.free / (1024**3), 2),
        'used_gb': round(disk_usage.used / (1024**3), 2),
        'total_gb': round(disk_usage.total / (1024**3), 2)
    }
    
    # System info
    status['system'] = {
        'python_version': __import__('sys').version,
        'django_version': __import__('django').get_version(),
    }
    
    return Response(status)

@api_view(['GET'])
@permission_classes([AllowAny])
def readiness_check(request):
    """Readiness check for Kubernetes/Render"""
    
    # Check if database is ready
    try:
        db_conn = connections['default']
        db_conn.cursor()
        return Response({'status': 'ready'}, status=200)
    except OperationalError:
        return Response({'status': 'not_ready'}, status=503)
