from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q
from apps.system.utils import ResponseWrapper
from apps.customer.models import Customer
from apps.supplier.models import Supplier
from apps.production.models import Order, ProductionPlan
from apps.materials.models import Inventory
from apps.materials.models import Material

class SearchView(APIView):
    """
    全局搜索视图
    提供跨模块数据搜索功能
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        keyword = request.query_params.get('keyword', '')
        types = request.query_params.get('types', '').split(',') if request.query_params.get('types') else []
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('pageSize', 10))
        
        if not keyword:
            return ResponseWrapper.error('搜索关键词不能为空')
        
        results = []
        facets = {}
        total = 0
        
        # 搜索客户
        if not types or 'customer' in types:
            customers = Customer.objects.filter(
                Q(name__icontains=keyword) | 
                Q(contact_person__icontains=keyword) | 
                Q(phone__icontains=keyword)
            )
            customer_count = customers.count()
            if customer_count > 0:
                facets['customer'] = customer_count
                total += customer_count
                if not types or 'customer' in types:
                    for customer in customers[(page-1)*page_size:page*page_size]:
                        results.append({
                            'id': customer.id,
                            'type': 'customer',
                            'title': customer.name,
                            'description': f'联系人: {customer.contact_person}, 电话: {customer.phone}',
                            'url': f'/customer/detail/{customer.id}'
                        })
        
        # 搜索供应商
        if not types or 'supplier' in types:
            suppliers = Supplier.objects.filter(
                Q(name__icontains=keyword) | 
                Q(contact_person__icontains=keyword) | 
                Q(phone__icontains=keyword)
            )
            supplier_count = suppliers.count()
            if supplier_count > 0:
                facets['supplier'] = supplier_count
                total += supplier_count
                if not types or 'supplier' in types:
                    for supplier in suppliers[(page-1)*page_size:page*page_size]:
                        results.append({
                            'id': supplier.id,
                            'type': 'supplier',
                            'title': supplier.name,
                            'description': f'联系人: {supplier.contact_person}, 电话: {supplier.phone}',
                            'url': f'/supplier/detail/{supplier.id}'
                        })
        
        # 搜索订单
        if not types or 'order' in types:
            orders = Order.objects.filter(
                Q(order_number__icontains=keyword) | 
                Q(product_name__icontains=keyword)
            )
            order_count = orders.count()
            if order_count > 0:
                facets['order'] = order_count
                total += order_count
                if not types or 'order' in types:
                    for order in orders[(page-1)*page_size:page*page_size]:
                        results.append({
                            'id': order.id,
                            'type': 'order',
                            'title': f'订单 {order.order_number}',
                            'description': f'产品: {order.product_name}, 数量: {order.quantity}',
                            'url': f'/production/order/detail/{order.id}'
                        })
        
        # 搜索库存
        if not types or 'inventory' in types:
            inventories = Inventory.objects.filter(
                Q(item_name__icontains=keyword) | 
                Q(item_code__icontains=keyword)
            )
            inventory_count = inventories.count()
            if inventory_count > 0:
                facets['inventory'] = inventory_count
                total += inventory_count
                if not types or 'inventory' in types:
                    for inventory in inventories[(page-1)*page_size:page*page_size]:
                        results.append({
                            'id': inventory.id,
                            'type': 'inventory',
                            'title': inventory.item_name,
                            'description': f'编码: {inventory.item_code}, 数量: {inventory.quantity}',
                            'url': f'/warehouse/inventory/detail/{inventory.id}'
                        })
        
        # 搜索物料
        if not types or 'material' in types:
            materials = Material.objects.filter(
                Q(name__icontains=keyword) | 
                Q(code__icontains=keyword)
            )
            material_count = materials.count()
            if material_count > 0:
                facets['material'] = material_count
                total += material_count
                if not types or 'material' in types:
                    for material in materials[(page-1)*page_size:page*page_size]:
                        results.append({
                            'id': material.id,
                            'type': 'material',
                            'title': material.name,
                            'description': f'编码: {material.code}',
                            'url': f'/materials/detail/{material.id}'
                        })
        
        return ResponseWrapper.success({
            'items': results,
            'total': total,
            'facets': facets
        })

class SearchSuggestionView(APIView):
    """
    搜索建议视图
    提供搜索建议功能
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        keyword = request.query_params.get('keyword', '')
        limit = int(request.query_params.get('limit', 5))
        
        if not keyword or len(keyword) < 2:
            return ResponseWrapper.success({'suggestions': []})
        
        suggestions = set()
        
        # 从客户名称中获取建议
        customers = Customer.objects.filter(name__icontains=keyword)[:limit]
        for customer in customers:
            suggestions.add(customer.name)
        
        # 从供应商名称中获取建议
        suppliers = Supplier.objects.filter(name__icontains=keyword)[:limit]
        for supplier in suppliers:
            suggestions.add(supplier.name)
        
        # 从订单产品名称中获取建议
        orders = Order.objects.filter(product_name__icontains=keyword)[:limit]
        for order in orders:
            suggestions.add(order.product_name)
        
        # 从库存物品名称中获取建议
        inventories = Inventory.objects.filter(item_name__icontains=keyword)[:limit]
        for inventory in inventories:
            suggestions.add(inventory.item_name)
        
        # 从物料名称中获取建议
        materials = Material.objects.filter(name__icontains=keyword)[:limit]
        for material in materials:
            suggestions.add(material.name)
        
        return ResponseWrapper.success({
            'suggestions': list(suggestions)[:limit]
        })

