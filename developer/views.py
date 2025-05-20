from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from django.db.models import Avg, Count, Sum, Max, Min
from django.core.paginator import Paginator
from django.db import connection
from django.core.cache import cache
from datetime import timedelta
import psutil
import socket
import json
import requests
import time

from .models import (
    SystemMonitor, APIMetric, SystemLog, ConfigItem,
    WebSocketSession, WebSocketMessage
)
from .serializers import (
    SystemMonitorSerializer, APIMetricSerializer, SystemLogSerializer,
    ConfigItemSerializer, WebSocketSessionSerializer, WebSocketMessageSerializer
)


class DeveloperPermission(permissions.BasePermission):
    """开发者权限类"""
    def has_permission(self, request, view):
        # 只允许管理员或者开发者角色的用户访问
        return request.user.is_authenticated and (
            request.user.is_staff or 
            request.user.is_superuser or
            request.user.roles.filter(name__icontains='developer').exists()
        )


class SystemMonitorViewSet(viewsets.ModelViewSet):
    """系统监控视图集"""
    queryset = SystemMonitor.objects.all()
    serializer_class = SystemMonitorSerializer
    permission_classes = [DeveloperPermission]
    filterset_fields = ['component']
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """获取当前系统状态"""
        try:
            # 获取当前系统资源使用情况
            cpu_usage = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            net_io = psutil.net_io_counters()
            
            data = {
                'cpu_usage': cpu_usage,
                'memory_usage': memory.percent,
                'disk_usage': disk.percent,
                'network_stats': {
                    'bytes_sent': net_io.bytes_sent,
                    'bytes_recv': net_io.bytes_recv,
                },
                'hostname': socket.gethostname(),
                'timestamp': timezone.now().isoformat(),
            }
            
            # 保存到数据库
            SystemMonitor.objects.create(
                component='app_server',
                cpu_usage=cpu_usage,
                memory_usage=memory.percent,
                disk_usage=disk.percent,
                network_in=net_io.bytes_recv / (1024 * 1024),  # 转换为MB
                network_out=net_io.bytes_sent / (1024 * 1024)  # 转换为MB
            )
            
            return Response(data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """获取系统监控数据汇总"""
        # 计算过去24小时的数据
        last_day = timezone.now() - timedelta(days=1)
        summary = SystemMonitor.objects.filter(timestamp__gte=last_day).aggregate(
            avg_cpu=Avg('cpu_usage'),
            max_cpu=Max('cpu_usage'),
            avg_memory=Avg('memory_usage'),
            max_memory=Max('memory_usage'),
            avg_disk=Avg('disk_usage'),
            count=Count('id')
        )
        
        # 按组件类型分组统计
        components = SystemMonitor.objects.filter(timestamp__gte=last_day).values('component').annotate(
            avg_cpu=Avg('cpu_usage'),
            avg_memory=Avg('memory_usage'),
            count=Count('id')
        )
        
        return Response({
            'summary': summary,
            'components': components
        })


class APIMetricViewSet(viewsets.ModelViewSet):
    """接口指标视图集"""
    queryset = APIMetric.objects.all()
    serializer_class = APIMetricSerializer
    permission_classes = [DeveloperPermission]
    filterset_fields = ['method', 'status_code', 'endpoint']
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """获取API调用统计信息"""
        # 获取时间范围
        days = int(request.query_params.get('days', 1))
        start_time = timezone.now() - timedelta(days=days)
        
        # 总体统计
        overall = APIMetric.objects.filter(timestamp__gte=start_time).aggregate(
            total_calls=Count('id'),
            avg_response_time=Avg('response_time'),
            success_count=Count('id', filter=models.Q(status_code__lt=400)),
            error_count=Count('id', filter=models.Q(status_code__gte=400))
        )
        
        # 计算成功率
        if overall['total_calls'] > 0:
            overall['success_rate'] = (overall['success_count'] / overall['total_calls']) * 100
        else:
            overall['success_rate'] = 0
        
        # 按方法分组
        by_method = APIMetric.objects.filter(timestamp__gte=start_time).values('method').annotate(
            count=Count('id'),
            avg_time=Avg('response_time')
        )
        
        # 按状态码分组
        by_status = APIMetric.objects.filter(timestamp__gte=start_time).values('status_code').annotate(
            count=Count('id')
        )
        
        # 最慢的接口
        slowest_apis = APIMetric.objects.filter(timestamp__gte=start_time).values('endpoint', 'method').annotate(
            avg_time=Avg('response_time'),
            count=Count('id')
        ).order_by('-avg_time')[:10]
        
        return Response({
            'overall': overall,
            'by_method': by_method,
            'by_status': by_status,
            'slowest_apis': slowest_apis
        })


class SystemLogViewSet(viewsets.ModelViewSet):
    """系统日志视图集"""
    queryset = SystemLog.objects.all()
    serializer_class = SystemLogSerializer
    permission_classes = [DeveloperPermission]
    filterset_fields = ['level', 'logger_name']
    search_fields = ['message', 'logger_name']
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """获取日志汇总信息"""
        # 获取时间范围
        days = int(request.query_params.get('days', 1))
        start_time = timezone.now() - timedelta(days=days)
        
        # 按级别统计
        by_level = SystemLog.objects.filter(timestamp__gte=start_time).values('level').annotate(
            count=Count('id')
        )
        
        # 按日志器统计
        by_logger = SystemLog.objects.filter(timestamp__gte=start_time).values('logger_name').annotate(
            count=Count('id')
        )
        
        # 最新错误
        recent_errors = SystemLog.objects.filter(
            timestamp__gte=start_time,
            level__in=['ERROR', 'CRITICAL']
        ).order_by('-timestamp')[:10]
        recent_errors_serializer = self.get_serializer(recent_errors, many=True)
        
        return Response({
            'by_level': by_level,
            'by_logger': by_logger,
            'recent_errors': recent_errors_serializer.data,
            'total_logs': SystemLog.objects.filter(timestamp__gte=start_time).count()
        })


class ConfigItemViewSet(viewsets.ModelViewSet):
    """配置项视图集"""
    queryset = ConfigItem.objects.all()
    serializer_class = ConfigItemSerializer
    permission_classes = [DeveloperPermission]
    filterset_fields = ['environment', 'type', 'is_sensitive']
    search_fields = ['key', 'description']
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=False, methods=['get'])
    def by_environment(self, request):
        """按环境分组获取配置"""
        env = request.query_params.get('environment', 'production')
        configs = ConfigItem.objects.filter(environment=env)
        
        # 按类型分组
        result = {}
        for config_type in dict(ConfigItem.TYPE_CHOICES).keys():
            type_configs = configs.filter(type=config_type)
            serializer = self.get_serializer(type_configs, many=True)
            result[config_type] = serializer.data
        
        return Response(result)
    
    @action(detail=True, methods=['get'])
    def reveal(self, request, pk=None):
        """显示敏感配置的实际值（需要特殊权限）"""
        # 只有超级管理员可以查看敏感配置的实际值
        if not request.user.is_superuser:
            return Response(
                {'detail': '只有超级管理员可以查看敏感配置的实际值'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        config = self.get_object()
        serializer = self.get_serializer(config)
        data = serializer.data
        
        # 如果是敏感配置，显示实际值
        if config.is_sensitive:
            data['value'] = config.value
        
        return Response(data)


class WebSocketSessionViewSet(viewsets.ModelViewSet):
    """会话管理视图集"""
    queryset = WebSocketSession.objects.all()
    serializer_class = WebSocketSessionSerializer
    permission_classes = [DeveloperPermission]
    filterset_fields = ['is_active', 'user']
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """获取活跃的WebSocket会话"""
        active_sessions = WebSocketSession.objects.filter(is_active=True)
        serializer = self.get_serializer(active_sessions, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        """关闭指定的WebSocket会话"""
        session = self.get_object()
        
        if not session.is_active:
            return Response({'detail': '会话已经关闭'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 标记会话为关闭状态
        session.is_active = False
        session.disconnected_at = timezone.now()
        session.save()
        
        # TODO: 实际关闭WebSocket连接的逻辑，需要与WebSocket服务集成
        
        return Response({'detail': '会话已关闭'}, status=status.HTTP_200_OK)


class WebSocketMessageViewSet(viewsets.ModelViewSet):
    """消息管理视图集"""
    queryset = WebSocketMessage.objects.all()
    serializer_class = WebSocketMessageSerializer
    permission_classes = [DeveloperPermission]
    filterset_fields = ['session', 'direction']
    search_fields = ['message']
    
    @action(detail=False, methods=['get'])
    def by_session(self, request):
        """获取指定会话的消息"""
        session_id = request.query_params.get('session_id')
        if not session_id:
            return Response({'detail': '需要提供会话ID'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            session = WebSocketSession.objects.get(session_id=session_id)
            messages = WebSocketMessage.objects.filter(session=session).order_by('timestamp')
            serializer = self.get_serializer(messages, many=True)
            return Response(serializer.data)
        except WebSocketSession.DoesNotExist:
            return Response({'detail': '会话不存在'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['post'])
    def send_test(self, request):
        """发送测试WebSocket消息"""
        session_id = request.data.get('session_id')
        message = request.data.get('message')
        
        if not session_id or not message:
            return Response({'detail': '需要提供会话ID和消息内容'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            session = WebSocketSession.objects.get(session_id=session_id, is_active=True)
            
            # 记录发送的消息
            websocket_message = WebSocketMessage.objects.create(
                session=session,
                direction='outgoing',
                message=message
            )
            
            # TODO: 实际发送WebSocket消息的逻辑，需要与WebSocket服务集成
            
            serializer = self.get_serializer(websocket_message)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except WebSocketSession.DoesNotExist:
            return Response({'detail': '会话不存在或已关闭'}, status=status.HTTP_404_NOT_FOUND)


# 从 apps/system/views_developer.py 合并的视图类

class APITestView(APIView):
    """接口测试视图"""
    permission_classes = [DeveloperPermission]
    
    def post(self, request):
        """测试API端点访问"""
        method = request.data.get('method', 'GET').upper()
        url = request.data.get('url')
        headers = request.data.get('headers', {})
        params = request.data.get('params', {})
        body = request.data.get('body', {})
        timeout = request.data.get('timeout', 10)
        
        if not url:
            return Response({'detail': '需要提供URL'}, status=status.HTTP_400_BAD_REQUEST)
        
        if method not in ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']:
            return Response({'detail': '不支持的HTTP方法'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            start_time = time.time()
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=body if method in ['POST', 'PUT', 'PATCH'] else None,
                timeout=timeout
            )
            end_time = time.time()
            
            # 尝试解析JSON响应
            try:
                response_data = response.json()
            except:
                response_data = response.text
            
            result = {
                'status_code': response.status_code,
                'headers': dict(response.headers),
                'data': response_data,
                'time_taken': round(end_time - start_time, 3)
            }
            
            return Response(result)
        except requests.exceptions.Timeout:
            return Response({'detail': '请求超时'}, status=status.HTTP_504_GATEWAY_TIMEOUT)
        except requests.exceptions.ConnectionError:
            return Response({'detail': '连接错误'}, status=status.HTTP_502_BAD_GATEWAY)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SystemHealthView(APIView):
    """系统健康状态视图"""
    permission_classes = [DeveloperPermission]
    
    def get(self, request):
        """获取系统健康状态"""
        # 检查各个服务的状态
        services = {
            'database': self._check_database(),
            'cache': self._check_cache(),
            'system_resources': {
                'status': 'healthy',
                'cpu_usage': psutil.cpu_percent(),
                'memory_usage': psutil.virtual_memory().percent,
                'disk_usage': psutil.disk_usage('/').percent
            }
        }
        
        # 确定整体系统状态
        overall_status = self._determine_overall_status(services)
        
        response_data = {
            'status': overall_status,
            'timestamp': timezone.now(),
            'services': services
        }
        
        return Response(response_data)
    
    def _check_database(self):
        """检查数据库状态"""
        try:
            # 测量数据库响应时间
            start_time = time.time()
            with connection.cursor() as cursor:
                cursor.execute('SELECT 1')
                cursor.fetchone()
            end_time = time.time()
            response_time = end_time - start_time
            
            return {
                'status': 'healthy',
                'response_time': round(response_time, 3),
                'connections': len(connection.connection.notices) if hasattr(connection.connection, 'notices') else 'N/A'
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e)
            }
    
    def _check_cache(self):
        """检查缓存状态"""
        try:
            # 测量缓存响应时间
            test_key = 'health_check_test'
            test_value = 'ok'
            
            start_time = time.time()
            cache.set(test_key, test_value, 10)
            result = cache.get(test_key)
            end_time = time.time()
            
            cache.delete(test_key)
            
            if result == test_value:
                return {
                    'status': 'healthy',
                    'response_time': round(end_time - start_time, 3)
                }
            else:
                return {
                    'status': 'degraded',
                    'error': '缓存读写不一致'
                }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e)
            }
    
    def _determine_overall_status(self, services):
        """确定整体系统状态"""
        if any(service.get('status') == 'unhealthy' for service in services.values() if isinstance(service, dict)):
            return 'unhealthy'
        
        if any(service.get('status') == 'degraded' for service in services.values() if isinstance(service, dict)):
            return 'degraded'
        
        # 检查系统资源使用情况
        system_resources = services.get('system_resources', {})
        if system_resources.get('cpu_usage', 0) > 90 or system_resources.get('memory_usage', 0) > 90 or system_resources.get('disk_usage', 0) > 90:
            return 'degraded'
        
        return 'healthy'


class SessionManagementView(APIView):
    """会话管理视图"""
    permission_classes = [DeveloperPermission]
    
    def get(self, request):
        """获取当前活跃会话列表"""
        # 注意：这里只是示例，实际实现需要根据会话存储方式调整
        from django.contrib.sessions.models import Session
        
        active_sessions = []
        for session in Session.objects.filter(expire_date__gt=timezone.now()):
            session_data = session.get_decoded()
            user_id = session_data.get('_auth_user_id')
            
            if user_id:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                try:
                    user = User.objects.get(pk=user_id)
                    active_sessions.append({
                        'session_key': session.session_key,
                        'user': user.username,
                        'ip_address': session_data.get('ip', 'unknown'),
                        'last_activity': session.expire_date - timedelta(seconds=settings.SESSION_COOKIE_AGE),
                        'expire_date': session.expire_date
                    })
                except User.DoesNotExist:
                    pass
        
        return Response(active_sessions)
    
    def post(self, request):
        """终止用户会话"""
        session_key = request.data.get('session_key')
        
        if not session_key:
            return Response({'detail': '需要提供会话密钥'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            from django.contrib.sessions.models import Session
            session = Session.objects.get(session_key=session_key)
            session.delete()
            return Response({'status': 'success', 'detail': '会话已终止'})
        except Session.DoesNotExist:
            return Response({'detail': '会话不存在'}, status=status.HTTP_404_NOT_FOUND)


class DebugModeView(APIView):
    """调试模式视图"""
    permission_classes = [DeveloperPermission]
    
    def post(self, request):
        """开启/关闭调试模式"""
        from django.conf import settings
        
        enable = request.data.get('enable')
        if enable is None:
            return Response({'detail': '需要提供 enable 参数'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 注意：在生产环境中不应该允许这种操作
        # 这里只是示例，实际实现可能需要使用环境变量或配置文件
        try:
            # 这里使用缓存来模拟调试模式切换
            # 实际应用中可能需要重启服务或其他方式
            cache.set('DEBUG_MODE', bool(enable), None)
            
            current_state = {
                'debug_mode': bool(enable),
                'settings_debug': settings.DEBUG,
                'timestamp': timezone.now()
            }
            
            return Response(current_state)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
