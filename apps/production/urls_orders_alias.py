from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.response import Response
from .views import OrderViewSet

class OrdersAliasViewSet(OrderViewSet):
    """订单别名视图集，返回前端期望的数据格式"""
    
    def list(self, request, *args, **kwargs):
        """重写list方法，返回前端期望的数据格式"""
        queryset = self.filter_queryset(self.get_queryset())
        
        # 不使用分页，直接返回所有数据
        serializer = self.get_serializer(queryset, many=True)
        
        # 返回前端期望的格式，确保数据在最外层
        return Response({
            'results': serializer.data,
            'count': len(serializer.data)
        })

router = DefaultRouter()
router.register('', OrdersAliasViewSet, basename='orders')

urlpatterns = router.urls
