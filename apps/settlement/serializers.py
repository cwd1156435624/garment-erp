from rest_framework import serializers
from .models import SettlementBill, SettlementItem, ApprovalHistory, Payment, Reconciliation
from apps.supplier.models import Supplier

class SettlementItemSerializer(serializers.ModelSerializer):
    """
    结算项目序列化器
    """
    class Meta:
        ref_name = 'settlement.SettlementItemSerializer'
        model = SettlementItem
        fields = ['id', 'item_type', 'reference_number', 'order', 'amount', 'description', 'created_at']
        read_only_fields = ['id', 'created_at']

class ApprovalHistorySerializer(serializers.ModelSerializer):
    """
    审批历史序列化器
    """
    created_by_name = serializers.SerializerMethodField()
    
    class Meta:
        ref_name = 'settlement.ApprovalHistorySerializer'
        model = ApprovalHistory
        fields = ['id', 'action', 'remark', 'created_at', 'created_by', 'created_by_name']
        read_only_fields = ['id', 'created_at', 'created_by']
    
    def get_created_by_name(self, obj):
        return obj.created_by.username if obj.created_by else ''

class PaymentSerializer(serializers.ModelSerializer):
    """
    付款记录序列化器
    """
    class Meta:
        ref_name = 'SettlementPaymentSerializer'
        model = Payment
        fields = ['id', 'amount', 'payment_date', 'payment_method', 'reference', 'remark', 'created_at']
        read_only_fields = ['id', 'created_at']

class SettlementBillListSerializer(serializers.ModelSerializer):
    """
    结算单列表序列化器
    """
    supplier_name = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()
    
    class Meta:
        ref_name = 'settlement.SettlementBillListSerializer'
        model = SettlementBill
        fields = ['id', 'bill_number', 'supplier', 'supplier_name', 'period_start', 'period_end', 
                  'total_amount', 'paid_amount', 'status', 'status_display', 'created_at']
    
    def get_supplier_name(self, obj):
        return obj.supplier.name if obj.supplier else ''
    
    def get_status_display(self, obj):
        return obj.get_status_display()

class SettlementBillDetailSerializer(serializers.ModelSerializer):
    """
    结算单详情序列化器
    """
    items = SettlementItemSerializer(many=True, read_only=True)
    approval_history = ApprovalHistorySerializer(many=True, read_only=True)
    payments = PaymentSerializer(many=True, read_only=True)
    supplier_name = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()
    
    class Meta:
        ref_name = 'settlement.SettlementBillDetailSerializer'
        model = SettlementBill
        fields = ['id', 'bill_number', 'supplier', 'supplier_name', 'period_start', 'period_end',
                  'total_amount', 'paid_amount', 'status', 'status_display', 'remark',
                  'items', 'approval_history', 'payments', 'created_at', 'updated_at']
        read_only_fields = ['id', 'bill_number', 'total_amount', 'paid_amount', 'status', 'created_at', 'updated_at']
    
    def get_supplier_name(self, obj):
        return obj.supplier.name if obj.supplier else ''
    
    def get_status_display(self, obj):
        return obj.get_status_display()

class SettlementBillCreateSerializer(serializers.ModelSerializer):
    """
    结算单创建序列化器
    """
    items = SettlementItemSerializer(many=True)
    
    class Meta:
        ref_name = 'settlement.SettlementBillCreateSerializer'
        model = SettlementBill
        fields = ['supplier', 'period_start', 'period_end', 'remark', 'items']
    
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        # 生成结算单号
        bill_number = f"ST{timezone.now().strftime('%Y%m%d%H%M%S')}"
        
        # 计算总金额
        total_amount = sum(item['amount'] for item in items_data)
        
        # 创建结算单
        settlement = SettlementBill.objects.create(
            bill_number=bill_number,
            total_amount=total_amount,
            **validated_data
        )
        
        # 创建结算项目
        for item_data in items_data:
            SettlementItem.objects.create(settlement=settlement, **item_data)
        
        return settlement

class SettlementBillUpdateSerializer(serializers.ModelSerializer):
    """
    结算单更新序列化器
    """
    items = SettlementItemSerializer(many=True)
    
    class Meta:
        ref_name = 'settlement.SettlementBillUpdateSerializer'
        model = SettlementBill
        fields = ['remark', 'items']
    
    def update(self, instance, validated_data):
        if instance.status != 'draft':
            raise serializers.ValidationError("只有草稿状态的结算单可以编辑")
        
        items_data = validated_data.pop('items', None)
        
        # 更新结算单基本信息
        instance.remark = validated_data.get('remark', instance.remark)
        
        if items_data is not None:
            # 删除原有结算项目
            instance.items.all().delete()
            
            # 创建新的结算项目
            total_amount = 0
            for item_data in items_data:
                SettlementItem.objects.create(settlement=instance, **item_data)
                total_amount += item_data['amount']
            
            # 更新总金额
            instance.total_amount = total_amount
        
        instance.save()
        return instance

