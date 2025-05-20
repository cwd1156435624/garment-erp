from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.utils import timezone
from .models import Order, ProductionPlan, ProductionException
from .serializers import ProductionPlanSerializer, ProductionExceptionSerializer
from apps.system.utils import ResponseWrapper

class ProgressView(APIView):
    """
    生产进度视图
    提供订单和工序的进度跟踪功能
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        order_id = request.query_params.get('orderId')
        process_id = request.query_params.get('processId')  # 这里的process_id实际对应ProductionPlan的id
        
        if not order_id and not process_id:
            return ResponseWrapper.error('订单ID或工序ID至少需要提供一个')
        
        if order_id:
            # 获取订单进度信息
            try:
                order = Order.objects.get(id=order_id, is_deleted=False)
                processes = ProductionPlan.objects.filter(order=order, is_deleted=False)
                
                # 计算订单整体完成率
                total_progress = 0
                if processes.exists():
                    total_progress = sum(p.progress for p in processes) / processes.count()
                
                # 构建订单进度数据
                order_progress = {
                    'id': order.id,
                    'orderNumber': order.order_number,
                    'productName': order.product_name,
                    'quantity': order.quantity,
                    'status': order.status,
                    'progress': total_progress,
                    'deliveryDate': order.delivery_date.strftime('%Y-%m-%d') if order.delivery_date else None
                }
                
                # 构建工序进度数据
                processes_progress = []
                for process in processes:
                    processes_progress.append({
                        'id': process.id,
                        'planNumber': process.plan_number,
                        'startDate': process.start_date.strftime('%Y-%m-%d') if process.start_date else None,
                        'endDate': process.end_date.strftime('%Y-%m-%d') if process.end_date else None,
                        'status': process.status,
                        'progress': process.progress,
                        'actualStartDate': process.actual_start_date.strftime('%Y-%m-%d') if process.actual_start_date else None,
                        'actualEndDate': process.actual_end_date.strftime('%Y-%m-%d') if process.actual_end_date else None,
                        'responsiblePerson': process.responsible_person.username if process.responsible_person else None
                    })
                
                return ResponseWrapper.success({
                    'order': order_progress,
                    'processes': processes_progress
                })
            except Order.DoesNotExist:
                return ResponseWrapper.error('订单不存在')
        else:
            # 获取单个工序进度信息
            try:
                process = ProductionPlan.objects.get(id=process_id, is_deleted=False)
                order = process.order
                
                # 构建工序进度数据
                process_progress = {
                    'id': process.id,
                    'planNumber': process.plan_number,
                    'startDate': process.start_date.strftime('%Y-%m-%d') if process.start_date else None,
                    'endDate': process.end_date.strftime('%Y-%m-%d') if process.end_date else None,
                    'status': process.status,
                    'progress': process.progress,
                    'actualStartDate': process.actual_start_date.strftime('%Y-%m-%d') if process.actual_start_date else None,
                    'actualEndDate': process.actual_end_date.strftime('%Y-%m-%d') if process.actual_end_date else None,
                    'responsiblePerson': process.responsible_person.username if process.responsible_person else None
                }
                
                # 构建订单进度数据
                order_progress = {
                    'id': order.id,
                    'orderNumber': order.order_number,
                    'productName': order.product_name,
                    'quantity': order.quantity,
                    'status': order.status,
                    'deliveryDate': order.delivery_date.strftime('%Y-%m-%d') if order.delivery_date else None
                }
                
                return ResponseWrapper.success({
                    'order': order_progress,
                    'processes': [process_progress]
                })
            except ProductionPlan.DoesNotExist:
                return ResponseWrapper.error('工序不存在')

class ProgressUpdateView(APIView):
    """
    进度更新视图
    提供更新工序进度的功能
    """
    permission_classes = [IsAuthenticated]
    
    def put(self, request, process_id):
        try:
            process = ProductionPlan.objects.get(id=process_id, is_deleted=False)
            
            # 获取更新数据
            completed_quantity = request.data.get('completedQuantity')
            status = request.data.get('status')
            remark = request.data.get('remark')
            
            # 更新进度
            if completed_quantity is not None:
                # 假设订单总数量存储在order.quantity中
                total_quantity = process.order.quantity
                if total_quantity > 0:
                    process.progress = min(100, (float(completed_quantity) / total_quantity) * 100)
            
            # 更新状态
            if status:
                if status in dict(ProductionPlan.STATUS_CHOICES):
                    process.status = status
                    if status == 'in_progress' and not process.actual_start_date:
                        process.actual_start_date = timezone.now().date()
                    elif status == 'completed' and not process.actual_end_date:
                        process.actual_end_date = timezone.now().date()
                        process.progress = 100
            
            # 更新备注
            if remark:
                if process.remarks:
                    process.remarks += f"\n{timezone.now().strftime('%Y-%m-%d %H:%M:%S')} - {remark}"
                else:
                    process.remarks = f"{timezone.now().strftime('%Y-%m-%d %H:%M:%S')} - {remark}"
            
            process.save()
            
            # 更新订单状态
            self.update_order_status(process.order)
            
            return ResponseWrapper.success(ProductionPlanSerializer(process).data, '进度更新成功')
        except ProductionPlan.DoesNotExist:
            return ResponseWrapper.error('工序不存在')
    
    def update_order_status(self, order):
        """
        根据所有工序的状态更新订单状态
        """
        processes = ProductionPlan.objects.filter(order=order, is_deleted=False)
        
        if not processes.exists():
            return
        
        # 检查是否所有工序都已完成
        all_completed = all(p.status == 'completed' for p in processes)
        any_in_progress = any(p.status == 'in_progress' for p in processes)
        
        if all_completed:
            order.status = 'completed'
        elif any_in_progress:
            order.status = 'processing'
        
        order.save()

class IssueReportView(APIView):
    """
    问题报告视图
    提供记录生产问题的功能
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, process_id):
        try:
            process = ProductionPlan.objects.get(id=process_id, is_deleted=False)
            
            # 获取问题数据
            issue_type = request.data.get('type')
            description = request.data.get('description')
            quantity = request.data.get('quantity')
            images = request.data.get('images', [])
            
            if not issue_type or not description:
                return ResponseWrapper.error('问题类型和描述不能为空')
            
            # 创建生产异常记录
            exception = ProductionException.objects.create(
                production_plan=process,
                exception_type=issue_type,
                severity='medium',  # 默认中等严重程度
                description=description,
                reported_by=request.user
            )
            
            # 更新工序备注
            if process.remarks:
                process.remarks += f"\n{timezone.now().strftime('%Y-%m-%d %H:%M:%S')} - 报告问题: {description}"
            else:
                process.remarks = f"{timezone.now().strftime('%Y-%m-%d %H:%M:%S')} - 报告问题: {description}"
            
            process.save()
            
            return ResponseWrapper.success(ProductionExceptionSerializer(exception).data, '问题报告成功')
        except ProductionPlan.DoesNotExist:
            return ResponseWrapper.error('工序不存在')