from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
import random

class OrderViewSet(viewsets.ViewSet):
    """订单 API 视图集"""
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        """获取订单列表"""
        # 返回空列表，模拟没有订单数据
        return Response([])
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """获取订单统计数据"""
        # 返回模拟的订单统计数据
        current_date = timezone.now().date()
        
        # 模拟数据
        data = {
            'total_orders': random.randint(100, 500),
            'pending_orders': random.randint(10, 50),
            'completed_orders': random.randint(50, 200),
            'cancelled_orders': random.randint(5, 20),
            'total_amount': round(random.uniform(10000, 100000), 2),
            'average_amount': round(random.uniform(1000, 5000), 2),
            'monthly_stats': [
                {
                    'month': (current_date.replace(day=1) - timezone.timedelta(days=i*30)).strftime('%Y-%m'),
                    'orders': random.randint(20, 100),
                    'amount': round(random.uniform(5000, 20000), 2)
                }
                for i in range(6)
            ],
            'status_distribution': {
                'pending': random.randint(10, 30),
                'processing': random.randint(20, 40),
                'shipping': random.randint(5, 15),
                'completed': random.randint(30, 60),
                'cancelled': random.randint(5, 15)
            }
        }
        
        return Response(data)
