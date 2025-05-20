from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from django.utils import timezone
from django.shortcuts import get_object_or_404
from .models import (
    Material, Location, Inventory, InventoryTransaction,
    Supplier, MaterialSupplier, Contact, SupplierEvaluation,
    ProcurementRequirement, ProcurementOrder, ProcurementItem, StatusHistory
)
from .serializers import (
    MaterialSerializer, MaterialDetailSerializer, LocationSerializer,
    InventorySerializer, InventoryDetailSerializer, InventoryTransactionSerializer,
    SupplierSerializer, SupplierDetailSerializer, MaterialSupplierSerializer,
    SupplierEvaluationSerializer, ProcurementRequirementSerializer,
    ProcurementOrderSerializer, ProcurementOrderDetailSerializer,
    ProcurementItemSerializer, StatusHistorySerializer, GoodsReceiptSerializer
)


class MaterialViewSet(viewsets.ModelViewSet):
    """
    物料视图集
    提供物料的增删改查功能
    """
    queryset = Material.objects.filter(is_deleted=False)
    serializer_class = MaterialSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return MaterialDetailSerializer
        return MaterialSerializer
    
    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save(update_fields=['is_deleted'])


class LocationViewSet(viewsets.ModelViewSet):
    """
    库位视图集
    提供库位的增删改查功能
    """
    queryset = Location.objects.filter(is_deleted=False)
    serializer_class = LocationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save(update_fields=['is_deleted'])


class InventoryViewSet(viewsets.ModelViewSet):
    """
    库存视图集
    提供库存的增删改查功能
    """
    queryset = Inventory.objects.filter(is_deleted=False)
    serializer_class = InventorySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return InventoryDetailSerializer
        return InventorySerializer
    
    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save(update_fields=['is_deleted'])


class SupplierViewSet(viewsets.ModelViewSet):
    """
    供应商视图集
    提供供应商的增删改查功能
    """
    queryset = Supplier.objects.filter(is_deleted=False)
    serializer_class = SupplierSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return SupplierDetailSerializer
        return SupplierSerializer
    
    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save(update_fields=['is_deleted'])


class ProcurementRequirementViewSet(viewsets.ModelViewSet):
    """
    采购需求视图集
    提供采购需求的增删改查功能
    """
    queryset = ProcurementRequirement.objects.filter(is_deleted=False)
    serializer_class = ProcurementRequirementSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save(update_fields=['is_deleted'])


