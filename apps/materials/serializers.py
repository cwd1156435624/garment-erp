from rest_framework import serializers
from .models import (
    Material, Location, Inventory, InventoryTransaction,
    Supplier, MaterialSupplier, Contact, SupplierEvaluation,
    ProcurementRequirement, ProcurementOrder, ProcurementItem, StatusHistory
)
from apps.users.serializers import UserSerializer


class MaterialSerializer(serializers.ModelSerializer):
    """物料序列化器"""
    status_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Material
        fields = ['id', 'code', 'name', 'category', 'unit', 'specifications', 
                  'min_stock', 'max_stock', 'unit_price', 'status', 'status_display', 
                  'remarks', 'created_at', 'updated_at', 'is_deleted']
    
    def get_status_display(self, obj):
        return obj.get_status_display()


class MaterialDetailSerializer(serializers.ModelSerializer):
    """物料详情序列化器"""
    status_display = serializers.SerializerMethodField()
    suppliers = serializers.SerializerMethodField()
    
    class Meta:
        model = Material
        ref_name = 'materials.MaterialDetail'
        fields = ['id', 'code', 'name', 'category', 'unit', 'specifications', 
                  'min_stock', 'max_stock', 'unit_price', 'status', 'status_display', 
                  'remarks', 'created_at', 'updated_at', 'is_deleted', 'suppliers']
    
    def get_status_display(self, obj):
        return obj.get_status_display()
    
    def get_suppliers(self, obj):
        material_suppliers = MaterialSupplier.objects.filter(material=obj)
        return MaterialSupplierSerializer(material_suppliers, many=True).data


class LocationSerializer(serializers.ModelSerializer):
    """库位序列化器"""
    status_display = serializers.SerializerMethodField()
    warehouse_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Location
        fields = ['id', 'code', 'name', 'warehouse', 'warehouse_name', 'area', 
                  'capacity', 'status', 'status_display', 'remarks', 
                  'created_at', 'updated_at', 'is_deleted']
    
    def get_status_display(self, obj):
        return obj.get_status_display()
    
    def get_warehouse_name(self, obj):
        return obj.warehouse.name if obj.warehouse else ''


class InventorySerializer(serializers.ModelSerializer):
    """库存序列化器"""
    material_name = serializers.SerializerMethodField()
    location_name = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Inventory
        fields = ['id', 'material', 'material_name', 'location', 'location_name', 
                  'batch_number', 'quantity', 'status', 'status_display', 
                  'production_date', 'expiry_date', 'created_at', 'updated_at', 'is_deleted']
    
    def get_material_name(self, obj):
        return f"{obj.material.code} - {obj.material.name}" if obj.material else ''
    
    def get_location_name(self, obj):
        return obj.location.name if obj.location else ''
    
    def get_status_display(self, obj):
        return obj.get_status_display()


class InventoryDetailSerializer(serializers.ModelSerializer):
    """库存详情序列化器"""
    material = MaterialSerializer(read_only=True)
    location = LocationSerializer(read_only=True)
    status_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Inventory
        fields = ['id', 'material', 'location', 'batch_number', 'quantity', 
                  'status', 'status_display', 'production_date', 'expiry_date', 
                  'created_at', 'updated_at', 'is_deleted']
    
    def get_status_display(self, obj):
        return obj.get_status_display()


class InventoryTransactionSerializer(serializers.ModelSerializer):
    """库存交易序列化器"""
    inventory_detail = serializers.SerializerMethodField()
    transaction_type_display = serializers.SerializerMethodField()
    adjustment_type_display = serializers.SerializerMethodField()
    operator_name = serializers.SerializerMethodField()
    
    class Meta:
        model = InventoryTransaction
        fields = ['id', 'transaction_number', 'inventory', 'inventory_detail', 
                  'transaction_type', 'transaction_type_display', 
                  'adjustment_type', 'adjustment_type_display', 
                  'quantity', 'batch_number', 'purchase_order', 'production_order', 
                  'from_location', 'to_location', 'operator', 'operator_name', 
                  'transaction_time', 'reason', 'remarks', 'created_at', 'updated_at']
    
    def get_inventory_detail(self, obj):
        return {
            'material_code': obj.inventory.material.code if obj.inventory and obj.inventory.material else '',
            'material_name': obj.inventory.material.name if obj.inventory and obj.inventory.material else '',
            'location_name': obj.inventory.location.name if obj.inventory and obj.inventory.location else '',
        }
    
    def get_transaction_type_display(self, obj):
        return obj.get_transaction_type_display()
    
    def get_adjustment_type_display(self, obj):
        return obj.get_adjustment_type_display() if obj.adjustment_type else ''
    
    def get_operator_name(self, obj):
        return obj.operator.username if obj.operator else ''


class InboundSerializer(serializers.Serializer):
    """入库序列化器"""
    material_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)
    location_id = serializers.IntegerField()
    batch_number = serializers.CharField(required=False, allow_blank=True)
    purchase_order_id = serializers.IntegerField(required=False, allow_null=True)
    production_date = serializers.DateField(required=False, allow_null=True)
    expiry_date = serializers.DateField(required=False, allow_null=True)
    remark = serializers.CharField(required=False, allow_blank=True)


