from rest_framework import serializers
from .models import ReportTemplate, SavedReport
from apps.users.serializers import UserSerializer

class ReportTemplateSerializer(serializers.ModelSerializer):
    created_by_info = UserSerializer(source='created_by', read_only=True)
    
    class Meta:
        model = ReportTemplate
        fields = ['id', 'name', 'report_type', 'description', 'config', 
                  'created_by', 'created_by_info', 'created_at', 'updated_at']
        read_only_fields = ['created_by', 'created_at', 'updated_at']

class SavedReportSerializer(serializers.ModelSerializer):
    created_by_info = UserSerializer(source='created_by', read_only=True)
    template_info = ReportTemplateSerializer(source='template', read_only=True)
    
    class Meta:
        model = SavedReport
        fields = ['id', 'name', 'template', 'template_info', 'parameters', 'result_data',
                  'status', 'error_message', 'created_by', 'created_by_info', 
                  'created_at', 'completed_at']
        read_only_fields = ['created_by', 'created_at', 'completed_at', 'status', 'error_message']

# 生产报表序列化器
class ProductionStatisticsSerializer(serializers.Serializer):
    time_range = serializers.CharField(required=True)
    group_by = serializers.CharField(required=True)
    workshop_id = serializers.CharField(required=False, allow_blank=True)

class ProductionEfficiencySerializer(serializers.Serializer):
    time_range = serializers.CharField(required=True)
    group_by = serializers.CharField(required=True)
    workshop_id = serializers.CharField(required=False, allow_blank=True)
    line_id = serializers.CharField(required=False, allow_blank=True)

class ProductionQualitySerializer(serializers.Serializer):
    time_range = serializers.CharField(required=True)
    product_id = serializers.CharField(required=False, allow_blank=True)
    process_id = serializers.CharField(required=False, allow_blank=True)

# 库存报表序列化器
class InventoryStatusSerializer(serializers.Serializer):
    date = serializers.DateField(required=True)
    category = serializers.CharField(required=False, allow_blank=True)

class InventoryTurnoverSerializer(serializers.Serializer):
    time_range = serializers.CharField(required=True)
    category = serializers.CharField(required=False, allow_blank=True)

class MaterialConsumptionSerializer(serializers.Serializer):
    time_range = serializers.CharField(required=True)
    material_id = serializers.CharField(required=False, allow_blank=True)
    group_by = serializers.CharField(required=True)

# 成本报表序列化器
class ProductionCostSerializer(serializers.Serializer):
    time_range = serializers.CharField(required=True)
    product_id = serializers.CharField(required=False, allow_blank=True)
    group_by = serializers.CharField(required=True)

class ProcurementCostSerializer(serializers.Serializer):
    time_range = serializers.CharField(required=True)
    category = serializers.CharField(required=False, allow_blank=True)
    supplier_id = serializers.CharField(required=False, allow_blank=True)

class CostVarianceSerializer(serializers.Serializer):
    time_range = serializers.CharField(required=True)
    product_id = serializers.CharField(required=False, allow_blank=True)