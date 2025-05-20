from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()

class APILog(models.Model):
    """API调用日志"""
    timestamp = models.DateTimeField('调用时间', default=timezone.now)
    method = models.CharField('HTTP方法', max_length=10)
    endpoint = models.CharField('API端点', max_length=255)
    request_body = models.JSONField('请求体', null=True, blank=True)
    response_body = models.JSONField('响应体', null=True, blank=True)
    status_code = models.IntegerField('状态码')
    duration = models.IntegerField('耗时(ms)')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='用户')
    ip_address = models.GenericIPAddressField('IP地址', null=True, blank=True)
    user_agent = models.CharField('用户代理', max_length=255, null=True, blank=True)
    error_message = models.TextField('错误信息', null=True, blank=True)
    is_deleted = models.BooleanField('是否删除', default=False)

    class Meta:
        db_table = 'sys_api_log'
        ordering = ['-timestamp']
        verbose_name = 'API日志'
        verbose_name_plural = verbose_name

class SystemLog(models.Model):
    """系统日志"""
    LEVEL_CHOICES = [
        ('info', '信息'),
        ('warn', '警告'),
        ('error', '错误'),
        ('debug', '调试')
    ]

    timestamp = models.DateTimeField('记录时间', default=timezone.now)
    level = models.CharField('日志级别', max_length=10, choices=LEVEL_CHOICES)
    message = models.TextField('日志消息')
    module = models.CharField('模块', max_length=100)
    details = models.JSONField('详细信息', null=True, blank=True)
    stack_trace = models.TextField('堆栈跟踪', null=True, blank=True)
    is_deleted = models.BooleanField('是否删除', default=False)

    class Meta:
        db_table = 'sys_system_log'
        ordering = ['-timestamp']
        verbose_name = '系统日志'
        verbose_name_plural = verbose_name

class PerformanceMetric(models.Model):
    """性能指标"""
    timestamp = models.DateTimeField('记录时间', default=timezone.now)
    endpoint = models.CharField('API端点', max_length=255)
    response_time = models.IntegerField('响应时间(ms)')
    cpu_usage = models.FloatField('CPU使用率')
    memory_usage = models.FloatField('内存使用率')
    concurrent_requests = models.IntegerField('并发请求数')
    request_count = models.IntegerField('请求总数')
    is_deleted = models.BooleanField('是否删除', default=False)

    class Meta:
        db_table = 'sys_performance_metric'
        ordering = ['-timestamp']
        verbose_name = '性能指标'
        verbose_name_plural = verbose_name

class ConfigOverride(models.Model):
    """配置覆盖"""
    key = models.CharField('配置键', max_length=100, unique=True)
    value = models.JSONField('配置值')
    description = models.TextField('描述', null=True, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    expires_at = models.DateTimeField('过期时间', null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='创建者')
    is_deleted = models.BooleanField('是否删除', default=False)

    class Meta:
        db_table = 'sys_config_override'
        ordering = ['-created_at']
        verbose_name = '配置覆盖'
        verbose_name_plural = verbose_name

class UserSession(models.Model):
    """用户会话"""
    session_id = models.CharField('会话ID', max_length=100, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    ip_address = models.GenericIPAddressField('IP地址', null=True, blank=True)
    user_agent = models.CharField('用户代理', max_length=255, null=True, blank=True)
    started_at = models.DateTimeField('开始时间', auto_now_add=True)
    last_activity = models.DateTimeField('最后活动时间', auto_now=True)
    is_active = models.BooleanField('是否活跃', default=True)

    class Meta:
        db_table = 'sys_user_session'
        ordering = ['-last_activity']
        verbose_name = '用户会话'
        verbose_name_plural = verbose_name

class DebugMode(models.Model):
    """调试模式"""
    enabled = models.BooleanField('是否启用', default=False)
    enabled_at = models.DateTimeField('启用时间', auto_now_add=True)
    expires_at = models.DateTimeField('过期时间', null=True, blank=True)
    enabled_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='启用者')

    class Meta:
        db_table = 'sys_debug_mode'
        verbose_name = '调试模式'
        verbose_name_plural = verbose_name