class ApprovalActionSerializer(serializers.Serializer):
    """
    审批操作序列化器
    """
    action = serializers.ChoiceField(choices=['approve', 'reject', 'return'])
    remark = serializers.CharField(required=False, allow_blank=True)

class PaymentCreateSerializer(serializers.ModelSerializer):
    """
    付款记录创建序列化器
    """
    class Meta:
        ref_name = 'settlement.PaymentCreateSerializer'
        model = Payment
        fields = ['amount', 'payment_date', 'payment_method', 'reference', 'remark']
    
    def validate_amount(self, value):
        settlement = self.context['settlement']
        remaining = settlement.total_amount - settlement.paid_amount
        if value <= 0:
            raise serializers.ValidationError("付款金额必须大于0")
        if value > remaining:
            raise serializers.ValidationError(f"付款金额不能超过剩余应付金额 {remaining}")
        return value

class ReconciliationListSerializer(serializers.ModelSerializer):
    """
    对账单列表序列化器
    """
    supplier_name = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()
    
    class Meta:
        ref_name = 'settlement.ReconciliationListSerializer'
        model = Reconciliation
        fields = ['id', 'reconciliation_number', 'supplier', 'supplier_name', 'month',
                  'total_procurement', 'total_settlement', 'status', 'status_display', 'created_at']
    
    def get_supplier_name(self, obj):
        return obj.supplier.name if obj.supplier else ''
    
    def get_status_display(self, obj):
        return obj.get_status_display()

class ReconciliationDetailSerializer(serializers.ModelSerializer):
    """
    对账单详情序列化器
    """
    supplier_name = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()
    
    class Meta:
        ref_name = 'settlement.ReconciliationDetailSerializer'
        model = Reconciliation
        fields = ['id', 'reconciliation_number', 'supplier', 'supplier_name', 'month',
                  'total_procurement', 'total_settlement', 'status', 'status_display',
                  'confirmation_date', 'confirmed_by', 'remark', 'created_at', 'updated_at']
    
    def get_supplier_name(self, obj):
        return obj.supplier.name if obj.supplier else ''
    
    def get_status_display(self, obj):
        return obj.get_status_display()

class ReconciliationCreateSerializer(serializers.ModelSerializer):
    """
    对账单创建序列化器
    """
    class Meta:
        ref_name = 'settlement.ReconciliationCreateSerializer'
        model = Reconciliation
        fields = ['supplier', 'month', 'remark']
    
    def create(self, validated_data):
        # 生成对账单号
        reconciliation_number = f"RC{timezone.now().strftime('%Y%m%d%H%M%S')}"
        
        # 获取对账月份的采购和结算数据
        supplier = validated_data['supplier']
        month = validated_data['month']
        year, month = month.split('-')
        
        # 计算采购总额
        start_date = datetime(int(year), int(month), 1)
        if int(month) == 12:
            end_date = datetime(int(year) + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = datetime(int(year), int(month) + 1, 1) - timedelta(days=1)
        
        # 获取该月的采购订单总额
        procurement_orders = ProcurementOrder.objects.filter(
            supplier=supplier,
            order_date__gte=start_date,
            order_date__lte=end_date
        )
        total_procurement = sum(order.total_amount for order in procurement_orders)
        
        # 获取该月的结算单总额
        settlement_bills = SettlementBill.objects.filter(
            supplier=supplier,
            created_at__gte=start_date,
            created_at__lte=end_date
        )
        total_settlement = sum(bill.total_amount for bill in settlement_bills)
        
        # 创建对账单
        reconciliation = Reconciliation.objects.create(
            reconciliation_number=reconciliation_number,
            total_procurement=total_procurement,
            total_settlement=total_settlement,
            **validated_data
        )
        
        return reconciliation

class ReconciliationConfirmSerializer(serializers.Serializer):
    """
    对账单确认序列化器
    """
    confirmation_date = serializers.DateField()
    confirmed_by = serializers.CharField(max_length=50)
    remark = serializers.CharField(required=False, allow_blank=True)