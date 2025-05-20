from django.db import models
from simple_history.models import HistoricalRecords
from apps.users.models import User

class BaseModel(models.Model):
    """
    基础模型类
    包含所有模型共用的字段
    """
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='创建人')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    is_deleted = models.BooleanField('是否删除', default=False)
    history = HistoricalRecords()

    class Meta:
        abstract = True

class SystemParameter(models.Model):
    """
    系统参数模型
    用于存储系统的各项配置参数
    """
    PARAM_TYPE_CHOICES = [
        ('string', '字符串'),
        ('number', '数值'),
        ('boolean', '布尔值'),
        ('json', 'JSON'),
    ]
    
    param_key = models.CharField('参数键', max_length=100, unique=True)
    param_value = models.TextField('参数值')
    param_type = models.CharField('参数类型', max_length=20, choices=PARAM_TYPE_CHOICES)
    description = models.CharField('参数描述', max_length=200)
    is_system = models.BooleanField('是否系统参数', default=False)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='创建人')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    is_deleted = models.BooleanField('是否删除', default=False)
    history = HistoricalRecords()
    
    class Meta:
        verbose_name = '系统参数'
        verbose_name_plural = verbose_name
        ordering = ['param_key']
        db_table = 'sys_parameter'
    
    def __str__(self):
        return f'{self.param_key} - {self.description}'

class OperationLog(models.Model):
    """
    操作日志模型
    用于记录用户的操作行为
    """
    OPERATION_TYPE_CHOICES = [
        ('create', '创建'),
        ('update', '更新'),
        ('delete', '删除'),
        ('query', '查询'),
        ('export', '导出'),
        ('import', '导入'),
        ('login', '登录'),
        ('logout', '登出'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='操作人')
    operation_type = models.CharField('操作类型', max_length=20, choices=OPERATION_TYPE_CHOICES)
    operation_module = models.CharField('操作模块', max_length=50)
    operation_desc = models.CharField('操作描述', max_length=200)
    operation_detail = models.TextField('操作详情', null=True, blank=True)
    ip_address = models.GenericIPAddressField('IP地址', null=True, blank=True)
    user_agent = models.CharField('User Agent', max_length=500, null=True, blank=True)
    created_at = models.DateTimeField('操作时间', auto_now_add=True)
    
    class Meta:
        verbose_name = '操作日志'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        db_table = 'sys_operation_log'
    
    def __str__(self):
        return f'{self.user.username} - {self.operation_type} - {self.operation_module}'