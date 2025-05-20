from rest_framework import serializers
from .models import (
    SystemMonitor, APIMetric, SystemLog, ConfigItem,
    WebSocketSession, WebSocketMessage
)
from apps.users.serializers import UserSerializer

class SystemMonitorSerializer(serializers.ModelSerializer):
    """系统监控数据序列化器"""
    component_display = serializers.CharField(source='get_component_display', read_only=True)
    
    class Meta:
        model = SystemMonitor
        fields = [
            'id', 'component', 'component_display', 'cpu_usage', 'memory_usage', 
            'disk_usage', 'network_in', 'network_out', 'timestamp'
        ]


class APIMetricSerializer(serializers.ModelSerializer):
    """API调用指标序列化器"""
    user_display = serializers.SerializerMethodField()
    
    class Meta:
        model = APIMetric
        fields = [
            'id', 'endpoint', 'method', 'status_code', 'response_time',
            'user', 'user_display', 'ip_address', 'timestamp'
        ]
    
    def get_user_display(self, obj):
        if obj.user:
            return obj.user.username
        return None


class SystemLogSerializer(serializers.ModelSerializer):
    """系统日志序列化器"""
    level_display = serializers.CharField(source='get_level_display', read_only=True)
    
    class Meta:
        model = SystemLog
        fields = [
            'id', 'logger_name', 'level', 'level_display', 
            'message', 'trace', 'timestamp'
        ]


class ConfigItemSerializer(serializers.ModelSerializer):
    """配置项序列化器"""
    environment_display = serializers.CharField(source='get_environment_display', read_only=True)
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    created_by_display = serializers.SerializerMethodField()
    
    class Meta:
        model = ConfigItem
        fields = [
            'id', 'key', 'value', 'description', 'is_sensitive',
            'environment', 'environment_display', 'type', 'type_display',
            'created_by', 'created_by_display', 'created_at', 'updated_at'
        ]
        extra_kwargs = {
            'value': {'write_only': True}  # 敏感配置值不在列表中显示
        }
    
    def get_created_by_display(self, obj):
        if obj.created_by:
            return obj.created_by.username
        return None
    
    def to_representation(self, instance):
        """敏感配置值在返回时被遮蔽"""
        ret = super().to_representation(instance)
        if instance.is_sensitive and 'value' in ret:
            ret['value'] = '******'
        return ret


class WebSocketSessionSerializer(serializers.ModelSerializer):
    """WebSocket会话序列化器"""
    user_display = serializers.SerializerMethodField()
    duration = serializers.SerializerMethodField()
    
    class Meta:
        model = WebSocketSession
        fields = [
            'id', 'session_id', 'user', 'user_display', 'client_ip',
            'connected_at', 'disconnected_at', 'is_active', 
            'last_activity', 'duration'
        ]
    
    def get_user_display(self, obj):
        return obj.user.username
    
    def get_duration(self, obj):
        """计算会话持续时间（秒）"""
        if obj.is_active:
            return None
        if obj.disconnected_at and obj.connected_at:
            return (obj.disconnected_at - obj.connected_at).total_seconds()
        return None


class WebSocketMessageSerializer(serializers.ModelSerializer):
    """WebSocket消息序列化器"""
    direction_display = serializers.CharField(source='get_direction_display', read_only=True)
    session_info = serializers.SerializerMethodField()
    
    class Meta:
        model = WebSocketMessage
        fields = [
            'id', 'session', 'session_info', 'direction', 'direction_display',
            'message', 'timestamp'
        ]
    
    def get_session_info(self, obj):
        return {
            'session_id': str(obj.session.session_id),
            'user': obj.session.user.username
        }
