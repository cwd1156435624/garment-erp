from django.db import models
from simple_history.models import HistoricalRecords
from apps.users.models import User

class Order(models.Model):
    """
    订单模型
    用于存储订单相关信息
    """
    STATUS_CHOICES = [
        ('pending', '待处理'),
        ('processing', '生产中'),
        ('completed', '已完成'),
        ('cancelled', '已取消'),
    ]
    
    order_number = models.CharField('订单编号', max_length=50, unique=True)
    customer = models.ForeignKey('customer.Customer', on_delete=models.PROTECT, verbose_name='客户')
    product_name = models.CharField('产品名称', max_length=100)
    quantity = models.IntegerField('数量')
    unit_price = models.DecimalField('单价', max_digits=10, decimal_places=2)
    total_amount = models.DecimalField('总金额', max_digits=12, decimal_places=2)
    delivery_date = models.DateField('交付日期')
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    remarks = models.TextField('备注', null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='创建人')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    is_deleted = models.BooleanField('是否删除', default=False)
    history = HistoricalRecords()
    
    class Meta:
        verbose_name = '订单'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        db_table = 'prod_order'
    
    def __str__(self):
        return self.order_number

class ProductionPlan(models.Model):
    """
    生产计划模型
    用于管理生产计划和进度
    """
    STATUS_CHOICES = [
        ('planned', '已计划'),
        ('in_progress', '进行中'),
        ('completed', '已完成'),
        ('delayed', '已延期'),
    ]
    
    order = models.ForeignKey(Order, on_delete=models.PROTECT, verbose_name='关联订单')
    plan_number = models.CharField('计划编号', max_length=50, unique=True)
    start_date = models.DateField('开始日期')
    end_date = models.DateField('结束日期')
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='planned')
    actual_start_date = models.DateField('实际开始日期', null=True, blank=True)
    actual_end_date = models.DateField('实际结束日期', null=True, blank=True)
    progress = models.FloatField('进度', default=0)
    responsible_person = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='负责人')
    remarks = models.TextField('备注', null=True, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    is_deleted = models.BooleanField('是否删除', default=False)
    history = HistoricalRecords()
    
    class Meta:
        verbose_name = '生产计划'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        db_table = 'prod_production_plan'
    
    def __str__(self):
        return self.plan_number

class CuttingTask(models.Model):
    """
    裁剪任务模型
    用于管理裁剪环节的任务分配和进度
    """
    STATUS_CHOICES = [
        ('pending', '待处理'),
        ('processing', '进行中'),
        ('completed', '已完成'),
    ]
    
    production_plan = models.ForeignKey(ProductionPlan, on_delete=models.PROTECT, verbose_name='生产计划')
    task_number = models.CharField('任务编号', max_length=50, unique=True)
    material = models.CharField('材料', max_length=100)
    quantity = models.IntegerField('数量')
    assigned_to = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='分配给')
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    start_time = models.DateTimeField('开始时间', null=True, blank=True)
    end_time = models.DateTimeField('结束时间', null=True, blank=True)
    remarks = models.TextField('备注', null=True, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    is_deleted = models.BooleanField('是否删除', default=False)
    history = HistoricalRecords()
    
    class Meta:
        verbose_name = '裁剪任务'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        db_table = 'prod_cutting_task'
    
    def __str__(self):
        return self.task_number

class ProductionException(models.Model):
    """
    生产异常记录模型
    用于记录生产过程中的异常情况
    """
    SEVERITY_CHOICES = [
        ('low', '轻微'),
        ('medium', '中等'),
        ('high', '严重'),
    ]
    
    production_plan = models.ForeignKey(ProductionPlan, on_delete=models.PROTECT, verbose_name='生产计划')
    exception_type = models.CharField('异常类型', max_length=50)
    severity = models.CharField('严重程度', max_length=20, choices=SEVERITY_CHOICES)
    description = models.TextField('异常描述')
    solution = models.TextField('解决方案', null=True, blank=True)
    reported_by = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='报告人')
    resolved_at = models.DateTimeField('解决时间', null=True, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    is_deleted = models.BooleanField('是否删除', default=False)
    history = HistoricalRecords()
    
    class Meta:
        verbose_name = '生产异常'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        db_table = 'prod_exception'
    
    def __str__(self):
        return f'{self.production_plan} - {self.exception_type}'

class Batch(models.Model):
    """
    批次管理模型
    用于管理生产批次信息
    """
    STATUS_CHOICES = [
        ('created', '已创建'),
        ('in_production', '生产中'),
        ('completed', '已完成'),
        ('quality_check', '质检中'),
    ]
    
    production_plan = models.ForeignKey(ProductionPlan, on_delete=models.PROTECT, verbose_name='生产计划')
    batch_number = models.CharField('批次编号', max_length=50, unique=True)
    quantity = models.IntegerField('数量')
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='created')
    start_date = models.DateField('开始日期')
    end_date = models.DateField('结束日期')
    quality_check_result = models.TextField('质检结果', null=True, blank=True)
    remarks = models.TextField('备注', null=True, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    is_deleted = models.BooleanField('是否删除', default=False)
    history = HistoricalRecords()
    
    class Meta:
        verbose_name = '生产批次'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        db_table = 'prod_batch'
    
    def __str__(self):
        return self.batch_number