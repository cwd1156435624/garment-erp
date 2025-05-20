from rest_framework import serializers
from .models import Equipment, MaintenanceRecord, FaultRecord

class EquipmentSerializer(serializers.ModelSerializer):
    """设备序列化器"""
    class Meta:
        model = Equipment
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'is_deleted']

class MaintenanceRecordSerializer(serializers.ModelSerializer):
    """设备维护记录序列化器"""
    class Meta:
        model = MaintenanceRecord
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'is_deleted']

class FaultRecordSerializer(serializers.ModelSerializer):
    """设备故障记录序列化器"""
    class Meta:
        model = FaultRecord
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'is_deleted']