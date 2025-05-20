from rest_framework import status, views, viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django.utils import timezone
from django.db.models import Q
from .models import ProductionException, Order, ProductionPlan
from .serializers import ProductionExceptionSerializer
from apps.system.utils import ResponseWrapper


class ExceptionListView(viewsets.ModelViewSet):
    """
    生产异常列表视图集
    用于获取生产异常记录，按类型和状态筛选
    """
    queryset = ProductionException.objects.filter(is_deleted=False)
    serializer_class = ProductionExceptionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # 获取查询参数
        exception_type = self.request.query_params.get('type')
        status = self.request.query_params.get('status')
        start_date = self.request.query_params.get('startDate')
        end_date = self.request.query_params.get('endDate')
        
        # 根据查询参数过滤
        if exception_type:
            queryset = queryset.filter(exception_type=exception_type)
        if status:
            queryset = queryset.filter(severity=status)  # 假设status对应severity字段
        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)
            
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


class ExceptionReportView(views.APIView):
    """
    异常报告创建视图
    用于创建异常报告，评估影响程度，通知相关人员
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            # 获取请求参数
            order_id = request.data.get('orderId')
            process_id = request.data.get('processId')  # 对应ProductionPlan的id
            exception_type = request.data.get('type')
            description = request.data.get('description')
            impact = request.data.get('impact')
            images = request.data.get('images', [])
            
            # 参数验证
            if not all([process_id, exception_type, description, impact]):
                return ResponseWrapper.error('工序ID、异常类型、描述和影响程度不能为空')
            
            # 验证生产计划是否存在
            try:
                production_plan = ProductionPlan.objects.get(id=process_id, is_deleted=False)
            except ProductionPlan.DoesNotExist:
                return ResponseWrapper.error('生产工序不存在')
            
            # 根据影响程度确定严重性
            severity_mapping = {
                'low': 'low',
                'medium': 'medium',
                'high': 'high'
            }
            severity = severity_mapping.get(impact.lower(), 'medium')
            
            # 创建异常记录
            exception = ProductionException.objects.create(
                production_plan=production_plan,
                exception_type=exception_type,
                severity=severity,
                description=description,
                reported_by=request.user
            )
            
            # 如果有图片，添加到描述中
            if images:
                exception.description += f"\n图片数量: {len(images)}"
                exception.save()
            
            # 返回成功响应
            return ResponseWrapper.success({
                'exceptionId': exception.id,
                'message': '异常报告创建成功'
            })
            
        except Exception as e:
            return ResponseWrapper.error(f'创建异常报告失败: {str(e)}')


class ExceptionHandlingView(views.APIView):
    """
    异常处理视图
    用于记录异常处理方案，更新异常状态，评估处理结果
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, id):
        try:
            # 获取请求参数
            solution = request.data.get('solution')
            handler = request.data.get('handler')
            result = request.data.get('result')
            status = request.data.get('status')
            
            # 参数验证
            if not all([solution, handler, result, status]):
                return ResponseWrapper.error('解决方案、处理人、处理结果和状态不能为空')
            
            # 验证异常记录是否存在
            try:
                exception = ProductionException.objects.get(id=id, is_deleted=False)
            except ProductionException.DoesNotExist:
                return ResponseWrapper.error('异常记录不存在')
            
            # 更新异常记录
            exception.solution = solution
            exception.resolved_at = timezone.now()
            
            # 将处理人和处理结果添加到解决方案中
            exception.solution += f"\n处理人: {handler}"
            exception.solution += f"\n处理结果: {result}"
            exception.solution += f"\n处理状态: {status}"
            
            exception.save()
            
            # 返回成功响应
            return ResponseWrapper.success({
                'exceptionId': exception.id,
                'message': '异常处理成功'
            })
            
        except Exception as e:
            return ResponseWrapper.error(f'处理异常失败: {str(e)}')