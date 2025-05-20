from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from django.db.models import Q
from django.core.paginator import Paginator
from django.db import connection
from django.core.cache import cache
import psutil
import requests
import time

from .models_developer import APILog, SystemLog, PerformanceMetric, ConfigOverride
from .serializers_developer import (
    APILogSerializer, APILogQueryParamsSerializer,
    SystemLogSerializer, SystemLogQueryParamsSerializer,
    PerformanceMetricSerializer, PerformanceMetricQueryParamsSerializer,
    ConfigOverrideSerializer, APITestResultSerializer, SystemHealthStatusSerializer
)
from .utils import ResponseWrapper

class APILogViewSet(viewsets.ModelViewSet):
    """API日志视图集"""
    queryset = APILog.objects.filter(is_deleted=False)
    serializer_class = APILogSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        params = APILogQueryParamsSerializer(data=self.request.query_params)
        if not params.is_valid():
            return queryset
        
        validated_data = params.validated_data
        
        # 构建过滤条件
        filters = Q()
        if validated_data.get('start_time'):
            filters &= Q(timestamp__gte=validated_data['start_time'])
        if validated_data.get('end_time'):
            filters &= Q(timestamp__lte=validated_data['end_time'])
        if validated_data.get('method'):
            filters &= Q(method=validated_data['method'])
        if validated_data.get('endpoint'):
            filters &= Q(endpoint__icontains=validated_data['endpoint'])
        if validated_data.get('status_code'):
            filters &= Q(status_code=validated_data['status_code'])
        if validated_data.get('user_id'):
            filters &= Q(user_id=validated_data['user_id'])
        if validated_data.get('min_duration'):
            filters &= Q(duration__gte=validated_data['min_duration'])
        if validated_data.get('max_duration'):
            filters &= Q(duration__lte=validated_data['max_duration'])
        
        # 应用排序
        sort_by = validated_data.get('sort_by', 'timestamp')
        sort_order = validated_data.get('sort_order', 'desc')
        if sort_order == 'desc':
            sort_by = f'-{sort_by}'
        
        return queryset.filter(filters).order_by(sort_by)
    
    @action(detail=False, methods=['post'])
    def clear(self, request):
        """清除API日志"""
        try:
            before = request.data.get('before')
            if not before:
                return ResponseWrapper.error('缺少必要参数')
            
            count = APILog.objects.filter(
                timestamp__lte=before,
                is_deleted=False
            ).update(is_deleted=True)
            
            return ResponseWrapper.success({
                'success': True,
                'count': count
            })
        except Exception as e:
            return ResponseWrapper.error(str(e))

class SystemLogViewSet(viewsets.ModelViewSet):
    """系统日志视图集"""
    queryset = SystemLog.objects.filter(is_deleted=False)
    serializer_class = SystemLogSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        params = SystemLogQueryParamsSerializer(data=self.request.query_params)
        if not params.is_valid():
            return queryset
        
        validated_data = params.validated_data
        
        # 构建过滤条件
        filters = Q()
        if validated_data.get('start_time'):
            filters &= Q(timestamp__gte=validated_data['start_time'])
        if validated_data.get('end_time'):
            filters &= Q(timestamp__lte=validated_data['end_time'])
        if validated_data.get('level'):
            filters &= Q(level=validated_data['level'])
        if validated_data.get('module'):
            filters &= Q(module__icontains=validated_data['module'])
        if validated_data.get('message'):
            filters &= Q(message__icontains=validated_data['message'])
        
        # 应用排序
        sort_by = validated_data.get('sort_by', 'timestamp')
        sort_order = validated_data.get('sort_order', 'desc')
        if sort_order == 'desc':
            sort_by = f'-{sort_by}'
        
        return queryset.filter(filters).order_by(sort_by)
    
    @action(detail=False, methods=['post'])
    def clear(self, request):
        """清除系统日志"""
        try:
            before = request.data.get('before')
            level = request.data.get('level')
            if not before:
                return ResponseWrapper.error('缺少必要参数')
            
            filters = Q(timestamp__lte=before, is_deleted=False)
            if level:
                filters &= Q(level=level)
            
            count = SystemLog.objects.filter(filters).update(is_deleted=True)
            
            return ResponseWrapper.success({
                'success': True,
                'count': count
            })
        except Exception as e:
            return ResponseWrapper.error(str(e))

class PerformanceMetricViewSet(viewsets.ModelViewSet):
    """性能指标视图集"""
    queryset = PerformanceMetric.objects.filter(is_deleted=False)
    serializer_class = PerformanceMetricSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        params = PerformanceMetricQueryParamsSerializer(data=self.request.query_params)
        if not params.is_valid():
            return queryset
        
        validated_data = params.validated_data
        
        # 构建过滤条件
        filters = Q()
        if validated_data.get('start_time'):
            filters &= Q(timestamp__gte=validated_data['start_time'])
        if validated_data.get('end_time'):
            filters &= Q(timestamp__lte=validated_data['end_time'])
        if validated_data.get('endpoint'):
            filters &= Q(endpoint__icontains=validated_data['endpoint'])
        if validated_data.get('min_response_time'):
            filters &= Q(response_time__gte=validated_data['min_response_time'])
        if validated_data.get('max_response_time'):
            filters &= Q(response_time__lte=validated_data['max_response_time'])
        
        return queryset.filter(filters).order_by('-timestamp')

class ConfigOverrideViewSet(viewsets.ModelViewSet):
    """配置覆盖视图集"""
    queryset = ConfigOverride.objects.filter(is_deleted=False)
    serializer_class = ConfigOverrideSerializer
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()