class ProcurementOrderViewSet(viewsets.ModelViewSet):
    """
    采购订单视图集
    提供采购订单的增删改查功能
    """
    queryset = ProcurementOrder.objects.filter(is_deleted=False)
    serializer_class = ProcurementOrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProcurementOrderDetailSerializer
        return ProcurementOrderSerializer
    
    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save(update_fields=['is_deleted'])
    
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """
        创建采购订单
        接收参数：
        - supplierId: 供应商ID
        - items: 采购项目列表，每个项目包含materialId, quantity, unitPrice
        - expectedDeliveryDate: 预计交付日期
        - paymentTerms: 付款条件
        - remark: 备注
        """
        supplier_id = request.data.get('supplierId')
        items_data = request.data.get('items', [])
        expected_delivery_date = request.data.get('expectedDeliveryDate')
        payment_terms = request.data.get('paymentTerms')
        remark = request.data.get('remark')
        
        # 验证必要参数
        if not supplier_id or not items_data or not expected_delivery_date:
            return Response({'error': '缺少必要参数'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            supplier = Supplier.objects.get(id=supplier_id)
        except Supplier.DoesNotExist:
            return Response({'error': '供应商不存在'}, status=status.HTTP_404_NOT_FOUND)
        
        # 生成订单编号
        order_number = f"PO{timezone.now().strftime('%Y%m%d%H%M%S')}"
        
        # 创建采购订单
        order = ProcurementOrder.objects.create(
            order_number=order_number,
            supplier=supplier,
            order_date=timezone.now().date(),
            expected_delivery_date=expected_delivery_date,
            payment_terms=payment_terms,
            purchaser=request.user,
            status='draft',
            remarks=remark
        )
        
        # 创建采购项目
        total_amount = 0
        for item_data in items_data:
            material_id = item_data.get('materialId')
            quantity = item_data.get('quantity')
            unit_price = item_data.get('unitPrice')
            
            if not material_id or not quantity or not unit_price:
                continue
            
            try:
                material = Material.objects.get(id=material_id)
            except Material.DoesNotExist:
                continue
            
            total_price = quantity * float(unit_price)
            ProcurementItem.objects.create(
                order=order,
                material=material,
                quantity=quantity,
                unit_price=unit_price,
                total_price=total_price
            )
            total_amount += total_price
        
        # 更新订单总金额
        order.total_amount = total_amount
        order.save(update_fields=['total_amount'])
        
        serializer = ProcurementOrderDetailSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['put'])
    @transaction.atomic
    def status(self, request, pk=None):
        """
        更新采购订单状态
        接收参数：
        - status: 新状态
        - remark: 备注
        """
        order = self.get_object()
        new_status = request.data.get('status')
        remark = request.data.get('remark', '')
        
        if not new_status:
            return Response({'error': '缺少状态参数'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 验证状态值是否有效
        valid_statuses = dict(ProcurementOrder.STATUS_CHOICES).keys()
        if new_status not in valid_statuses:
            return Response({'error': '无效的状态值'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 记录状态变更历史
        StatusHistory.objects.create(
            order=order,
            from_status=order.status,
            to_status=new_status,
            operator=request.user,
            remarks=remark
        )
        
        # 更新订单状态
        order.status = new_status
        order.save(update_fields=['status'])
        
        serializer = ProcurementOrderDetailSerializer(order)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    @transaction.atomic
    def receipt(self, request, pk=None):
        """
        记录采购收货
        接收参数：
        - items: 收货项目列表，每个项目包含materialId, quantity, qualityStatus
        - receiptDate: 收货日期
        - remark: 备注
        """
        order = self.get_object()
        serializer = GoodsReceiptSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        validated_data = serializer.validated_data
        items_data = validated_data.get('items', [])
        receipt_date = validated_data.get('receipt_date')
        remark = validated_data.get('remarks', '')
        
        # 更新采购项目的已收货数量
        all_received = True
        for item_data in items_data:
            procurement_item_id = item_data.get('procurement_item_id')
            received_quantity = item_data.get('received_quantity')
            location_id = item_data.get('location_id')
            batch_number = item_data.get('batch_number', '')
            production_date = item_data.get('production_date')
            expiry_date = item_data.get('expiry_date')
            quality_status = item_data.get('quality_status')
            
            try:
                procurement_item = ProcurementItem.objects.get(id=procurement_item_id, order=order)
                location = Location.objects.get(id=location_id)
            except (ProcurementItem.DoesNotExist, Location.DoesNotExist):
                return Response({'error': '采购项目或库位不存在'}, status=status.HTTP_404_NOT_FOUND)
            
            # 更新已收货数量
            procurement_item.received_quantity += received_quantity
            procurement_item.save(update_fields=['received_quantity'])
            
            # 检查是否所有项目都已完全收货
            if procurement_item.received_quantity < procurement_item.quantity:
                all_received = False
            
            # 如果质量状态为合格，则更新库存
            if quality_status == 'qualified':
                # 查找或创建库存记录
                inventory, created = Inventory.objects.get_or_create(
                    material=procurement_item.material,
                    location=location,
                    batch_number=batch_number,
                    defaults={
                        'quantity': 0,
                        'status': 'normal',
                        'production_date': production_date,
                        'expiry_date': expiry_date
                    }
                )
                
                # 更新库存数量
                inventory.quantity += received_quantity
                inventory.save(update_fields=['quantity'])
                
                # 创建库存交易记录
                InventoryTransaction.objects.create(
                    transaction_number=f"IN{timezone.now().strftime('%Y%m%d%H%M%S')}",
                    inventory=inventory,
                    transaction_type='inbound',
                    quantity=received_quantity,
                    batch_number=batch_number,
                    purchase_order=order,
                    to_location=location,
                    operator=request.user,
                    transaction_time=timezone.now(),
                    reason='采购收货',
                    remarks=remark
                )
        
        # 更新订单状态和实际交付日期
        if all_received:
            # 记录状态变更历史
            StatusHistory.objects.create(
                order=order,
                from_status=order.status,
                to_status='completed',
                operator=request.user,
                remarks='所有物料已收货完成'
            )
            order.status = 'completed'
        else:
            # 记录状态变更历史
            StatusHistory.objects.create(
                order=order,
                from_status=order.status,
                to_status='received',
                operator=request.user,
                remarks='部分物料已收货'
            )
            order.status = 'received'
        
        order.actual_delivery_date = receipt_date
        order.save(update_fields=['status', 'actual_delivery_date'])
        
        serializer = ProcurementOrderDetailSerializer(order)
        return Response(serializer.data)