from rest_framework import viewsets, permissions
from rest_framework.response import Response
from django.utils import timezone
from .models_alerts import SystemAlert
from .serializers_alerts import SystemAlertSerializer

class AlertViewSet(viewsets.ModelViewSet):
    """系统告警视图集"""
    serializer_class = SystemAlertSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """获取告警列表，支持排序"""
        queryset = SystemAlert.objects.all()
        
        # 处理排序参数
        ordering = self.request.query_params.get('ordering', '-created_at')
        if ordering:
            queryset = queryset.order_by(ordering)
            
        return queryset
    
    def list(self, request, *args, **kwargs):
        """重写list方法，返回前端期望的数据格式"""
        queryset = self.filter_queryset(self.get_queryset())
        
        # 处理分页
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'results': serializer.data,
            'count': len(serializer.data)
        })