class APITestView(APIView):
    """API测试视图"""
    def post(self, request):
        try:
            method = request.data.get('method')
            endpoint = request.data.get('endpoint')
            request_body = request.data.get('requestBody')
            headers = request.data.get('headers', {})
            
            if not all([method, endpoint]):
                return ResponseWrapper.error('缺少必要参数')
            
            start_time = time.time()
            response = requests.request(
                method=method,
                url=endpoint,
                json=request_body,
                headers=headers
            )
            duration = int((time.time() - start_time) * 1000)
            
            result = {
                'success': 200 <= response.status_code < 300,
                'status_code': response.status_code,
                'response_time': duration,
                'response_body': response.json() if response.headers.get('content-type', '').startswith('application/json') else None,
                'error_message': None if response.ok else response.text
            }
            
            serializer = APITestResultSerializer(data=result)
            if not serializer.is_valid():
                return ResponseWrapper.error(serializer.errors)
            
            return ResponseWrapper.success(serializer.validated_data)
        except Exception as e:
            return ResponseWrapper.error(str(e))

class SystemHealthView(APIView):
    """系统健康状态视图"""
    def get(self, request):
        try:
            # 检查服务状态
            services = []
            # 这里可以添加更多服务检查
            services.append(self._check_database())
            services.append(self._check_cache())
            
            # 系统资源使用情况
            memory = psutil.virtual_memory()
            cpu = psutil.cpu_percent(interval=1)
            
            status_data = {
                'status': self._determine_overall_status(services),
                'timestamp': timezone.now(),
                'services': services,
                'database': self._check_database(),
                'cache': self._check_cache(),
                'memory': {
                    'used': memory.used,
                    'total': memory.total,
                    'percentage': memory.percent
                },
                'cpu': {
                    'usage': cpu,
                    'cores': psutil.cpu_count()
                },
                'uptime': int(time.time() - psutil.boot_time())
            }
            
            serializer = SystemHealthStatusSerializer(data=status_data)
            if not serializer.is_valid():
                return ResponseWrapper.error(serializer.errors)
            
            return ResponseWrapper.success(serializer.validated_data)
        except Exception as e:
            return ResponseWrapper.error(str(e))
    
    def _check_database(self):
        """检查数据库状态"""
        try:
            start_time = time.time()
            with connection.cursor() as cursor:
                cursor.execute('SELECT 1')
            response_time = int((time.time() - start_time) * 1000)
            
            return {
                'name': 'database',
                'status': 'up',
                'response_time': response_time
            }
        except Exception as e:
            return {
                'name': 'database',
                'status': 'down',
                'message': str(e)
            }
    
    def _check_cache(self):
        """检查缓存状态"""
        try:
            cache.set('health_check', 'ok', 10)
            status = cache.get('health_check') == 'ok'
            
            return {
                'status': 'up' if status else 'down',
                'hit_rate': cache.get_stats().get('hit_rate', 0),
                'size': cache.get_stats().get('bytes', 0),
                'max_size': cache.get_stats().get('max_bytes', 0)
            }
        except Exception as e:
            return {
                'status': 'down',
                'message': str(e)
            }
    
    def _determine_overall_status(self, services):
        """确定整体系统状态"""
        if any(service['status'] == 'down' for service in services):
            return 'unhealthy'
        if any(service['status'] == 'degraded' for service in services):
            return 'degraded'
        return 'healthy'

class SessionManagementView(APIView):
    """会话管理视图"""
    def get(self, request):
        """获取当前活跃会话列表"""
        try:
            active_sessions = UserSession.objects.filter(is_active=True)
            unique_users = active_sessions.values('user').distinct().count()
            
            session_details = [{
                'session_id': session.session_id,
                'user_id': session.user.id,
                'username': session.user.username,
                'ip_address': session.ip_address,
                'started_at': session.started_at,
                'last_activity': session.last_activity
            } for session in active_sessions]
            
            return ResponseWrapper.success({
                'sessions': active_sessions.count(),
                'users': unique_users,
                'details': session_details
            })
        except Exception as e:
            return ResponseWrapper.error(str(e))
    
    def post(self, request):
        """终止用户会话"""
        try:
            session_id = request.data.get('session_id')
            if not session_id:
                return ResponseWrapper.error('缺少会话ID')
            
            session = UserSession.objects.filter(session_id=session_id, is_active=True).first()
            if not session:
                return ResponseWrapper.error('会话不存在或已终止')
            
            session.is_active = False
            session.save()
            
            return ResponseWrapper.success({
                'success': True
            })
        except Exception as e:
            return ResponseWrapper.error(str(e))

class DebugModeView(APIView):
    """调试模式视图"""
    def post(self, request):
        """开启/关闭调试模式"""
        try:
            enabled = request.data.get('enabled')
            duration = request.data.get('duration', 0)
            
            if enabled is None:
                return ResponseWrapper.error('缺少必要参数')
            
            debug_mode = DebugMode.objects.first() or DebugMode()
            debug_mode.enabled = enabled
            debug_mode.enabled_by = request.user
            
            if enabled and duration > 0:
                debug_mode.expires_at = timezone.now() + timezone.timedelta(minutes=duration)
            else:
                debug_mode.expires_at = None
            
            debug_mode.save()
            
            return ResponseWrapper.success({
                'success': True,
                'expiresAt': debug_mode.expires_at.isoformat() if debug_mode.expires_at else None
            })
        except Exception as e:
            return ResponseWrapper.error(str(e))