class OutboundSerializer(serializers.Serializer):
    """出库序列化器"""
    material_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)
    location_id = serializers.IntegerField()
    production_order_id = serializers.IntegerField(required=False, allow_null=True)
    remark = serializers.CharField(required=False, allow_blank=True)


class AdjustmentSerializer(serializers.Serializer):
    """库存调整序列化器"""
    material_id = serializers.IntegerField()
    location_id = serializers.IntegerField()
    quantity = serializers.IntegerField()
    adjustment_type = serializers.ChoiceField(choices=InventoryTransaction.ADJUSTMENT_TYPE_CHOICES)
    reason = serializers.CharField()
    remark = serializers.CharField(required=False, allow_blank=True)


class StocktakingItemSerializer(serializers.Serializer):
    """盘点项目序列化器"""
    material_id = serializers.IntegerField()
    location_id = serializers.IntegerField()
    actual_quantity = serializers.IntegerField(min_value=0)


class StocktakingSerializer(serializers.Serializer):
    """库存盘点序列化器"""
    items = StocktakingItemSerializer(many=True)
    remark = serializers.CharField(required=False, allow_blank=True)


class TransferSerializer(serializers.Serializer):
    """库存转移序列化器"""
    material_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)
    from_location_id = serializers.IntegerField()
    to_location_id = serializers.IntegerField()
    batch_number = serializers.CharField(required=False, allow_blank=True)
    remark = serializers.CharField(required=False, allow_blank=True)


class ContactSerializer(serializers.ModelSerializer):
    """联系人序列化器"""
    class Meta:
        model = Contact
        fields = ['id', 'name', 'position', 'phone', 'email', 'is_primary', 'remarks']


class SupplierSerializer(serializers.ModelSerializer):
    """供应商序列化器"""
    status_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Supplier
        ref_name = 'materials.SupplierSerializer'
        fields = ['id', 'code', 'name', 
                  'contact_person', 'contact_phone', 'email', 'address', 
                  'status', 'status_display', 'remarks', 
                  'created_at', 'updated_at', 'is_deleted']
    
    def get_status_display(self, obj):
        return obj.get_status_display()


class SupplierDetailSerializer(serializers.ModelSerializer):
    """供应商详情序列化器"""
    status_display = serializers.SerializerMethodField()
    contacts = ContactSerializer(many=True, read_only=True)
    materials = serializers.SerializerMethodField()
    
    class Meta:
        model = Supplier
        ref_name = 'materials.SupplierDetailSerializer'
        fields = ['id', 'code', 'name', 'address', 'contact_person', 
                  'contact_phone', 'email', 
                  'status', 'status_display', 'remarks', 'created_at', 'updated_at', 
                  'is_deleted', 'contacts', 'materials']
    
    def get_status_display(self, obj):
        return obj.get_status_display()
    
    def get_materials(self, obj):
        material_suppliers = MaterialSupplier.objects.filter(supplier=obj)
        result = []
        for ms in material_suppliers:
            result.append({
                'id': ms.material.id,
                'code': ms.material.code,
                'name': ms.material.name,
                'unit_price': ms.unit_price,
                'is_preferred': ms.is_preferred,
                'lead_time': ms.lead_time
            })
        return result


class MaterialSupplierSerializer(serializers.ModelSerializer):
    """物料供应商序列化器"""
    supplier_name = serializers.SerializerMethodField()
    material_name = serializers.SerializerMethodField()
    
    class Meta:
        model = MaterialSupplier
        fields = ['id', 'material', 'material_name', 'supplier', 'supplier_name', 
                  'is_preferred', 'unit_price', 'lead_time', 'min_order_quantity', 'remarks']
    
    def get_supplier_name(self, obj):
        return obj.supplier.name if obj.supplier else ''
    
    def get_material_name(self, obj):
        return obj.material.name if obj.material else ''


class SupplierEvaluationSerializer(serializers.ModelSerializer):
    """供应商评估序列化器"""
    evaluator_name = serializers.SerializerMethodField()
    supplier_name = serializers.SerializerMethodField()
    
    class Meta:
        model = SupplierEvaluation
        fields = ['id', 'supplier', 'supplier_name', 'period', 'quality_score', 
                  'delivery_score', 'price_score', 'service_score', 'total_score', 
                  'evaluator', 'evaluator_name', 'evaluation_date', 'remarks']
    
    def get_evaluator_name(self, obj):
        return obj.evaluator.username if obj.evaluator else ''
    
    def get_supplier_name(self, obj):
        return obj.supplier.name if obj.supplier else ''


