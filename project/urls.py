"""
URL configuration for project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import RedirectView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

# API文档配置
schema_view = get_schema_view(
    openapi.Info(
        title="ERP API",
        default_version='v1',
        description="ERP系统 API文档",
    ),
    url="https://yagtpotihswf.sealosbja.site/api",  # 与前端保持一致的API基础URL
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('', RedirectView.as_view(url='/swagger/')),
    path('admin/', admin.site.urls),
    # JWT认证接口
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # API文档
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    # 别名路由 - 系统公告
    path('api/notices/', include('apps.system.urls_notices_alias')),
    # 版本化路径 - 系统公告
    path('api/v1/notices/', include('apps.system.urls_notices_alias')),
    # 别名路由 - 订单
    path('api/orders/', include('apps.production.urls_orders_alias')),
    # 系统告警API
    path('api/alerts/', include('apps.system.urls_alerts')),
    # API版本控制
    path('api/v1/', include(('api.v1.urls', 'api'), namespace='v1')),
    
    # 保留当前API路由以保持向后兼容性
    # 这些路由将在未来版本中逐步迁移到版本化API
    path('api/users/', include('apps.users.urls')),  # 用户认证相关接口
    path('api/equipment/', include('apps.equipment.urls')),
    path('api/system/', include('apps.system.urls')),
    path('api/production/', include('apps.production.urls')),
    path('api/developer/', include('developer.urls')),
    path('api/inventory/', include('apps.inventory.urls')),
    path('api/supplier/', include('apps.supplier.urls')),
    path('api/warehouse/', include('apps.warehouse.urls')),
    path('api/settlement/', include('apps.settlement.urls')),
    path('api/scanning/', include('apps.scanning.urls')),
    path('api/reports/', include('apps.reports.urls')),
    path('api/materials/', include('apps.materials.urls')),
    path('api/search/', include('apps.search.urls')),
    path('api/design/', include('apps.design.urls')),
    # 直接映射design-files路径到design/files，与前端路径保持一致
    # 使用re_path确保无论有没有斜杠的URL都能正确匹配
    re_path(r'^api/design-files/?', include('apps.design.urls_files_alias')),
    # 通知API - 非版本化路径（与前端兼容）
    path('api/notifications/', include('apps.notification.urls_alias')),
    # 通知API - 原始路径（与版本化API保持一致）
    path('api/v1/notifications/', include('apps.notification.urls')),
    # 客户API
    path('api/customer/', include('apps.customer.urls')),
    # 财务API
    path('api/finance/', include('apps.finance.urls')),
    # 员工API
    path('api/employee/', include('apps.employee.urls')),
    # 物料清单API
    path('api/bom/', include('apps.bom.urls')),
]
