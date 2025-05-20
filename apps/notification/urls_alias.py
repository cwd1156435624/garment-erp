from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NotificationViewSet

# 这个别名路由配置将被包含在主urls.py中，路径为/api/notifications/
# 它提供与版本化API相同的功能，但使用非版本化的路径
urlpatterns = [
    # 添加特殊端点的配置
    # 获取未读通知数量
    path('unread-count/', NotificationViewSet.as_view({'get': 'unread_count'}), name='notification-unread-count'),
    # 标记所有通知为已读
    path('read-all/', NotificationViewSet.as_view({'post': 'read_all'}), name='notification-read-all'),
    # 标记单个通知为已读
    path('<int:pk>/read/', NotificationViewSet.as_view({'post': 'read'}), name='notification-read'),
]

# 创建一个路由器，注册通知视图集
# 注意：路由器必须在特殊端点之后注册，以避免路由冲突
router = DefaultRouter()
router.register('', NotificationViewSet, basename='notification')

# 添加路由器生成的路由
urlpatterns += [
    path('', include(router.urls)),
]
