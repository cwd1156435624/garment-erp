from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.http import HttpResponse
from django.utils import timezone
import csv
import json
from datetime import datetime
from .models import OperationLog
from .serializers import OperationLogSerializer
from .utils import ResponseWrapper

class LogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    操作日志视图集
    提供日志查询和导出功能
    """
    queryset = OperationLog.objects.all()
    serializer_class = OperationLogSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        # 获取查询参数
        log_type = self.request.query_params.get('type')
        user_id = self.request.query_params.get('userId')
        module = self.request.query_params.get('module')
        start_time = self.request.query_params.get('startTime')
        end_time = self.request.query_params.get('endTime')
        
        # 根据查询参数过滤
        if log_type:
            queryset = queryset.filter(operation_type=log_type)
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        if module:
            queryset = queryset.filter(module=module)
        if start_time:
            try:
                start_datetime = datetime.strptime(start_time, '%Y-%m-%d')
                queryset = queryset.filter(operation_time__gte=start_datetime)
            except ValueError:
                pass
        if end_time:
            try:
                end_datetime = datetime.strptime(end_time, '%Y-%m-%d')
                end_datetime = end_datetime.replace(hour=23, minute=59, second=59)
                queryset = queryset.filter(operation_time__lte=end_datetime)
            except ValueError:
                pass
                
        return queryset.order_by('-created_at')
    
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
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return ResponseWrapper.success(serializer.data)
    
    @action(detail=False, methods=['get'])
    def export(self, request):
        """
        导出日志
        支持CSV和JSON格式导出
        """
        queryset = self.filter_queryset(self.get_queryset())
        format_type = request.query_params.get('format', 'csv')
        
        if format_type == 'json':
            # 导出为JSON格式
            serializer = self.get_serializer(queryset, many=True)
            response = HttpResponse(json.dumps(serializer.data, ensure_ascii=False), content_type='application/json')
            response['Content-Disposition'] = f'attachment; filename="logs_{timezone.now().strftime("%Y%m%d%H%M%S")}.json"'
            return response
        else:
            # 默认导出为CSV格式
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="logs_{timezone.now().strftime("%Y%m%d%H%M%S")}.csv"'
            
            writer = csv.writer(response)
            writer.writerow(['操作人', '操作类型', '操作时间', '操作模块', '操作描述', 'IP地址', '是否成功'])
            
            for log in queryset:
                writer.writerow([
                    log.user.username,
                    log.get_operation_type_display(),
                    log.operation_time.strftime('%Y-%m-%d %H:%M:%S'),
                    log.module,
                    log.operation_desc,
                    log.ip_address,
                    '成功' if log.is_success else '失败'
                ])
            
            return response