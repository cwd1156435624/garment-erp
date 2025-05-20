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
        # 返回模拟的库存统计数据
        data = {
            'total_items': random.randint(1000, 5000),
            'low_stock_items': random.randint(50, 200),
            'out_of_stock_items': random.randint(10, 50),
            'total_value': round(random.uniform(100000, 500000), 2),
            'category_distribution': {
                'raw_materials': random.randint(300, 1000),
                'work_in_progress': random.randint(200, 800),
                'finished_goods': random.randint(500, 2000),
                'packaging': random.randint(100, 500),
                'spare_parts': random.randint(50, 300)
            },
            'location_distribution': {
                'warehouse_a': random.randint(300, 1000),
                'warehouse_b': random.randint(200, 800),
                'production_floor': random.randint(100, 500),
                'shipping_area': random.randint(50, 300)
            },
            'recent_movements': [
                {
                    'date': f"2025-04-{i:02d}",
                    'inbound': random.randint(50, 200),
                    'outbound': random.randint(40, 180)
                }
                for i in range(1, 6)
            ]
        }
        
        return Response(data)
