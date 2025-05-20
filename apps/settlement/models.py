from django.db import models
from django.utils import timezone
from apps.supplier.models import Supplier
from apps.production.models import Order
from apps.system.models import BaseModel

class SettlementBill(BaseModel):
    """
    结算单模型
    """
    STATUS_CHOICES = (
        ('draft', '草稿'),
        ('submitted', '已提交'),
        ('approved', '已审批'),
        ('rejected', '已驳回'),
        ('returned', '已退回'),
        ('partial_paid', '部分付款'),
        ('paid', '已付款'),
        ('closed', '已关闭'),
    )
    
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, verbose_name='供应商')
    bill_number = models.CharField(max_length=50, unique=True, verbose_name='结算单号')
    period_start = models.DateField(verbose_name='结算周期开始')
    period_end = models.DateField(verbose_name='结算周期结束')
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='结算总金额')
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='已付金额')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name='状态')
    remark = models.TextField(blank=True, null=True, verbose_name='备注')
    
    class Meta:
        verbose_name = '结算单'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
    
    def __str__(self):
        return self.bill_number

class SettlementItem(BaseModel):
    """
    结算项目模型
    """
    TYPE_CHOICES = (
        ('procurement', '采购订单'),
        ('return', '退货'),
        ('adjustment', '调整'),
    )
    
    settlement = models.ForeignKey(SettlementBill, on_delete=models.CASCADE, related_name='items', verbose_name='结算单')
    item_type = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name='项目类型')
    reference_number = models.CharField(max_length=50, verbose_name='关联单号')
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='订单')
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='金额')
    description = models.CharField(max_length=255, verbose_name='描述')
    
    class Meta:
        verbose_name = '结算项目'
        verbose_name_plural = verbose_name
    
    def __str__(self):
        return f"{self.settlement.bill_number}-{self.reference_number}"

class ApprovalHistory(BaseModel):
    """
    审批历史模型
    """
    ACTION_CHOICES = (
        ('submit', '提交'),
        ('approve', '通过'),
        ('reject', '驳回'),
        ('return', '退回修改'),
    )
    
    settlement = models.ForeignKey(SettlementBill, on_delete=models.CASCADE, related_name='approval_history', verbose_name='结算单')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, verbose_name='操作')
    remark = models.TextField(blank=True, null=True, verbose_name='备注')
    
    class Meta:
        verbose_name = '审批历史'
        verbose_name_plural = verbose_name
        ordering = ['created_at']

class Payment(BaseModel):
    """
    付款记录模型
    """
    METHOD_CHOICES = (
        ('bank_transfer', '银行转账'),
        ('cash', '现金'),
        ('check', '支票'),
        ('other', '其他'),
    )
    
    settlement = models.ForeignKey(SettlementBill, on_delete=models.CASCADE, related_name='payments', verbose_name='结算单')
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='付款金额')
    payment_date = models.DateField(verbose_name='付款日期')
    payment_method = models.CharField(max_length=20, choices=METHOD_CHOICES, verbose_name='付款方式')
    reference = models.CharField(max_length=100, blank=True, null=True, verbose_name='参考号')
    remark = models.TextField(blank=True, null=True, verbose_name='备注')
    
    class Meta:
        verbose_name = '付款记录'
        verbose_name_plural = verbose_name
        ordering = ['-payment_date']

class Reconciliation(BaseModel):
    """
    对账单模型
    """
    STATUS_CHOICES = (
        ('draft', '草稿'),
        ('confirmed', '已确认'),
        ('closed', '已关闭'),
    )
    
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, verbose_name='供应商')
    reconciliation_number = models.CharField(max_length=50, unique=True, verbose_name='对账单号')
    month = models.CharField(max_length=7, verbose_name='对账月份')  # 格式: YYYY-MM
    total_procurement = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='采购总额')
    total_settlement = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='结算总额')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name='状态')
    confirmation_date = models.DateField(null=True, blank=True, verbose_name='确认日期')
    confirmed_by = models.CharField(max_length=50, blank=True, null=True, verbose_name='确认人')
    remark = models.TextField(blank=True, null=True, verbose_name='备注')
    
    class Meta:
        verbose_name = '对账单'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
    
    def __str__(self):
        return self.reconciliation_number