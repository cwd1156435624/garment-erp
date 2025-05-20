from rest_framework import serializers
from .models import Order, ProductionPlan, CuttingTask, ProductionException, Batch

class OrderSerializer(serializers.ModelSerializer):
    """订单序列化器"""
    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'is_deleted']

class ProductionPlanSerializer(serializers.ModelSerializer):
    """生产计划序列化器"""
    class Meta:
        model = ProductionPlan
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'is_deleted']

class CuttingTaskSerializer(serializers.ModelSerializer):
    """裁剪任务序列化器"""
    class Meta:
        model = CuttingTask
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'is_deleted']

class ProductionExceptionSerializer(serializers.ModelSerializer):
    """生产异常序列化器"""
    class Meta:
        model = ProductionException
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'is_deleted']

class BatchSerializer(serializers.ModelSerializer):
    """生产批次序列化器"""
    class Meta:
        model = Batch
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'is_deleted']