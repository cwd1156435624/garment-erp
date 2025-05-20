from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    if response is not None:
        # 统一响应格式
        error_data = {
            'code': response.status_code,
            'message': str(exc),
            'data': response.data
        }
        response.data = error_data

    return response

def api_response(data=None, message='Success', code=status.HTTP_200_OK):
    """统一的API响应格式
    
    Args:
        data: 响应数据
        message: 提示信息
        code: 状态码
    """
    return Response({
        'code': code,
        'message': message,
        'data': data
    })

class ResponseWrapper:
    """统一的响应处理类
    
    用法示例:
    @api_view(['GET'])
    def my_view(request):
        try:
            data = get_data()
            return ResponseWrapper.success(data)
        except Exception as e:
            return ResponseWrapper.error(str(e))
    """
    
    @staticmethod
    def success(data=None, message='success'):
        """成功响应
        
        Args:
            data: 响应数据
            message: 成功提示信息
        """
        return Response({
            'code': status.HTTP_200_OK,
            'message': message,
            'data': data
        })
    
    @staticmethod
    def error(message, code=status.HTTP_400_BAD_REQUEST, data=None):
        """错误响应
        
        Args:
            message: 错误信息
            code: HTTP状态码
            data: 错误详细信息
        """
        return Response({
            'code': code,
            'message': message,
            'data': data
        }, status=code)

class ResponseWrapper:
    @staticmethod
    def success(data=None, message='success'):
        return Response({
            'code': status.HTTP_200_OK,
            'message': message,
            'data': data
        })
    
    @staticmethod
    def error(message, code=status.HTTP_400_BAD_REQUEST, data=None):
        return Response({
            'code': code,
            'message': message,
            'data': data
        }, status=code)