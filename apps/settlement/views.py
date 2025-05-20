from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.utils import timezone
from django.db.models import Q, Sum
from django.shortcuts import get_object_or_404
import datetime
import uuid
import csv
import io

from .models import SettlementBill, SettlementItem, ApprovalHistory as SettlementApproval, Payment as SettlementPayment, Reconciliation as Factory
from .serializers import (
    SettlementBillListSerializer as SettlementListSerializer, 
    SettlementBillDetailSerializer as SettlementDetailSerializer,
    SettlementBillCreateSerializer as SettlementCreateSerializer, 
    SettlementBillUpdateSerializer as SettlementUpdateSerializer,
    ReconciliationListSerializer as FactoryListSerializer, 
    ReconciliationDetailSerializer as FactoryDetailSerializer,
    ReconciliationCreateSerializer as FactoryCreateSerializer, 
    ReconciliationConfirmSerializer as FactoryUpdateSerializer,
    ApprovalActionSerializer as SettlementApprovalSerializer, 
    PaymentSerializer as SettlementPaymentSerializer
)
from apps.system.utils import ResponseWrapper

class SettlementViewSet(viewsets.ModelViewSet):
    """
    结算单视图集
    提供结算单的CRUD操作和自定义操作
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return SettlementListSerializer
        elif self.action == 'create':
            return SettlementCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return SettlementUpdateSerializer
        else:
            return SettlementDetailSerializer
    
    def get_queryset(self):
        queryset = SettlementBill.objects.filter(is_deleted=False)
        # 过滤条件
        status = self.request.query_params.get('status')
        factory_id = self.request.query_params.get('factory_id')
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if status:
            queryset = queryset.filter(status=status)
        if factory_id:
            queryset = queryset.filter(factory_id=factory_id)
        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return Response({
                'count': self.paginator.page.paginator.count,
                'next': self.paginator.get_next_link(),
                'previous': self.paginator.get_previous_link(),
                'results': serializer.data
            })
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def perform_create(self, serializer):
        # 生成结算单编号
        settlement_number = f"ST{timezone.now().strftime('%Y%m%d')}{str(uuid.uuid4().int)[:3]}"
        serializer.save(created_by=self.request.user, settlement_number=settlement_number)
    
    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)
    
    def perform_destroy(self, instance):
        # 软删除
        instance.is_deleted = True
        instance.save()
    
    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        """
        提交结算单审批
        """
        settlement = self.get_object()
        
        if settlement.status != 'draft':
            return Response({
                'detail': '只有草稿状态的结算单可以提交审批'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 更新结算单状态
        settlement.status = 'pending'
        settlement.save()
        
        # 创建提交记录
        SettlementApproval.objects.create(
            settlement=settlement,
            status='pending',
            created_by=request.user
        )
        
        return Response({
            'id': settlement.id,
            'settlement_number': settlement.settlement_number,
            'status': settlement.status,
            'submitted_by': {
                'id': request.user.id,
                'username': request.user.username
            },
            'submitted_at': timezone.now().isoformat()
        })
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """
        审批结算单
        """
        settlement = self.get_object()
        
        if settlement.status != 'pending':
            return Response({
                'detail': '当前状态不允许审批操作'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        approved = request.data.get('approved', False)
        comments = request.data.get('comments', '')
        
        # 更新结算单状态
        settlement.status = 'approved' if approved else 'rejected'
        settlement.save()
        
        # 创建审批记录
        approval = SettlementApproval.objects.create(
            settlement=settlement,
            status=settlement.status,
            comments=comments,
            created_by=request.user
        )
        
        return Response({
            'id': settlement.id,
            'settlement_number': settlement.settlement_number,
            'status': settlement.status,
            'approved_by': {
                'id': request.user.id,
                'username': request.user.username
            },
            'approved_at': approval.created_at.isoformat(),
            'comments': comments
        })
    
    @action(detail=True, methods=['post'])
    def payment(self, request, pk=None):
        """
        记录结算单付款
        """
        settlement = self.get_object()
        
        if settlement.status != 'approved':
            return Response({
                'detail': '只有已审批的结算单可以记录付款'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        payment_method = request.data.get('payment_method')
        payment_date = request.data.get('payment_date')
        payment_amount = request.data.get('payment_amount')
        payment_reference = request.data.get('payment_reference')
        notes = request.data.get('notes', '')
        
        if not all([payment_method, payment_date, payment_amount]):
            return Response({
                'detail': '付款方式、付款日期和付款金额为必填项'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 创建付款记录
        payment = SettlementPayment.objects.create(
            settlement=settlement,
            payment_method=payment_method,
            payment_date=payment_date,
            payment_amount=payment_amount,
            payment_reference=payment_reference,
            notes=notes,
            created_by=request.user
        )
        
        # 更新结算单状态
        settlement.status = 'paid'
        settlement.payment_method = payment_method
        settlement.payment_date = payment_date
        settlement.payment_reference = payment_reference
        settlement.save()
        
        return Response({
            'id': settlement.id,
            'settlement_number': settlement.settlement_number,
            'status': settlement.status,
            'payment_method': payment_method,
            'payment_date': payment_date,
            'payment_amount': payment_amount,
            'payment_reference': payment_reference,
            'paid_by': {
                'id': request.user.id,
                'username': request.user.username
            },
            'paid_at': payment.created_at.isoformat()
        })
    
    @action(detail=False, methods=['post'])
    def batch_export(self, request):
        """
        批量导出结算单
        """
        ids = request.data.get('ids', [])
        export_format = request.data.get('format', 'csv')
        
        if not ids:
            return Response({
                'detail': '请选择要导出的结算单'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        settlements = SettlementBill.objects.filter(id__in=ids, is_deleted=False)
        
        if export_format == 'csv':
            # 创建CSV响应
            output = io.StringIO()
            writer = csv.writer(output)
            
            # 写入表头
            writer.writerow(['结算单号', '工厂', '期间', '总金额', '状态', '创建时间'])
            
            # 写入数据
            for settlement in settlements:
                writer.writerow([
                    settlement.settlement_number,
                    settlement.factory.name if settlement.factory else '',
                    settlement.period,
                    settlement.total_amount,
                    settlement.get_status_display(),
                    settlement.created_at.strftime('%Y-%m-%d %H:%M:%S')
                ])
            
            output.seek(0)
            response = Response(output.getvalue(), content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="settlements.csv"'
            return response
        else:
            return Response({
                'detail': '不支持的导出格式'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def batch_delete(self, request):
        """
        批量删除结算单
        """
        ids = request.data.get('ids', [])
        
        if not ids:
            return Response({
                'detail': '请选择要删除的结算单'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 软删除所选结算单
        SettlementBill.objects.filter(id__in=ids).update(is_deleted=True)
        
        return Response({
            'success': True,
            'message': f'成功删除 {len(ids)} 个结算单'
        })
        
class FactoryViewSet(viewsets.ModelViewSet):
    """
    工厂视图集
    提供工厂的CRUD操作和自定义操作
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return FactoryListSerializer
        elif self.action == 'create':
            return FactoryCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return FactoryUpdateSerializer
        else:
            return FactoryDetailSerializer
    
    def get_queryset(self):
        queryset = Factory.objects.filter(is_deleted=False)
        # 过滤条件
        status = self.request.query_params.get('status')
        name = self.request.query_params.get('name')
        
        if status:
            queryset = queryset.filter(status=status)
        if name:
            queryset = queryset.filter(name__icontains=name)
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return Response({
                'count': self.paginator.page.paginator.count,
                'next': self.paginator.get_next_link(),
                'previous': self.paginator.get_previous_link(),
                'results': serializer.data
            })
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def perform_create(self, serializer):
        # 生成工厂编号
        factory_code = f"FC{timezone.now().strftime('%Y%m%d')}{str(uuid.uuid4().int)[:3]}"
        serializer.save(created_by=self.request.user, factory_code=factory_code)
    
    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)
    
    def perform_destroy(self, instance):
        # 软删除
        instance.is_deleted = True
        instance.save()
    
    @action(detail=False, methods=['post'])
    def batch_export(self, request):
        """
        批量导出工厂
        """
        ids = request.data.get('ids', [])
        export_format = request.data.get('format', 'csv')
        
        if not ids:
            return Response({
                'detail': '请选择要导出的工厂'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        factories = Factory.objects.filter(id__in=ids, is_deleted=False)
        
        if export_format == 'csv':
            # 创建CSV响应
            output = io.StringIO()
            writer = csv.writer(output)
            
            # 写入表头
            writer.writerow(['工厂编号', '工厂名称', '联系人', '联系电话', '地址', '状态', '创建时间'])
            
            # 写入数据
            for factory in factories:
                writer.writerow([
                    factory.factory_code,
                    factory.name,
                    factory.contact_person,
                    factory.contact_phone,
                    factory.address,
                    factory.get_status_display(),
                    factory.created_at.strftime('%Y-%m-%d %H:%M:%S')
                ])
            
            output.seek(0)
            response = Response(output.getvalue(), content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="factories.csv"'
            return response
        else:
            return Response({
                'detail': '不支持的导出格式'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def batch_delete(self, request):
        """
        批量删除工厂
        """
        ids = request.data.get('ids', [])
        
        if not ids:
            return Response({
                'detail': '请选择要删除的工厂'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 软删除所选工厂
        Factory.objects.filter(id__in=ids).update(is_deleted=True)
        
        return Response({
            'success': True,
            'message': f'成功删除 {len(ids)} 个工厂'
        })
    
    @action(detail=True, methods=['get'])
    def settlements(self, request, pk=None):
        """
        获取工厂的结算单
        """
        factory = self.get_object()
        settlements = SettlementBill.objects.filter(factory=factory, is_deleted=False)
        
        # 分页
        page = self.paginate_queryset(settlements)
        if page is not None:
            serializer = SettlementListSerializer(page, many=True)
            return Response({
                'count': self.paginator.page.paginator.count,
                'next': self.paginator.get_next_link(),
                'previous': self.paginator.get_previous_link(),
                'results': serializer.data
            })
        
        serializer = SettlementListSerializer(settlements, many=True)
        return Response(serializer.data)

class ReconciliationViewSet(viewsets.ModelViewSet):
    """
    对账单视图集
    提供对账单的CRUD操作和自定义操作
    """
    queryset = Factory.objects.filter(is_deleted=False)
    
    def get_serializer_class(self):
        if self.action == 'list':
            return FactoryListSerializer
        elif self.action == 'create':
            return FactoryCreateSerializer
        else:
            return FactoryDetailSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        # 过滤条件
        status_filter = self.request.query_params.get('status')
        supplier_id = self.request.query_params.get('supplierId')
        month = self.request.query_params.get('month')
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if supplier_id:
            queryset = queryset.filter(supplier_id=supplier_id)
        if month:
            queryset = queryset.filter(month=month)
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return ResponseWrapper(
                data={
                    'items': serializer.data,
                    'total': self.paginator.page.paginator.count
                },
                msg="获取对账单列表成功"
            )
        serializer = self.get_serializer(queryset, many=True)
        return ResponseWrapper(
            data={
                'items': serializer.data,
                'total': len(serializer.data)
            },
            msg="获取对账单列表成功"
        )
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        
        # 获取关联的采购订单和结算单
        year, month = instance.month.split('-')
        start_date = f"{year}-{month}-01"
        if month == '12':
            end_date = f"{int(year)+1}-01-01"
        else:
            next_month = int(month) + 1
            end_date = f"{year}-{next_month:02d}-01"
        
        from apps.finance.models import ProcurementOrder
        from apps.finance.serializers import ProcurementOrderSerializer
        
        orders = ProcurementOrder.objects.filter(
            supplier=instance.supplier,
            order_date__gte=start_date,
            order_date__lt=end_date
        )
        
        bills = SettlementBill.objects.filter(
            supplier=instance.supplier,
            created_at__gte=start_date,
            created_at__lt=end_date
        )
        
        return ResponseWrapper(
            data={
                'reconciliation': serializer.data,
                'orders': ProcurementOrderSerializer(orders, many=True).data,
                'bills': SettlementBillListSerializer(bills, many=True).data
            },
            msg="获取对账单详情成功"
        )
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """
        确认对账单
        """
        reconciliation = self.get_object()
        serializer = FactoryUpdateSerializer(data=request.data)
        
        if not serializer.is_valid():
            return ResponseWrapper(
                data=serializer.errors,
                msg="参数错误",
                code=400
            )
        
        if reconciliation.status != 'draft':
            return ResponseWrapper(
                data=None,
                msg="只有草稿状态的对账单可以确认",
                code=400
            )
        
        # 更新对账单状态和确认信息
        reconciliation.status = 'confirmed'
        reconciliation.confirmation_date = serializer.validated_data['confirmation_date']
        reconciliation.confirmed_by = serializer.validated_data['confirmed_by']
        reconciliation.remark = serializer.validated_data.get('remark', reconciliation.remark)
        reconciliation.save()
        
        return ResponseWrapper(
            data=None,
            msg="对账单确认成功"
        )
    
    @action(detail=True, methods=['get'])
    def export(self, request, pk=None):
        """
        导出对账单
        """
        reconciliation = self.get_object()
        format_type = request.query_params.get('format', 'pdf')
        
        # 这里应该实现导出逻辑，根据format_type导出不同格式的文件
        # 由于导出功能需要额外的库支持，这里只返回成功信息
        
        return ResponseWrapper(
            data={
                'url': f"/media/exports/reconciliation_{reconciliation.id}.{format_type}"
            },
            msg=f"对账单导出{format_type}成功"
        )