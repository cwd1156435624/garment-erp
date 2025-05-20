import time
import logging
import psutil
import os
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from prometheus_client import Counter, Histogram, Gauge

logger = logging.getLogger('apps')

# 定义Prometheus指标
HTTP_REQUEST_COUNTER = Counter(
    'http_request_total',
    'Total number of HTTP requests',
    ['method', 'endpoint', 'status']
)

HTTP_REQUEST_LATENCY = Histogram(
    'http_request_latency_seconds',
    'HTTP request latency in seconds',
    ['method', 'endpoint']
)

ACTIVE_REQUESTS = Gauge(
    'http_active_requests',
    'Number of active HTTP requests',
    ['method']
)

SYSTEM_MEMORY_USAGE = Gauge(
    'system_memory_usage_bytes',
    'System memory usage in bytes',
    ['type']
)

SYSTEM_CPU_USAGE = Gauge(
    'system_cpu_usage_percent',
    'System CPU usage in percent',
    []
)

SYSTEM_DISK_USAGE = Gauge(
    'system_disk_usage_bytes',
    'System disk usage in bytes',
    ['type', 'mount']
)

class MonitoringMiddleware(MiddlewareMixin):
    """监控中间件，用于记录请求日志、性能指标和异常信息"""
    
    def process_request(self, request):
        # 记录请求开始时间
        request.start_time = time.time()
        
        # 增加活跃请求计数
        ACTIVE_REQUESTS.labels(method=request.method).inc()
        
        # 记录系统资源使用情况
        self._record_system_metrics()
        
        # 记录请求日志
        logger.info(
            f'Request: {request.method} {request.path} '
            f'from {request.META.get("REMOTE_ADDR")}'
        )
    
    def process_response(self, request, response):
        if hasattr(request, 'start_time'):
            # 计算请求处理时间
            duration = time.time() - request.start_time
            
            # 记录Prometheus指标
            HTTP_REQUEST_COUNTER.labels(
                method=request.method,
                endpoint=request.path,
                status=response.status_code
            ).inc()
            
            HTTP_REQUEST_LATENCY.labels(
                method=request.method,
                endpoint=request.path
            ).observe(duration)
            
            # 减少活跃请求计数
            ACTIVE_REQUESTS.labels(method=request.method).dec()
            
            # 记录响应日志
            logger.info(
                f'Response: {request.method} {request.path} '
                f'status={response.status_code} '
                f'duration={duration:.3f}s'
            )
        
        return response
    
    def process_exception(self, request, exception):
        # 减少活跃请求计数
        ACTIVE_REQUESTS.labels(method=request.method).dec()
        
        # 记录异常日志
        logger.error(
            f'Exception in {request.method} {request.path}: '
            f'{str(exception)}',
            exc_info=True
        )
    
    def _record_system_metrics(self):
        """记录系统资源使用情况"""
        # 记录内存使用情况
        memory = psutil.virtual_memory()
        SYSTEM_MEMORY_USAGE.labels(type='total').set(memory.total)
        SYSTEM_MEMORY_USAGE.labels(type='available').set(memory.available)
        SYSTEM_MEMORY_USAGE.labels(type='used').set(memory.used)
        
        # 记录CPU使用情况
        SYSTEM_CPU_USAGE.set(psutil.cpu_percent(interval=None))
        
        # 记录磁盘使用情况
        for partition in psutil.disk_partitions():
            if os.path.exists(partition.mountpoint):
                usage = psutil.disk_usage(partition.mountpoint)
                SYSTEM_DISK_USAGE.labels(type='total', mount=partition.mountpoint).set(usage.total)
                SYSTEM_DISK_USAGE.labels(type='used', mount=partition.mountpoint).set(usage.used)
                SYSTEM_DISK_USAGE.labels(type='free', mount=partition.mountpoint).set(usage.free)