class AdvancedSearchView(APIView):
    """
    高级搜索视图
    提供复杂的搜索条件组合功能
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        filters = request.data.get('filters', {})
        sort = request.data.get('sort', '-created_at')
        page = int(request.data.get('page', 1))
        page_size = int(request.data.get('pageSize', 10))
        
        if not filters:
            return ResponseWrapper.error('搜索条件不能为空')
        
        # 获取搜索类型
        search_type = filters.get('type')
        if not search_type:
            return ResponseWrapper.error('搜索类型不能为空')
        
        results = []
        total = 0
        
        # 根据不同类型执行不同的搜索逻辑
        if search_type == 'customer':
            # 客户高级搜索
            query = Q()
            if 'name' in filters:
                query &= Q(name__icontains=filters['name'])
            if 'contact_person' in filters:
                query &= Q(contact_person__icontains=filters['contact_person'])
            if 'phone' in filters:
                query &= Q(phone__icontains=filters['phone'])
            if 'status' in filters:
                query &= Q(status=filters['status'])
            
            customers = Customer.objects.filter(query, is_deleted=False)
            total = customers.count()
            customers = customers.order_by(sort)[(page-1)*page_size:page*page_size]
            
            for customer in customers:
                results.append({
                    'id': customer.id,
                    'type': 'customer',
                    'title': customer.name,
                    'description': f'联系人: {customer.contact_person}, 电话: {customer.phone}',
                    'url': f'/customer/detail/{customer.id}'
                })
        
        elif search_type == 'supplier':
            # 供应商高级搜索
            query = Q()
            if 'name' in filters:
                query &= Q(name__icontains=filters['name'])
            if 'contact_person' in filters:
                query &= Q(contact_person__icontains=filters['contact_person'])
            if 'phone' in filters:
                query &= Q(phone__icontains=filters['phone'])
            if 'status' in filters:
                query &= Q(status=filters['status'])
            
            suppliers = Supplier.objects.filter(query, is_deleted=False)
            total = suppliers.count()
            suppliers = suppliers.order_by(sort)[(page-1)*page_size:page*page_size]
            
            for supplier in suppliers:
                results.append({
                    'id': supplier.id,
                    'type': 'supplier',
                    'title': supplier.name,
                    'description': f'联系人: {supplier.contact_person}, 电话: {supplier.phone}',
                    'url': f'/supplier/detail/{supplier.id}'
                })
        
        elif search_type == 'material':
            # 物料高级搜索
            query = Q()
            if 'name' in filters:
                query &= Q(name__icontains=filters['name'])
            if 'code' in filters:
                query &= Q(code__icontains=filters['code'])
            if 'category' in filters:
                query &= Q(category=filters['category'])
            if 'status' in filters:
                query &= Q(status=filters['status'])
            
            materials = Material.objects.filter(query, is_deleted=False)
            total = materials.count()
            materials = materials.order_by(sort)[(page-1)*page_size:page*page_size]
            
            for material in materials:
                results.append({
                    'id': material.id,
                    'type': 'material',
                    'title': material.name,
                    'description': f'编码: {material.code}',
                    'url': f'/materials/detail/{material.id}'
                })
        
        elif search_type == 'order':
            # 订单高级搜索
            query = Q()
            if 'order_number' in filters:
                query &= Q(order_number__icontains=filters['order_number'])
            if 'product_name' in filters:
                query &= Q(product_name__icontains=filters['product_name'])
            if 'status' in filters:
                query &= Q(status=filters['status'])
            if 'date_range' in filters:
                date_range = filters['date_range']
                if date_range.get('start'):
                    query &= Q(created_at__gte=date_range['start'])
                if date_range.get('end'):
                    query &= Q(created_at__lte=date_range['end'])
            
            orders = Order.objects.filter(query, is_deleted=False)
            total = orders.count()
            orders = orders.order_by(sort)[(page-1)*page_size:page*page_size]
            
            for order in orders:
                results.append({
                    'id': order.id,
                    'type': 'order',
                    'title': f'订单 {order.order_number}',
                    'description': f'产品: {order.product_name}, 数量: {order.quantity}',
                    'url': f'/production/order/detail/{order.id}'
                })
        
        elif search_type == 'inventory':
            # 库存高级搜索
            query = Q()
            if 'item_name' in filters:
                query &= Q(item_name__icontains=filters['item_name'])
            if 'item_code' in filters:
                query &= Q(item_code__icontains=filters['item_code'])
            if 'location' in filters:
                query &= Q(location=filters['location'])
            if 'quantity_range' in filters:
                quantity_range = filters['quantity_range']
                if quantity_range.get('min') is not None:
                    query &= Q(quantity__gte=quantity_range['min'])
                if quantity_range.get('max') is not None:
                    query &= Q(quantity__lte=quantity_range['max'])
            
            inventories = Inventory.objects.filter(query, is_deleted=False)
            total = inventories.count()
            inventories = inventories.order_by(sort)[(page-1)*page_size:page*page_size]
            
            for inventory in inventories:
                results.append({
                    'id': inventory.id,
                    'type': 'inventory',
                    'title': inventory.item_name,
                    'description': f'编码: {inventory.item_code}, 数量: {inventory.quantity}',
                    'url': f'/warehouse/inventory/detail/{inventory.id}'
                })
        
        return ResponseWrapper.success({
            'items': results,
            'total': total
        })