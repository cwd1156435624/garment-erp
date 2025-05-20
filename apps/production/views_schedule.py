from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.utils import timezone
from datetime import datetime
from .models import Order, ProductionPlan
from .serializers import ProductionPlanSerializer
from apps.system.utils import ResponseWrapper
from apps.users.models import User

class ScheduleViewSet(viewsets.ModelViewSet):
    """
    生产调度视图集
    提供生产计划的管理功能
    """
    queryset = ProductionPlan.objects.filter(is_deleted=False)
    serializer_class = ProductionPlanSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        # 获取查询参数
        workshop = self.request.query_params.get('workshop')
        line = self.request.query_params.get('line')
        date = self.request.query_params.get('date')
        
        # 根据查询参数过滤
        if workshop:
            queryset = queryset.filter(remarks__icontains=workshop)  # 假设车间信息存储在remarks字段中
        if line:
            queryset = queryset.filter(remarks__icontains=line)  # 假设生产线信息存储在remarks字段中
        if date:
            try:
                filter_date = datetime.strptime(date, '%Y-%m-%d').date()
                queryset = queryset.filter(Q(start_date=filter_date) | Q(end_date=filter_date))
            except ValueError:
                pass
                
        return queryset
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return ResponseWrapper.success({
                'items': serializer.data,
                'total': self.paginator.page.paginator.count
            })
        serializer = self.get_serializer(queryset, many=True)
        return ResponseWrapper.success({
            'items': serializer.data,
            'total': queryset.count()
        })
    
    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        # 检查资源冲突
        start_time = data.get('startTime')
        end_time = data.get('endTime')
        workshop_id = data.get('workshopId')
        line_id = data.get('lineId')
        operators = data.get('operators', [])
        
        # 这里简化处理，实际应该检查资源是否已被占用
        
        # 创建生产计划
        serializer = self.get_serializer(data={
            'order': data.get('orderId'),
            'plan_number': f'PP{timezone.now().strftime("%Y%m%d%H%M%S")}',
            'start_date': start_time.split('T')[0] if start_time else None,
            'end_date': end_time.split('T')[0] if end_time else None,
            'status': 'planned',
            'responsible_person': request.user.id,
            'remarks': f'车间: {workshop_id}, 生产线: {line_id}, 操作员: {",".join(operators)}'
        })
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return ResponseWrapper.success(serializer.data, '创建成功')
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        data = request.data.copy()
        
        # 更新生产计划
        update_data = {
            'start_date': data.get('startTime', '').split('T')[0] if data.get('startTime') else instance.start_date,
            'end_date': data.get('endTime', '').split('T')[0] if data.get('endTime') else instance.end_date,
            'status': data.get('priority', instance.status),
            'remarks': instance.remarks
        }
        
        # 更新备注中的资源信息
        if data.get('workshopId') or data.get('lineId') or data.get('operators'):
            remarks_parts = instance.remarks.split(', ') if instance.remarks else []
            workshop_part = f'车间: {data.get("workshopId")}' if data.get('workshopId') else next((p for p in remarks_parts if p.startswith('车间:')), '')
            line_part = f'生产线: {data.get("lineId")}' if data.get('lineId') else next((p for p in remarks_parts if p.startswith('生产线:')), '')
            operators_part = f'操作员: {",".join(data.get("operators"))}' if data.get('operators') else next((p for p in remarks_parts if p.startswith('操作员:')), '')
            update_data['remarks'] = f'{workshop_part}, {line_part}, {operators_part}'
        
        serializer = self.get_serializer(instance, data=update_data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return ResponseWrapper.success(serializer.data, '更新成功')
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_deleted = True
        instance.save()
        return ResponseWrapper.success(None, '删除成功')
    
    @action(detail=False, methods=['get'])
    def available_resources(self, request):
        """
        获取可用资源
        返回指定时间段内可用的生产资源
        """
        start_time = request.query_params.get('startTime')
        end_time = request.query_params.get('endTime')
        resource_type = request.query_params.get('resourceType')
        
        # 这里简化处理，实际应该查询数据库获取可用资源
        # 返回模拟数据
        workshops = [
            {'id': 'w1', 'name': '一号车间'},
            {'id': 'w2', 'name': '二号车间'},
            {'id': 'w3', 'name': '三号车间'}
        ]
        
        lines = [
            {'id': 'l1', 'name': '生产线1', 'workshop_id': 'w1'},
            {'id': 'l2', 'name': '生产线2', 'workshop_id': 'w1'},
            {'id': 'l3', 'name': '生产线3', 'workshop_id': 'w2'}
        ]