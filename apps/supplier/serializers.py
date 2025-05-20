from rest_framework import serializers
from .models import Supplier, SupplierPerformance, SupplierContract, SupplierEvaluation

class SupplierSerializer(serializers.ModelSerializer):
    """供应商序列化器"""
    class Meta:
        model = Supplier
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'is_deleted']

class SupplierPerformanceSerializer(serializers.ModelSerializer):
    """供应商绩效序列化器"""
    class Meta:
        model = SupplierPerformance
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'is_deleted']

class SupplierContractSerializer(serializers.ModelSerializer):
    """供应商合同序列化器"""
    class Meta:
        model = SupplierContract
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'is_deleted']

class SupplierEvaluationSerializer(serializers.ModelSerializer):
    """供应商评估序列化器"""
    class Meta:
        model = SupplierEvaluation
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'is_deleted']