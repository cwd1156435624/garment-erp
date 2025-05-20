from django.db import models
from apps.users.models import User
from apps.production.models import Order, ProductionPlan, Batch
from apps.warehouse.models import Warehouse, FinishedGoods

class ReportTemplate(models.Model):
    """
    报表模板模型
    用于存储预定义的报表模板
    """
    REPORT_TYPE_CHOICES = [
        ('production', '生产报表'),
        ('inventory', '库存报表'),
        ('cost', '成本报表'),
        ('custom', '自定义报表'),
    ]
    
    name = models.CharField('模板名称', max_length=100)
    report_type = models.CharField('报表类型', max_length=20, choices=REPORT_TYPE_CHOICES)
    description = models.TextField('描述', blank=True, null=True)
    config = models.JSONField('配置', default=dict)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='创建人')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    is_deleted = models.BooleanField('是否删除', default=False)
    
    class Meta:
        verbose_name = '报表模板'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        db_table = 'report_template'
    
    def __str__(self):
        return self.name

class SavedReport(models.Model):
    """
    保存的报表模型
    用于存储用户生成并保存的报表
    """
    STATUS_CHOICES = [
        ('generating', '生成中'),
        ('completed', '已完成'),
        ('failed', '失败'),
    ]
    
    name = models.CharField('报表名称', max_length=100)
    template = models.ForeignKey(ReportTemplate, on_delete=models.PROTECT, verbose_name='报表模板', null=True, blank=True)
    parameters = models.JSONField('参数', default=dict)
    result_data = models.JSONField('结果数据', default=dict)
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='generating')
    error_message = models.TextField('错误信息', blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='创建人')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    completed_at = models.DateTimeField('完成时间', null=True, blank=True)
    is_deleted = models.BooleanField('是否删除', default=False)
    
    class Meta:
        verbose_name = '保存的报表'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        db_table = 'saved_report'
    
    def __str__(self):
        return self.name