from django.urls import path, re_path
from .views import DesignFileViewSet

# 设计稿文件别名路由，与前端请求路径保持一致
urlpatterns = [
    # 创建设计稿 - 支持有无斜杠两种形式
    path('', DesignFileViewSet.as_view({'get': 'list', 'post': 'create'})),
    # 设计稿详情
    path('<int:pk>/', DesignFileViewSet.as_view({
        'get': 'retrieve', 
        'put': 'update', 
        'patch': 'partial_update', 
        'delete': 'destroy'
    })),
    # 设计稿上传 - 支持有无斜杠两种形式
    re_path(r'^upload/?$', DesignFileViewSet.as_view({'post': 'upload_file'})),
    # 设计稿审批
    path('<int:pk>/approve/', DesignFileViewSet.as_view({'post': 'approve'})),
    # 设计稿拒绝
    path('<int:pk>/reject/', DesignFileViewSet.as_view({'post': 'reject'})),
    # 设计稿发布
    path('<int:pk>/publish/', DesignFileViewSet.as_view({'post': 'publish'})),
]
