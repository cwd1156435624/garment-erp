from rest_framework import serializers
from .models import SystemParameter, OperationLog

class SystemParameterSerializer(serializers.ModelSerializer):
    """系统参数序列化器"""
    class Meta:
        model = SystemParameter
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'is_deleted']

class OperationLogSerializer(serializers.ModelSerializer):
    """操作日志序列化器"""
    class Meta:
        model = OperationLog
        fields = '__all__'