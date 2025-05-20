"""
API v1版本的URL配置
此文件定义了API v1版本的所有URL路由
"""

from django.urls import path, include

urlpatterns = [
    # 用户API
    path('users/', include('apps.users.urls')),
    
    # 通知API
    path('notifications/', include('apps.notification.urls')),
    
    # 系统API
    path('system/', include('apps.system.urls')),
    
    # 生产API
    path('production/', include('apps.production.urls')),
    
    # 订单API别名
    path('orders/', include('apps.production.urls_orders_alias')),
    
    # 系统告警API别名
    path('alerts/', include('apps.system.urls_alerts')),
    
    # 设备API
    path('equipment/', include('apps.equipment.urls')),
    
    # 库存API
    path('inventory/', include('apps.inventory.urls')),
    
    # 供应商API
    path('supplier/', include('apps.supplier.urls')),
    
    # 仓库API
    path('warehouse/', include('apps.warehouse.urls')),
    
    # 结算API
    path('settlement/', include('apps.settlement.urls')),
    
    # 扫描API
    path('scanning/', include('apps.scanning.urls')),
    
    # 报表API
    path('reports/', include('apps.reports.urls')),
    
    # 物料API
    path('materials/', include('apps.materials.urls')),
    
    # 搜索API
    path('search/', include('apps.search.urls')),
    
    # 设计API
    path('design/', include('apps.design.urls')),
    
    # 设计文件API别名
    path('design-files/', include('apps.design.urls_files_alias')),
    
    # 客户API
    path('customer/', include('apps.customer.urls')),
    
    # 财务API
    path('finance/', include('apps.finance.urls')),
    
    # 员工API
    path('employee/', include('apps.employee.urls')),
    
    # 物料清单API
    path('bom/', include('apps.bom.urls')),
]
