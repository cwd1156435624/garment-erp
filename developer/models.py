from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.users.models import User
import uuid

class SystemMonitor(models.Model):
    """系统监控数据模型"""
    COMPONENT_CHOICES = (
        ('app_server', _('应用服务器')),
        ('db_server', _('数据库服务器')),
        ('file_server', _('文件服务器')),
        ('cache_server', _('缓存服务器')),
        ('queue_server', _('队列服务器')),
    )
    
    component = models.CharField(_('组件名称'), max_length=50, choices=COMPONENT_CHOICES)
    cpu_usage = models.FloatField(_('CPU使用率'), help_text='百分比')
    memory_usage = models.FloatField(_('内存使用率'), help_text='百分比')
    disk_usage = models.FloatField(_('磁盘使用率'), help_text='百分比')
    network_in = models.FloatField(_('网络入流量'), help_text='MB/s')
    network_out = models.FloatField(_('网络出流量'), help_text='MB/s')
    timestamp = models.DateTimeField(_('记录时间'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('系统监控数据')
        verbose_name_plural = _('系统监控数据')
        ordering = ['-timestamp']
    
    def __str__(self):
        return f'{self.get_component_display()} - {self.timestamp}'


class APIMetric(models.Model):
    """API调用指标模型"""
    METHOD_CHOICES = (
        ('GET', 'GET'),
        ('POST', 'POST'),
        ('PUT', 'PUT'),
        ('DELETE', 'DELETE'),
        ('PATCH', 'PATCH'),
    )
    
    endpoint = models.CharField(_('API端点'), max_length=255)
    method = models.CharField(_('请求方法'), max_length=10, choices=METHOD_CHOICES)
    status_code = models.IntegerField(_('状态码'))
    response_time = models.IntegerField(_('响应时间'), help_text='毫秒')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_('用户'))
    ip_address = models.GenericIPAddressField(_('IP地址'), null=True, blank=True)
    timestamp = models.DateTimeField(_('记录时间'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('API调用指标')
        verbose_name_plural = _('API调用指标')
        ordering = ['-timestamp']
    
    def __str__(self):
        return f'{self.method} {self.endpoint} - {self.status_code}'


class SystemLog(models.Model):
    """系统日志模型"""
    LEVEL_CHOICES = (
        ('DEBUG', _('调试')),
        ('INFO', _('信息')),
        ('WARNING', _('警告')),
        ('ERROR', _('错误')),
        ('CRITICAL', _('严重')),
    )
    
    logger_name = models.CharField(_('日志器名称'), max_length=100)
    level = models.CharField(_('日志级别'), max_length=10, choices=LEVEL_CHOICES)
    message = models.TextField(_('日志消息'))
    trace = models.TextField(_('堆栈跟踪'), null=True, blank=True)
    timestamp = models.DateTimeField(_('记录时间'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('系统日志')
        verbose_name_plural = _('系统日志')
        ordering = ['-timestamp']
    
    def __str__(self):
        return f'{self.level} - {self.logger_name} - {self.timestamp}'


class ConfigItem(models.Model):
    """配置项模型"""
    ENVIRONMENT_CHOICES = (
        ('development', _('开发环境')),
        ('testing', _('测试环境')),
        ('production', _('生产环境')),
    )
    
    TYPE_CHOICES = (
        ('app', _('应用配置')),
        ('api', _('API配置')),
        ('db', _('数据库配置')),
        ('cache', _('缓存配置')),
        ('queue', _('队列配置')),
    )
    
    key = models.CharField(_('配置键'), max_length=100)
    value = models.TextField(_('配置值'))
    description = models.TextField(_('描述'), null=True, blank=True)
    is_sensitive = models.BooleanField(_('敏感配置'), default=False, help_text='敏感配置会被加密存储')
    environment = models.CharField(_('环境'), max_length=20, choices=ENVIRONMENT_CHOICES)
    type = models.CharField(_('类型'), max_length=20, choices=TYPE_CHOICES)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_configs', verbose_name=_('创建人'))
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    
    class Meta:
        verbose_name = _('配置项')
        verbose_name_plural = _('配置项')
        unique_together = ('key', 'environment')
        ordering = ['type', 'key']
    
    def __str__(self):
        return f'{self.key} ({self.get_environment_display()})'


class WebSocketSession(models.Model):
    """WebSocket会话模型"""
    session_id = models.UUIDField(_('会话ID'), default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('用户'))
    client_ip = models.GenericIPAddressField(_('客户端IP'), null=True, blank=True)
    connected_at = models.DateTimeField(_('连接时间'), auto_now_add=True)
    disconnected_at = models.DateTimeField(_('断开时间'), null=True, blank=True)
    is_active = models.BooleanField(_('是否活跃'), default=True)
    last_activity = models.DateTimeField(_('最后活动时间'), auto_now=True)
    
    class Meta:
        verbose_name = _('WebSocket会话')
        verbose_name_plural = _('WebSocket会话')
        ordering = ['-connected_at']
    
    def __str__(self):
        return f'{self.user.username} - {self.session_id}'


class WebSocketMessage(models.Model):
    """WebSocket消息模型"""
    DIRECTION_CHOICES = (
        ('incoming', _('接收')),
        ('outgoing', _('发送')),
    )
    
    session = models.ForeignKey(WebSocketSession, on_delete=models.CASCADE, related_name='messages', verbose_name=_('会话'))
    direction = models.CharField(_('方向'), max_length=10, choices=DIRECTION_CHOICES)
    message = models.TextField(_('消息内容'))
    timestamp = models.DateTimeField(_('时间戳'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('WebSocket消息')
        verbose_name_plural = _('WebSocket消息')
        ordering = ['-timestamp']
    
    def __str__(self):
        return f'{self.get_direction_display()} - {self.timestamp}'
