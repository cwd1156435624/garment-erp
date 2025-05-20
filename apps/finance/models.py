from django.db import models
from simple_history.models import HistoricalRecords
from apps.users.models import User
from apps.production.models import Order, ProductionPlan

class FactorySettlement(models.Model):
    """
    工厂结算单模型
    用于管理工厂生产的结算记录
    """
    STATUS_CHOICES = [
        ('pending', '待审核'),
        ('approved', '已审核'),
        ('paid', '已付款'),
        ('cancelled', '已取消'),
    ]
    
    settlement_number = models.CharField('结算单号', max_length=50, unique=True)
    production_plan = models.ForeignKey(ProductionPlan, on_delete=models.PROTECT, verbose_name='生产计划')
    settlement_amount = models.DecimalField('结算金额', max_digits=12, decimal_places=2)
    settlement_date = models.DateField('结算日期')
    payment_date = models.DateField('付款日期', null=True, blank=True)
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    approved_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='approved_factory_settlements', null=True, blank=True, verbose_name='审核人')
    approved_at = models.DateTimeField('审核时间', null=True, blank=True)
    remarks = models.TextField('备注', null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='created_factory_settlements', verbose_name='创建人')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    is_deleted = models.BooleanField('是否删除', default=False)
    history = HistoricalRecords()
    
    class Meta:
        verbose_name = '工厂结算单'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        db_table = 'fin_factory_settlement'
    
    def __str__(self):
        return self.settlement_number

class OutsourceSettlement(models.Model):
    """
    外发结算单模型
    用于管理外发加工的结算记录
    """
    STATUS_CHOICES = [
        ('pending', '待审核'),
        ('approved', '已审核'),
        ('paid', '已付款'),
        ('cancelled', '已取消'),
    ]
    
    settlement_number = models.CharField('结算单号', max_length=50, unique=True)
    supplier = models.ForeignKey('supplier.Supplier', on_delete=models.PROTECT, verbose_name='供应商')
    order = models.ForeignKey(Order, on_delete=models.PROTECT, verbose_name='订单')
    settlement_amount = models.DecimalField('结算金额', max_digits=12, decimal_places=2)
    settlement_date = models.DateField('结算日期')
    payment_date = models.DateField('付款日期', null=True, blank=True)
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    approved_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='approved_outsource_settlements', null=True, blank=True, verbose_name='审核人')
    approved_at = models.DateTimeField('审核时间', null=True, blank=True)
    remarks = models.TextField('备注', null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='created_outsource_settlements', verbose_name='创建人')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    is_deleted = models.BooleanField('是否删除', default=False)
    history = HistoricalRecords()
    
    class Meta:
        verbose_name = '外发结算单'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        db_table = 'fin_outsource_settlement'
    
    def __str__(self):
        return self.settlement_number

class Payment(models.Model):
    """
    付款计划模型
    用于管理付款计划和记录
    """
    TYPE_CHOICES = [
        ('factory', '工厂结算'),
        ('outsource', '外发结算'),
        ('material', '原料采购'),
        ('other', '其他'),
    ]
    
    STATUS_CHOICES = [
        ('planned', '已计划'),
        ('processing', '处理中'),
        ('completed', '已完成'),
        ('cancelled', '已取消'),
    ]
    
    payment_number = models.CharField('付款编号', max_length=50, unique=True)
    payment_type = models.CharField('付款类型', max_length=20, choices=TYPE_CHOICES)
    amount = models.DecimalField('付款金额', max_digits=12, decimal_places=2)
    planned_date = models.DateField('计划付款日期')
    actual_date = models.DateField('实际付款日期', null=True, blank=True)
    payee = models.CharField('收款方', max_length=100)
    bank_account = models.CharField('收款账号', max_length=50)
    bank_name = models.CharField('开户行', max_length=100)
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='planned')
    approved_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='approved_payments', null=True, blank=True, verbose_name='审核人')
    approved_at = models.DateTimeField('审核时间', null=True, blank=True)
    remarks = models.TextField('备注', null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='created_payments', verbose_name='创建人')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    is_deleted = models.BooleanField('是否删除', default=False)
    history = HistoricalRecords()
    
    class Meta:
        verbose_name = '付款计划'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        db_table = 'fin_payment'
    
    def __str__(self):
        return self.payment_number

class CostCalculation(models.Model):
    """
    成本核算模型
    用于管理产品成本的计算和记录
    """
    order = models.ForeignKey(Order, on_delete=models.PROTECT, verbose_name='订单')
    material_cost = models.DecimalField('材料成本', max_digits=12, decimal_places=2)
    labor_cost = models.DecimalField('人工成本', max_digits=12, decimal_places=2)
    overhead_cost = models.DecimalField('管理费用', max_digits=12, decimal_places=2)
    outsource_cost = models.DecimalField('外发成本', max_digits=12, decimal_places=2, default=0)
    logistics_cost = models.DecimalField('物流成本', max_digits=12, decimal_places=2, default=0)
    other_cost = models.DecimalField('其他成本', max_digits=12, decimal_places=2, default=0)
    total_cost = models.DecimalField('总成本', max_digits=12, decimal_places=2)
    unit_cost = models.DecimalField('单位成本', max_digits=10, decimal_places=2)
    gross_profit = models.DecimalField('毛利', max_digits=12, decimal_places=2)
    gross_profit_rate = models.DecimalField('毛利率', max_digits=5, decimal_places=2)
    calculation_date = models.DateField('核算日期')
    remarks = models.TextField('备注', null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='创建人')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    is_deleted = models.BooleanField('是否删除', default=False)
    history = HistoricalRecords()
    
    class Meta:
        verbose_name = '成本核算'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        db_table = 'fin_cost_calculation'
    
    def __str__(self):
        return f'{self.order} - {self.calculation_date}'