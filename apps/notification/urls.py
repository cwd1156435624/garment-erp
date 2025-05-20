from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NotificationViewSet

# 首先定义特殊端点
urlpatterns = [
    # 获取未读通知数量
    path('unread-count/', NotificationViewSet.as_view({'get': 'unread_count'}), name='notification-unread-count'),
    # 标记所有通知为已读
    path('read-all/', NotificationViewSet.as_view({'post': 'read_all'}), name='notification-read-all'),
    # 标记单个通知为已读
    path('<int:pk>/read/', NotificationViewSet.as_view({'post': 'read'}), name='notification-read'),
]

# 然后添加路由器生成的路由
router = DefaultRouter()
router.register('', NotificationViewSet, basename='notification')

urlpatterns += [
    path('', include(router.urls)),
]
