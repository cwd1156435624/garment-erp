from rest_framework import serializers
from .models import Barcode, ScanningHistory, BarcodeGenerationBatch, PrintJob
from apps.materials.models import Material, Location, InventoryTransaction
from apps.production.models import Order
from apps.materials.serializers import MaterialSerializer, LocationSerializer
from apps.production.serializers import OrderSerializer

class BarcodeSerializer(serializers.ModelSerializer):
    """
    条码序列化器
    """
    barcode_type_display = serializers.CharField(source='get_barcode_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    material_name = serializers.SerializerMethodField()
    # product_name = serializers.SerializerMethodField() 
    # location_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Barcode
        fields = ['id', 'barcode_number', 'barcode_type', 'barcode_type_display', 'status', 'status_display',
                  'reference_id', 'material', 'material_name', 
                  'warehouse', 'order', 'operator_id', 
                  'print_count', 'last_print_time', 'created_at', 'updated_at', 'is_deleted']
    
    def get_material_name(self, obj):
        return obj.material.name if obj.material else ''
    
    # def get_product_name(self, obj):
    #    return obj.product.name if obj.product else '' 
    
    # def get_location_name(self, obj):
    #    return obj.warehouse.name if obj.warehouse else ''

class BarcodeGenerationSerializer(serializers.Serializer):
    """
    条码生成序列化器
    """
    type = serializers.ChoiceField(choices=Barcode.TYPE_CHOICES)
    quantity = serializers.IntegerField(min_value=1, max_value=1000)
    prefix = serializers.CharField(max_length=20, required=False, allow_blank=True)
    reference_ids = serializers.ListField(child=serializers.CharField(), required=False)

class BarcodePrintSerializer(serializers.Serializer):
    """
    条码打印序列化器
    """
    barcode_ids = serializers.ListField(child=serializers.CharField())
    printer_name = serializers.CharField(max_length=100)
    format = serializers.ChoiceField(choices=PrintJob.FORMAT_CHOICES, default='standard')
    copies = serializers.IntegerField(min_value=1, max_value=10, default=1)

class ScanningHistorySerializer(serializers.ModelSerializer):
    """
    扫码历史序列化器
    """
    barcode_number = serializers.SerializerMethodField()
    operation_type_display = serializers.SerializerMethodField()
    location_barcode_number = serializers.SerializerMethodField()
    order_barcode_number = serializers.SerializerMethodField()
    process_barcode_number = serializers.SerializerMethodField()
    operator_barcode_number = serializers.SerializerMethodField()
    package_barcode_number = serializers.SerializerMethodField()
    
    class Meta:
        model = ScanningHistory
        fields = ['id', 'barcode', 'barcode_number', 'operation_type', 'operation_type_display',
                  'quantity', 'location_barcode', 'location_barcode_number',
                  'order_barcode', 'order_barcode_number', 'process_barcode', 'process_barcode_number',
                  'operator_barcode', 'operator_barcode_number', 'package_barcode', 'package_barcode_number',
                  'batch_number', 'result', 'remark', 'created_at']
    
    def get_barcode_number(self, obj):
        return obj.barcode.barcode_number if obj.barcode else ''
    
    def get_operation_type_display(self, obj):
        return obj.get_operation_type_display()
    
    def get_location_barcode_number(self, obj):
        return obj.location_barcode.barcode_number if obj.location_barcode else ''
    
    def get_order_barcode_number(self, obj):
        return obj.order_barcode.barcode_number if obj.order_barcode else ''
    
    def get_process_barcode_number(self, obj):
        return obj.process_barcode.barcode_number if obj.process_barcode else ''
    
    def get_operator_barcode_number(self, obj):
        return obj.operator_barcode.barcode_number if obj.operator_barcode else ''
    
    def get_package_barcode_number(self, obj):
        return obj.package_barcode.barcode_number if obj.package_barcode else ''

class BarcodeRecognizeSerializer(serializers.Serializer):
    """
    条码识别序列化器
    """
    barcode = serializers.CharField(max_length=100)

class MaterialInboundScanningSerializer(serializers.Serializer):
    """
    物料入库扫码序列化器
    """
    materialBarcode = serializers.CharField(max_length=100)
    locationBarcode = serializers.CharField(max_length=100)
    quantity = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0.01)
    batchNumber = serializers.CharField(max_length=50, required=False, allow_blank=True)

class MaterialOutboundScanningSerializer(serializers.Serializer):
    """
    物料出库扫码序列化器
    """
    materialBarcode = serializers.CharField(max_length=100)
    locationBarcode = serializers.CharField(max_length=100)
    quantity = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0.01)
    orderBarcode = serializers.CharField(max_length=100, required=False)

class ProductionProcessScanningSerializer(serializers.Serializer):
    """
    生产过程扫码序列化器
    """
    orderBarcode = serializers.CharField(max_length=100)
    processBarcode = serializers.CharField(max_length=100)
    operatorBarcode = serializers.CharField(max_length=100)
    quantity = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0.01)

class ProductPackagingScanningSerializer(serializers.Serializer):
    """
    产品包装扫码序列化器
    """
    productBarcode = serializers.CharField(max_length=100)
    packageBarcode = serializers.CharField(max_length=100)
    quantity = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0.01)