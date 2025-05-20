from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class WebSocketConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.websocket'
    verbose_name = _('WebSocket服务')
    
    def ready(self):
        """应用就绪时执行的操作"""
        # 导入信号处理器
        from . import signals
        pass
