"""
API版本控制中间件
用于在响应中添加版本信息，并支持弃用通知
"""

from django.utils.deprecation import MiddlewareMixin
import re

class APIVersionHeaderMiddleware(MiddlewareMixin):
    """
    在API响应中添加版本信息的中间件
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # 编译正则表达式以匹配API URL
        self.api_pattern = re.compile(r'^/api/(?:v(\d+))?/')
        # 存储API版本信息
        self.api_versions = {
            '1': {
                'status': 'active',
                'deprecated': False,
                'sunset_date': None
            },
            # 未来可以添加更多版本
        }
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # 检查是否是API请求
        path = request.path_info
        match = self.api_pattern.match(path)
        
        if match:
            # 确定API版本
            version = match.group(1) if match.group(1) else '1'  # 默认为v1
            
            # 添加API版本响应头
            response['X-API-Version'] = f'v{version}'
            
            # 如果版本已弃用，添加弃用通知
            if version in self.api_versions and self.api_versions[version]['deprecated']:
                response['Deprecation'] = 'true'
                
                # 如果有日落日期，添加日落日期
                if self.api_versions[version]['sunset_date']:
                    response['Sunset'] = self.api_versions[version]['sunset_date']
                
                # 添加替代版本信息
                latest_version = max(self.api_versions.keys(), key=int)
                if latest_version != version:
                    response['X-API-Suggested-Version'] = f'v{latest_version}'
        
        return response
