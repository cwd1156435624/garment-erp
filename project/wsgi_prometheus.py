"""WSGI配置, 用于Prometheus多进程模式

这个文件是对原始wsgi.py的扩展，添加了Prometheus多进程模式的支持
"""

import os
from django.conf import settings
from django.core.wsgi import get_wsgi_application

# 设置Prometheus多进程模式的环境变量
os.environ.setdefault('prometheus_multiproc_dir', str(settings.PROMETHEUS_METRICS['DIRECTORY']))

# 设置Django设置模块
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

# 获取WSGI应用
application = get_wsgi_application()