from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import UserViewSet

router = DefaultRouter()
router.register('', UserViewSet)

urlpatterns = [
    # 用户相关的路由会自动生成：
    # POST /api/users/login/ - 用户登录
    # POST /api/users/register/ - 用户注册
    # GET /api/users/profile/ - 获取用户信息
    # POST /api/users/change_password/ - 修改密码
    
    # 添加别名路由，将/users/me/映射到profile端点
    path('me/', UserViewSet.as_view({'get': 'profile'})),
] + router.urls