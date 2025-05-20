from rest_framework import serializers
from .models import Warehouse, DeliveryTask, FinishedGoods

class WarehouseSerializer(serializers.ModelSerializer):
    """仓库序列化器"""
    class Meta:
        model = Warehouse
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'is_deleted']

class DeliveryTaskSerializer(serializers.ModelSerializer):
    """送货任务序列化器"""
    class Meta:
        model = DeliveryTask
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'is_deleted']

class FinishedGoodsSerializer(serializers.ModelSerializer):
    """成品库存序列化器"""
    class Meta:
        model = FinishedGoods
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'is_deleted']