from rest_framework import serializers
from .models import FactorySettlement, OutsourceSettlement, Payment, CostCalculation

class FactorySettlementSerializer(serializers.ModelSerializer):
    """工厂结算单序列化器"""
    class Meta:
        model = FactorySettlement
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'is_deleted']

class OutsourceSettlementSerializer(serializers.ModelSerializer):
    """外发结算单序列化器"""
    class Meta:
        model = OutsourceSettlement
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'is_deleted']

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        ref_name = 'finance.Payment'
        model = Payment
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'is_deleted']

class CostCalculationSerializer(serializers.ModelSerializer):
    """成本核算序列化器"""
    class Meta:
        model = CostCalculation
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'is_deleted']