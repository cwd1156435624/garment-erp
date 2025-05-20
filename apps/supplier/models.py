from django.db import models
from simple_history.models import HistoricalRecords
from apps.users.models import User

class Supplier(models.Model):
    """
    供应商模型
    用于存储供应商基本信息
    """
    TYPE_CHOICES = [
        ('material', '原料供应商'),
        ('outsource', '外发加工商'),
        ('equipment', '设备供应商'),
        ('other', '其他'),
    ]
    
    STATUS_CHOICES = [
        ('active', '合作中'),
        ('suspended', '已暂停'),
        ('terminated', '已终止'),
    ]
    
    name = models.CharField('供应商名称', max_length=100)
    supplier_type = models.CharField('供应商类型', max_length=20, choices=TYPE_CHOICES)
    contact_person = models.CharField('联系人', max_length=50)
    contact_phone = models.CharField('联系电话', max_length=20)
    email = models.EmailField('电子邮箱', null=True, blank=True)
    address = models.CharField('地址', max_length=200)
    business_license = models.CharField('营业执照号', max_length=50)
    tax_number = models.CharField('税号', max_length=50)
    bank_name = models.CharField('开户行', max_length=100)
    bank_account = models.CharField('银行账号', max_length=50)
    credit_limit = models.DecimalField('信用额度', max_digits=12, decimal_places=2, default=0)
    payment_terms = models.CharField('付款条件', max_length=200)
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='active')
    remarks = models.TextField('备注', null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='创建人', related_name='supplier_created')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    is_deleted = models.BooleanField('是否删除', default=False)
    history = HistoricalRecords()
    
    class Meta:
        verbose_name = '供应商'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        db_table = 'sup_supplier'
    
    def __str__(self):
        return self.name

class SupplierPerformance(models.Model):
    """
    供应商绩效评分模型
    用于记录供应商的绩效评估结果
    """
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, verbose_name='供应商')
    evaluation_date = models.DateField('评估日期')
    quality_score = models.DecimalField('质量得分', max_digits=5, decimal_places=2)
    delivery_score = models.DecimalField('交付得分', max_digits=5, decimal_places=2)
    price_score = models.DecimalField('价格得分', max_digits=5, decimal_places=2)
    service_score = models.DecimalField('服务得分', max_digits=5, decimal_places=2)
    total_score = models.DecimalField('总分', max_digits=5, decimal_places=2)
    evaluation_content = models.TextField('评估内容')
    improvement_suggestions = models.TextField('改进建议', null=True, blank=True)
    evaluated_by = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='评估人', related_name='supplier_performances')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    is_deleted = models.BooleanField('是否删除', default=False)
    history = HistoricalRecords()
    
    class Meta:
        verbose_name = '供应商绩效'
        verbose_name_plural = verbose_name
        ordering = ['-evaluation_date']
        db_table = 'sup_performance'
    
    def __str__(self):
        return f'{self.supplier} - {self.evaluation_date}'

class SupplierContract(models.Model):
    """
    供应商合同模型
    用于管理供应商合同文件和信息
    """
    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('active', '生效中'),
        ('expired', '已过期'),
        ('terminated', '已终止'),
    ]
    
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, verbose_name='供应商')
    contract_number = models.CharField('合同编号', max_length=50, unique=True)
    contract_name = models.CharField('合同名称', max_length=100)
    contract_type = models.CharField('合同类型', max_length=50)
    start_date = models.DateField('生效日期')
    end_date = models.DateField('到期日期')
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='draft')
    contract_file = models.FileField('合同文件', upload_to='contracts/')
    amount = models.DecimalField('合同金额', max_digits=12, decimal_places=2)
    payment_terms = models.TextField('付款条件')
    remarks = models.TextField('备注', null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='创建人', related_name='supplier_contract_created')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    is_deleted = models.BooleanField('是否删除', default=False)
    history = HistoricalRecords()
    
    class Meta:
        verbose_name = '供应商合同'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        db_table = 'sup_contract'
    
    def __str__(self):
        return self.contract_number

class SupplierEvaluation(models.Model):
    """
    供应商评估模型
    用于记录供应商的综合评估信息
    """
    RESULT_CHOICES = [
        ('excellent', '优秀'),
        ('good', '良好'),
        ('fair', '一般'),
        ('poor', '差'),
    ]
    
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, verbose_name='供应商')
    evaluation_date = models.DateField('评估日期')
    evaluation_period = models.CharField('评估周期', max_length=50)
    financial_status = models.TextField('财务状况评估')
    production_capacity = models.TextField('生产能力评估')
    quality_system = models.TextField('质量体系评估')
    market_reputation = models.TextField('市场信誉评估')
    cooperation_history = models.TextField('合作历史评估')
    overall_result = models.CharField('综合评定', max_length=20, choices=RESULT_CHOICES)
    improvement_requirements = models.TextField('改进要求', null=True, blank=True)
    next_evaluation_date = models.DateField('下次评估日期')
    evaluated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='supplier_evaluations')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    is_deleted = models.BooleanField('是否删除', default=False)
    history = HistoricalRecords()
    
    class Meta:
        verbose_name = '供应商评估'
        verbose_name_plural = verbose_name
        ordering = ['-evaluation_date']
        db_table = 'sup_evaluation'
    
    def __str__(self):
        return f'{self.supplier} - {self.evaluation_date}'