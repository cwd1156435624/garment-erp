from rest_framework import serializers
from .models import Customer, TaskReminder

class CustomerSerializer(serializers.ModelSerializer):
    """客户序列化器"""
    class Meta:
        model = Customer
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'is_deleted']

class TaskReminderSerializer(serializers.ModelSerializer):
    """任务提醒序列化器"""
    class Meta:
        model = TaskReminder
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'is_deleted']