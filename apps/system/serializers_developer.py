from rest_framework import serializers
from django.utils import timezone
from .models_developer import APILog, SystemLog, PerformanceMetric, ConfigOverride

class APILogSerializer(serializers.ModelSerializer):
    """API日志序列化器"""
    class Meta:
        model = APILog
        exclude = ['is_deleted']
        read_only_fields = ['timestamp']

class APILogQueryParamsSerializer(serializers.Serializer):
    """API日志查询参数序列化器"""
    start_time = serializers.DateTimeField(required=False)
    end_time = serializers.DateTimeField(required=False)
    method = serializers.CharField(required=False)
    endpoint = serializers.CharField(required=False)
    status_code = serializers.IntegerField(required=False)
    user_id = serializers.CharField(required=False)
    min_duration = serializers.IntegerField(required=False)
    max_duration = serializers.IntegerField(required=False)
    page = serializers.IntegerField(required=False, min_value=1, default=1)
    page_size = serializers.IntegerField(required=False, min_value=1, max_value=100, default=20)
    sort_by = serializers.CharField(required=False)
    sort_order = serializers.ChoiceField(choices=['asc', 'desc'], required=False, default='desc')

class SystemLogSerializer(serializers.ModelSerializer):
    """系统日志序列化器"""
    class Meta:
        model = SystemLog
        exclude = ['is_deleted']
        read_only_fields = ['timestamp']

class SystemLogQueryParamsSerializer(serializers.Serializer):
    """系统日志查询参数序列化器"""
    start_time = serializers.DateTimeField(required=False)
    end_time = serializers.DateTimeField(required=False)
    level = serializers.ChoiceField(choices=['info', 'warn', 'error', 'debug'], required=False)
    module = serializers.CharField(required=False)
    message = serializers.CharField(required=False)
    page = serializers.IntegerField(required=False, min_value=1, default=1)
    page_size = serializers.IntegerField(required=False, min_value=1, max_value=100, default=20)
    sort_by = serializers.CharField(required=False)
    sort_order = serializers.ChoiceField(choices=['asc', 'desc'], required=False, default='desc')

class PerformanceMetricSerializer(serializers.ModelSerializer):
    """性能指标序列化器"""
    class Meta:
        model = PerformanceMetric
        exclude = ['is_deleted']
        read_only_fields = ['timestamp']

class PerformanceMetricQueryParamsSerializer(serializers.Serializer):
    """性能指标查询参数序列化器"""
    start_time = serializers.DateTimeField(required=False)
    end_time = serializers.DateTimeField(required=False)
    endpoint = serializers.CharField(required=False)
    min_response_time = serializers.IntegerField(required=False)
    max_response_time = serializers.IntegerField(required=False)
    page = serializers.IntegerField(required=False, min_value=1, default=1)
    page_size = serializers.IntegerField(required=False, min_value=1, max_value=100, default=20)

class ConfigOverrideSerializer(serializers.ModelSerializer):
    """配置覆盖序列化器"""
    class Meta:
        model = ConfigOverride
        exclude = ['is_deleted']
        read_only_fields = ['created_at', 'updated_at', 'created_by']

class APITestResultSerializer(serializers.Serializer):
    """API测试结果序列化器"""
    success = serializers.BooleanField()
    status_code = serializers.IntegerField()
    response_time = serializers.IntegerField()
    response_body = serializers.JSONField(required=False)
    error_message = serializers.CharField(required=False)

class SystemHealthStatusSerializer(serializers.Serializer):
    """系统健康状态序列化器"""
    status = serializers.ChoiceField(choices=['healthy', 'degraded', 'unhealthy'])
    timestamp = serializers.DateTimeField(default=timezone.now)
    services = serializers.ListField(child=serializers.DictField())
    database = serializers.DictField()
    cache = serializers.DictField()
    memory = serializers.DictField()
    cpu = serializers.DictField()
    uptime = serializers.IntegerField()