class ProcurementRequirementSerializer(serializers.ModelSerializer):
    """采购需求序列化器"""
    material_name = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()
    priority_display = serializers.SerializerMethodField()
    requester_name = serializers.SerializerMethodField()
    approver_name = serializers.SerializerMethodField()
    
    class Meta:
        model = ProcurementRequirement
        fields = ['id', 'requirement_number', 'material', 'material_name', 'quantity', 
                  'required_date', 'status', 'status_display', 'priority', 'priority_display', 
                  'requester', 'requester_name', 'approver', 'approver_name', 'approval_date', 
                  'production_order', 'reason', 'remarks', 'created_at', 'updated_at', 'is_deleted']
    
    def get_material_name(self, obj):
        return f"{obj.material.code} - {obj.material.name}" if obj.material else ''
    
    def get_status_display(self, obj):
        return obj.get_status_display()
    
    def get_priority_display(self, obj):
        return obj.get_priority_display()
    
    def get_requester_name(self, obj):
        return obj.requester.username if obj.requester else ''
    
    def get_approver_name(self, obj):
        return obj.approver.username if obj.approver else ''


class ProcurementItemSerializer(serializers.ModelSerializer):
    """采购项目序列化器"""
    material_name = serializers.SerializerMethodField()
    
    class Meta:
        model = ProcurementItem
        fields = ['id', 'material', 'material_name', 'quantity', 'unit_price', 
                  'total_price', 'requirement', 'received_quantity', 'remarks']
    
    def get_material_name(self, obj):
        return f"{obj.material.code} - {obj.material.name}" if obj.material else ''


class StatusHistorySerializer(serializers.ModelSerializer):
    """状态历史序列化器"""
    operator_name = serializers.SerializerMethodField()
    
    class Meta:
        model = StatusHistory
        fields = ['id', 'from_status', 'to_status', 'change_time', 'operator_name', 'remarks']
    
    def get_operator_name(self, obj):
        return obj.operator.username if obj.operator else ''


class ProcurementOrderSerializer(serializers.ModelSerializer):
    """采购订单序列化器"""
    supplier_name = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()
    purchaser_name = serializers.SerializerMethodField()
    approver_name = serializers.SerializerMethodField()
    
    class Meta:
        model = ProcurementOrder
        fields = ['id', 'order_number', 'supplier', 'supplier_name', 'order_date', 
                  'expected_delivery_date', 'actual_delivery_date', 'status', 'status_display', 
                  'total_amount', 'payment_terms', 'shipping_method', 'contact_person', 
                  'contact_phone', 'delivery_address', 'purchaser', 'purchaser_name', 
                  'approver', 'approver_name', 'approval_date', 'remarks', 
                  'created_at', 'updated_at', 'is_deleted']
    
    def get_supplier_name(self, obj):
        return obj.supplier.name if obj.supplier else ''
    
    def get_status_display(self, obj):
        return obj.get_status_display()
    
    def get_purchaser_name(self, obj):
        return obj.purchaser.username if obj.purchaser else ''
    
    def get_approver_name(self, obj):
        return obj.approver.username if obj.approver else ''


class ProcurementOrderDetailSerializer(serializers.ModelSerializer):
    """采购订单详情序列化器"""
    supplier = SupplierSerializer(read_only=True)
    status_display = serializers.SerializerMethodField()
    purchaser = UserSerializer(read_only=True)
    approver = UserSerializer(read_only=True)
    items = ProcurementItemSerializer(many=True, read_only=True)
    status_history = StatusHistorySerializer(many=True, read_only=True)
    
    class Meta:
        model = ProcurementOrder
        fields = ['id', 'order_number', 'supplier', 'order_date', 
                  'expected_delivery_date', 'actual_delivery_date', 'status', 'status_display', 
                  'total_amount', 'payment_terms', 'shipping_method', 'contact_person', 
                  'contact_phone', 'delivery_address', 'purchaser', 'approver', 'approval_date', 
                  'remarks', 'created_at', 'updated_at', 'is_deleted', 'items', 'status_history']
    
    def get_status_display(self, obj):
        return obj.get_status_display()


class GoodsReceiptItemSerializer(serializers.Serializer):
    """收货项目序列化器"""
    procurement_item_id = serializers.IntegerField()
    received_quantity = serializers.IntegerField(min_value=1)
    location_id = serializers.IntegerField()
    batch_number = serializers.CharField(required=False, allow_blank=True)
    production_date = serializers.DateField(required=False, allow_null=True)
    expiry_date = serializers.DateField(required=False, allow_null=True)
    quality_status = serializers.ChoiceField(choices=[
        ('qualified', '合格'),
        ('unqualified', '不合格'),
        ('pending', '待检')
    ], default='qualified')
    remarks = serializers.CharField(required=False, allow_blank=True)


class GoodsReceiptSerializer(serializers.Serializer):
    """物料收货序列化器"""
    procurement_order_id = serializers.IntegerField()
    receipt_date = serializers.DateField()
    receipt_number = serializers.CharField(required=False, allow_blank=True)
    delivery_note = serializers.CharField(required=False, allow_blank=True)
    items = GoodsReceiptItemSerializer(many=True)
    remarks = serializers.CharField(required=False, allow_blank=True)


class MaterialImportSerializer(serializers.Serializer):
    """物料导入序列化器"""
    file = serializers.FileField()