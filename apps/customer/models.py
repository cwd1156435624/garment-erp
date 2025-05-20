from django.db import models
from simple_history.models import HistoricalRecords
from apps.users.models import User

class Customer(models.Model):
    """
    客户模型
    用于存储客户基本信息
    """
    LEVEL_CHOICES = [
        ('vip', 'VIP客户'),
        ('regular', '普通客户'),
        ('potential', '潜在客户'),
    ]
    
    name = models.CharField('客户名称', max_length=100)
    contact_person = models.CharField('联系人', max_length=50)
    contact_phone = models.CharField('联系电话', max_length=20)
    email = models.EmailField('电子邮箱', null=True, blank=True)
    address = models.CharField('地址', max_length=200)
    level = models.CharField('客户等级', max_length=20, choices=LEVEL_CHOICES, default='regular')
    credit_limit = models.DecimalField('信用额度', max_digits=12, decimal_places=2, default=0)
    account_receivable = models.DecimalField('应收账款', max_digits=12, decimal_places=2, default=0)
    remarks = models.TextField('备注', null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='创建人')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    is_deleted = models.BooleanField('是否删除', default=False)
    history = HistoricalRecords()
    
    class Meta:
        verbose_name = '客户'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        db_table = 'crm_customer'
    
    def __str__(self):
        return self.name

class TaskReminder(models.Model):
    """
    任务提醒模型
    用于管理客户相关的任务提醒
    """
    PRIORITY_CHOICES = [
        ('high', '高'),
        ('medium', '中'),
        ('low', '低'),
    ]
    
    STATUS_CHOICES = [
        ('pending', '待处理'),
        ('processing', '处理中'),
        ('completed', '已完成'),
        ('cancelled', '已取消'),
    ]
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name='客户')
    title = models.CharField('标题', max_length=100)
    content = models.TextField('内容')
    priority = models.CharField('优先级', max_length=20, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    due_date = models.DateTimeField('截止时间')
    assigned_to = models.ForeignKey(User, on_delete=models.PROTECT, related_name='assigned_tasks', verbose_name='负责人')
    completed_at = models.DateTimeField('完成时间', null=True, blank=True)
    completed_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='completed_tasks', null=True, blank=True, verbose_name='完成人')
    remarks = models.TextField('备注', null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='created_tasks', verbose_name='创建人')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    is_deleted = models.BooleanField('是否删除', default=False)
    history = HistoricalRecords()
    
    class Meta:
        verbose_name = '任务提醒'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        db_table = 'crm_task_reminder'
    
    def __str__(self):
        return self.title