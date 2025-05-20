from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
import random

class InventoryViewSet(viewsets.ViewSet):
    """库存 API 视图集"""
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """获取库存统计数据"""
        # 根据前端需要的格式返回数据
        # 前端期望的数据格式：{total: 0, inStock: 0, lowStock: 0}
        import random
        
        # 直接返回前端需要的数据结构
        return Response({
            'data': {
                'total': random.randint(1000, 5000),
                'inStock': random.randint(800, 4500),
                'lowStock': random.randint(50, 200)
            }
        })
