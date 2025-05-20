from rest_framework import serializers
from .models_alerts import SystemAlert
from apps.users.serializers import UserSerializer

class SystemAlertSerializer(serializers.ModelSerializer):
    """系统告警序列化器"""
    created_by_info = UserSerializer(source='created_by', read_only=True, allow_null=True)
    resolved_by_info = UserSerializer(source='resolved_by', read_only=True, allow_null=True)
    
    class Meta:
        model = SystemAlert
        fields = ['id', 'title', 'content', 'severity', 'status', 'source',
                'created_by', 'created_by_info', 'created_at', 'updated_at',
                'resolved_by', 'resolved_by_info', 'resolved_at', 'resolution_comment']
        read_only_fields = ['created_by', 'created_at', 'updated_at']