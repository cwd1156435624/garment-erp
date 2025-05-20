from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.decorators import action
from .views_notice import NoticeViewSet
from .serializers_notice import NoticeSerializer

class NotificationsViewSet(NoticeViewSet):
    """系统公告别名视图集，返回前端期望的数据格式"""
    
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
        
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """获取未读通知数量"""
        unread_count = self.get_unread_count(request.user)
        return Response({'count': unread_count})

router = DefaultRouter()

# 创建一个视图集，但使用不同的基础名称
router.register('api/notifications', NotificationsViewSet, basename='notifications')

urlpatterns = router.urls
