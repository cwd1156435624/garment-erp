from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Q
from django.shortcuts import get_object_or_404
import uuid
import datetime

from .models import Barcode, ScanningHistory, BarcodeGenerationBatch, PrintJob
from .serializers import (
    BarcodeSerializer, BarcodeGenerationSerializer, BarcodePrintSerializer,
    ScanningHistorySerializer, BarcodeRecognizeSerializer,
    MaterialInboundScanningSerializer, MaterialOutboundScanningSerializer,
    ProductionProcessScanningSerializer, ProductPackagingScanningSerializer
)
from apps.materials.models import Material, Location, InventoryTransaction, Inventory
from apps.production.models import Order
# 已移除ResponseWrapper导入，使用标准的Response

class BarcodeViewSet(viewsets.ModelViewSet):
    """
    条码视图集
    提供条码的CRUD操作和自定义操作
    """
    queryset = Barcode.objects.filter(is_deleted=False)
    serializer_class = BarcodeSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        # 过滤条件
        barcode_type = self.request.query_params.get('type')
        status_filter = self.request.query_params.get('status')
        search_text = self.request.query_params.get('search')
        reference_id = self.request.query_params.get('reference_id')
        
        if barcode_type:
            queryset = queryset.filter(barcode_type=barcode_type)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if search_text:
            queryset = queryset.filter(
                Q(barcode_number__icontains=search_text) |
                Q(reference_id__icontains=search_text)
            )
        if reference_id:
            queryset = queryset.filter(reference_id=reference_id)
        
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
        serializer.save(created_by=self.request.user)
        
    def perform_destroy(self, instance):
        # 软删除
        instance.is_deleted = True
        instance.save()
        
    @action(detail=False, methods=['post'])
    def batch_export(self, request):
        """
        批量导出条码
        """
        ids = request.data.get('ids', [])
        if not ids:
            return Response({'error': '请选择要导出的条码'}, status=status.HTTP_400_BAD_REQUEST)
            
        queryset = self.get_queryset().filter(id__in=ids)
        serializer = self.get_serializer(queryset, many=True)
        
        # 返回导出数据
        return Response({
            'count': len(serializer.data),
            'results': serializer.data
        })
    
    @action(detail=False, methods=['post'])
    def batch_delete(self, request):
        """
        批量删除条码
        """
        ids = request.data.get('ids', [])
        if not ids:
            return Response({'error': '请选择要删除的条码'}, status=status.HTTP_400_BAD_REQUEST)
            
        queryset = self.get_queryset().filter(id__in=ids)
        count = queryset.count()
        
        # 执行软删除
        for barcode in queryset:
            barcode.is_deleted = True
            barcode.save()
        
        return Response({
            'count': count,
            'message': f'成功删除 {count} 个条码'
        })
    
    @action(detail=False, methods=['post'])
    def generate(self, request):
        """
        批量生成条码
        """
        serializer = BarcodeGenerationSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                'error': '参数错误',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        barcode_type = serializer.validated_data['type']
        quantity = serializer.validated_data['quantity']
        prefix = serializer.validated_data.get('prefix', '')
        reference_ids = serializer.validated_data.get('reference_ids', [])
        
        # 生成批次号
        batch_number = f"BG{timezone.now().strftime('%Y%m%d%H%M%S')}"
        
        # 获取当前最大编号
        last_barcode = Barcode.objects.filter(barcode_type=barcode_type).order_by('-barcode_number').first()
        if last_barcode and last_barcode.barcode_number.isdigit():
            start_number = int(last_barcode.barcode_number) + 1
        else:
            start_number = 1000000
        
        end_number = start_number + quantity - 1
        
        # 创建生成批次记录
        batch = BarcodeGenerationBatch.objects.create(
            batch_number=batch_number,
            barcode_type=barcode_type,
            quantity=quantity,
            prefix=prefix,
            start_number=start_number,
            end_number=end_number,
            created_by=request.user
        )
        
        # 批量生成条码
        barcodes = []
        for i in range(quantity):
            barcode_number = f"{prefix}{start_number + i}"
            reference_id = reference_ids[i] if i < len(reference_ids) else None
            
            # 根据条码类型关联不同的对象
            kwargs = {
                'barcode_number': barcode_number,
                'barcode_type': barcode_type,
                'reference_id': reference_id,
                'created_by': request.user
            }
            
            if barcode_type == 'material' and reference_id:
                try:
                    material = Material.objects.get(id=reference_id)
                    kwargs['material'] = material
                except Material.DoesNotExist:
                    pass
            elif barcode_type == 'product' and reference_id:
                try:
                    product = Product.objects.get(id=reference_id)
                    kwargs['product'] = product
                except Product.DoesNotExist:
                    pass
            elif barcode_type == 'location' and reference_id:
                try:
                    location = Location.objects.get(id=reference_id)
                    kwargs['location'] = location
                except Location.DoesNotExist:
                    pass
            elif barcode_type == 'order' and reference_id:
                try:
                    order = Order.objects.get(id=reference_id)
                    kwargs['order'] = order
                except Order.DoesNotExist:
                    pass
            elif barcode_type == 'process' and reference_id:
                try:
                    process = Process.objects.get(id=reference_id)
                    kwargs['process'] = process
                except Process.DoesNotExist:
                    pass
            
            barcode = Barcode.objects.create(**kwargs)
            barcodes.append(barcode)
        
        return Response({
            'batch': batch.batch_number,
            'quantity': quantity,
            'barcodes': BarcodeSerializer(barcodes, many=True).data,
            'message': '条码生成成功'
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'])
    def print(self, request):
        """
        打印条码
        """
        serializer = BarcodePrintSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                'error': '参数错误',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        barcode_ids = serializer.validated_data['barcode_ids']
        printer_name = serializer.validated_data['printer_name']
        format_type = serializer.validated_data['format']
        copies = serializer.validated_data.get('copies', 1)
        
        # 获取条码对象
        barcodes = Barcode.objects.filter(id__in=barcode_ids)
        if not barcodes.exists():
            return Response({
                'error': '未找到指定条码'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # 生成打印任务编号
        job_number = f"PJ{timezone.now().strftime('%Y%m%d%H%M%S')}"
        
        # 创建打印任务
        print_job = PrintJob.objects.create(
            job_number=job_number,
            printer_name=printer_name,
            format=format_type,
            copies=copies,
            status='processing',
            created_by=request.user
        )
        print_job.barcodes.set(barcodes)
        
        # 更新条码打印信息
        for barcode in barcodes:
            barcode.print_count += 1
            barcode.last_print_time = timezone.now()
            barcode.save()
        
        # 这里应该实现实际的打印逻辑，连接打印机等
        # 由于打印功能需要额外的硬件支持，这里只更新状态
        print_job.status = 'completed'
        print_job.save()
        
        return Response({
            'job_number': job_number,
            'printer': printer_name,
            'format': format_type,
            'copies': copies,
            'barcode_count': barcodes.count(),
            'message': '条码打印任务已提交'
        }, status=status.HTTP_200_OK)

class ScanningViewSet(viewsets.ViewSet):
    """
    扫码操作视图集
    提供各种扫码操作的接口
    """
    
    @action(detail=False, methods=['post'])
    def recognize(self, request):
        """
        条码识别
        """
        serializer = BarcodeRecognizeSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                'error': '参数错误',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        barcode_number = serializer.validated_data['barcode']
        
        try:
            barcode = Barcode.objects.get(barcode_number=barcode_number)
        except Barcode.DoesNotExist:
            return Response({
                'error': '条码不存在'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # 根据条码类型返回不同的数据
        data = {
            'type': barcode.barcode_type,
            'barcode': BarcodeSerializer(barcode).data
        }
        
        if barcode.barcode_type == 'material' and barcode.material:
            from apps.warehouse.serializers import MaterialSerializer
            data['data'] = MaterialSerializer(barcode.material).data
        elif barcode.barcode_type == 'product' and barcode.product:
            from apps.production.serializers import ProductSerializer
            data['data'] = ProductSerializer(barcode.product).data
        elif barcode.barcode_type == 'location' and barcode.location:
            from apps.warehouse.serializers import LocationSerializer
            data['data'] = LocationSerializer(barcode.location).data
        elif barcode.barcode_type == 'order' and barcode.order:
            from apps.production.serializers import OrderSerializer
            data['data'] = OrderSerializer(barcode.order).data
        elif barcode.barcode_type == 'process' and barcode.process:
            from apps.production.serializers import ProcessSerializer
            data['data'] = ProcessSerializer(barcode.process).data
        
        return Response(data)
    
    @action(detail=False, methods=['post'], url_path='material/inbound')
    def material_inbound(self, request):
        """
        物料入库扫码
        """
        serializer = MaterialInboundScanningSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                'error': '参数错误',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        material_barcode_number = serializer.validated_data['materialBarcode']
        location_barcode_number = serializer.validated_data['locationBarcode']
        quantity = serializer.validated_data['quantity']
        batch_number = serializer.validated_data.get('batchNumber')
        
        # 获取物料条码和库位条码
        try:
            material_barcode = Barcode.objects.get(barcode_number=material_barcode_number, barcode_type='material')
            location_barcode = Barcode.objects.get(barcode_number=location_barcode_number, barcode_type='location')
        except Barcode.DoesNotExist:
            return Response({
                'error': '条码不存在或类型不匹配'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # 验证物料和库位
        if not material_barcode.material:
            return Response({
                'error': '物料条码未关联物料'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not location_barcode.location:
            return Response({
                'error': '库位条码未关联库位'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        material = material_barcode.material
        location = location_barcode.location
        
        # 创建入库记录
        transaction = InventoryTransaction.objects.create(
            material=material,
            location=location,
            transaction_type='inbound',
            quantity=quantity,
            batch_number=batch_number,
            created_by=request.user
        )
        
        # 更新库存
        inventory, created = Inventory.objects.get_or_create(
            material=material,
            location=location,
            defaults={'quantity': 0}
        )
        inventory.quantity += quantity
        inventory.last_transaction = transaction
        inventory.save()
        
        # 记录扫码历史
        scanning_history = ScanningHistory.objects.create(
            barcode=material_barcode,
            operation_type='material_inbound',
            quantity=quantity,
            location_barcode=location_barcode,
            batch_number=batch_number,
            result='success',
            created_by=request.user
        )
        
        return Response({
            'transaction_id': transaction.id,
            'material': material.name,
            'location': location.name,
            'quantity': quantity,
            'current_stock': inventory.quantity
        })
    
    @action(detail=False, methods=['post'], url_path='material/outbound')
    def material_outbound(self, request):
        """
        物料出库扫码
        """
        serializer = MaterialOutboundScanningSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                'error': '参数错误',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        material_barcode_number = serializer.validated_data['materialBarcode']
        location_barcode_number = serializer.validated_data['locationBarcode']
        quantity = serializer.validated_data['quantity']
        order_barcode_number = serializer.validated_data.get('orderBarcode')
        
        # 获取物料条码和库位条码
        try:
            material_barcode = Barcode.objects.get(barcode_number=material_barcode_number, barcode_type='material')
            location_barcode = Barcode.objects.get(barcode_number=location_barcode_number, barcode_type='location')
        except Barcode.DoesNotExist:
            return Response({
                'error': '条码不存在或类型不匹配'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # 验证物料和库位
        if not material_barcode.material:
            return Response({
                'error': '物料条码未关联物料'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not location_barcode.location:
            return Response({
                'error': '库位条码未关联库位'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        material = material_barcode.material
        location = location_barcode.location
        
        # 检查库存是否足够
        try:
            inventory = Inventory.objects.get(material=material, location=location)
            if inventory.quantity < quantity:
                return Response({
                    'error': f'库存不足，当前库存: {inventory.quantity}'
                }, status=status.HTTP_400_BAD_REQUEST)
        except Inventory.DoesNotExist:
            return Response({
                'error': '该库位没有此物料库存'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # 获取订单条码（如果有）
        order_barcode = None
        if order_barcode_number:
            try:
                order_barcode = Barcode.objects.get(barcode_number=order_barcode_number, barcode_type='order')
            except Barcode.DoesNotExist:
                return Response({
                    'error': '订单条码不存在或类型不匹配'
                }, status=status.HTTP_404_NOT_FOUND)
        
        # 创建出库记录
        transaction = InventoryTransaction.objects.create(
            material=material,
            location=location,
            transaction_type='outbound',
            quantity=quantity,
            order=order_barcode.order if order_barcode and order_barcode.order else None,
            created_by=request.user
        )
        
        # 更新库存
        inventory.quantity -= quantity
        inventory.last_transaction = transaction
        inventory.save()
        
        # 记录扫码历史
        scanning_history = ScanningHistory.objects.create(
            barcode=material_barcode,
            operation_type='material_outbound',
            quantity=quantity,
            location_barcode=location_barcode,
            order_barcode=order_barcode,
            result='success',
            created_by=request.user
        )
        
        return Response({
            'transaction_id': transaction.id,
            'material': material.name,
            'location': location.name,
            'quantity': quantity,
            'current_stock': inventory.quantity
        })
    
    @action(detail=False, methods=['post'], url_path='production/process')
    def production_process(self, request):
        """
        生产过程扫码
        """
        serializer = ProductionProcessScanningSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                'error': '参数错误',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        order_barcode_number = serializer.validated_data['orderBarcode']
        process_barcode_number = serializer.validated_data['processBarcode']
        operator_barcode_number = serializer.validated_data['operatorBarcode']
        quantity = serializer.validated_data['quantity']
        
        # 获取订单条码、工序条码和操作员条码
        try:
            order_barcode = Barcode.objects.get(barcode_number=order_barcode_number, barcode_type='order')
            process_barcode = Barcode.objects.get(barcode_number=process_barcode_number, barcode_type='process')
            operator_barcode = Barcode.objects.get(barcode_number=operator_barcode_number, barcode_type='operator')
        except Barcode.DoesNotExist:
            return Response({
                'error': '条码不存在或类型不匹配'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # 验证订单和工序
        if not order_barcode.order:
            return Response({
                'error': '订单条码未关联订单'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not process_barcode.process:
            return Response({
                'error': '工序条码未关联工序'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        order = order_barcode.order
        process = process_barcode.process
        operator_id = operator_barcode.operator_id
        
        # 创建生产记录
        production_record = ProductionRecord.objects.create(
            order=order,
            process=process,
            operator_id=operator_id,
            quantity=quantity,
            created_by=request.user
        )
        
        # 记录扫码历史
        scanning_history = ScanningHistory.objects.create(
            barcode=order_barcode,
            operation_type='production_process',
            quantity=quantity,
            order_barcode=order_barcode,
            process_barcode=process_barcode,
            operator_barcode=operator_barcode,
            result='success',
            created_by=request.user
        )
        
        return Response({
            'record_id': production_record.id,
            'order': order.order_number,
            'process': process.name,
            'operator': operator_id,
            'quantity': quantity
        })
    
    @action(detail=False, methods=['post'], url_path='production/packaging')
    def product_packaging(self, request):
        """
        产品包装扫码
        """
        serializer = ProductPackagingScanningSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                'error': '参数错误',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        product_barcode_number = serializer.validated_data['productBarcode']
        package_barcode_number = serializer.validated_data['packageBarcode']
        quantity = serializer.validated_data['quantity']
        
        # 获取产品条码和包装条码
        try:
            product_barcode = Barcode.objects.get(barcode_number=product_barcode_number, barcode_type='product')
            package_barcode = Barcode.objects.get(barcode_number=package_barcode_number, barcode_type='package')
        except Barcode.DoesNotExist:
            return Response({
                'error': '条码不存在或类型不匹配'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # 验证产品
        if not product_barcode.product:
            return Response({
                'error': '产品条码未关联产品'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        product = product_barcode.product
        
        # 记录扫码历史
        scanning_history = ScanningHistory.objects.create(
            barcode=product_barcode,
            operation_type='product_packaging',
            quantity=quantity,
            package_barcode=package_barcode,
            result='success',
            created_by=request.user
        )
        
        return Response({
            'product': product.name,
            'package': package_barcode.barcode_number,
            'quantity': quantity
        })

class ScanningHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    扫码历史视图集
    提供扫码历史的查询操作
    """
    queryset = ScanningHistory.objects.all()
    serializer_class = ScanningHistorySerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        # 过滤条件
        barcode = self.request.query_params.get('barcode')
        operation_type = self.request.query_params.get('operationType')
        start_time = self.request.query_params.get('startTime')
        end_time = self.request.query_params.get('endTime')
        
        if barcode:
            try:
                barcode_obj = Barcode.objects.get(barcode_number=barcode)
                queryset = queryset.filter(
                    Q(barcode=barcode_obj) |
                    Q(location_barcode=barcode_obj) |
                    Q(order_barcode=barcode_obj) |
                    Q(process_barcode=barcode_obj) |
                    Q(operator_barcode=barcode_obj) |
                    Q(package_barcode=barcode_obj)
                )
            except Barcode.DoesNotExist:
                return ScanningHistory.objects.none()
        
        if operation_type:
            queryset = queryset.filter(operation_type=operation_type)
        
        if start_time:
            queryset = queryset.filter(created_at__gte=start_time)
        
        if end_time:
            queryset = queryset.filter(created_at__lte=end_time)
        
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
        serializer.save(created_by=self.request.user)
        
    @action(detail=False, methods=['post'])
    def batch_export(self, request):
        """
        批量导出扫码历史
        """
        ids = request.data.get('ids', [])
        if not ids:
            return Response({'error': '请选择要导出的扫码历史'}, status=status.HTTP_400_BAD_REQUEST)
            
        queryset = self.get_queryset().filter(id__in=ids)
        serializer = self.get_serializer(queryset, many=True)
        
        # 返回导出数据
        return Response({
            'count': len(serializer.data),
            'results': serializer.data
        })
        
    @action(detail=False, methods=['post'])
    def batch_delete(self, request):
        """
        批量删除扫码历史
        """
        ids = request.data.get('ids', [])
        if not ids:
            return Response({'error': '请选择要删除的扫码历史'}, status=status.HTTP_400_BAD_REQUEST)
            
        queryset = self.get_queryset().filter(id__in=ids)
        count = queryset.count()
        
        # 执行删除
        queryset.delete()
        
        return Response({
            'count': count,
            'message': f'成功删除 {count} 条扫码历史记录'
        })