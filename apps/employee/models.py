from django.db import models
from simple_history.models import HistoricalRecords
from apps.users.models import User

class Employee(models.Model):
    """
    员工模型
    用于存储员工基本信息
    """
    STATUS_CHOICES = [
        ('active', '在职'),
        ('resigned', '离职'),
        ('suspended', '停职'),
    ]
    
    EDUCATION_CHOICES = [
        ('high_school', '高中'),
        ('college', '大专'),
        ('bachelor', '本科'),
        ('master', '硕士'),
        ('doctor', '博士'),
    ]
    
    employee_number = models.CharField('工号', max_length=50, unique=True)
    name = models.CharField('姓名', max_length=50)
    gender = models.CharField('性别', max_length=10)
    birth_date = models.DateField('出生日期')
    id_card = models.CharField('身份证号', max_length=18, unique=True)
    phone = models.CharField('手机号', max_length=11)
    email = models.EmailField('电子邮箱', null=True, blank=True)
    address = models.CharField('住址', max_length=200)
    education = models.CharField('学历', max_length=20, choices=EDUCATION_CHOICES)
    department = models.CharField('部门', max_length=50)
    position = models.CharField('职位', max_length=50)
    hire_date = models.DateField('入职日期')
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='active')
    bank_name = models.CharField('开户行', max_length=100)
    bank_account = models.CharField('银行账号', max_length=50)
    emergency_contact = models.CharField('紧急联系人', max_length=50)
    emergency_phone = models.CharField('紧急联系电话', max_length=11)
    remarks = models.TextField('备注', null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='创建人')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    is_deleted = models.BooleanField('是否删除', default=False)
    history = HistoricalRecords()
    
    class Meta:
        verbose_name = '员工'
        verbose_name_plural = verbose_name
        ordering = ['employee_number']
        db_table = 'emp_employee'
    
    def __str__(self):
        return f'{self.employee_number} - {self.name}'

class Attendance(models.Model):
    """
    考勤记录模型
    用于记录员工的考勤信息
    """
    TYPE_CHOICES = [
        ('check_in', '上班打卡'),
        ('check_out', '下班打卡'),
        ('break_start', '休息开始'),
        ('break_end', '休息结束'),
    ]
    
    STATUS_CHOICES = [
        ('normal', '正常'),
        ('late', '迟到'),
        ('early_leave', '早退'),
        ('absent', '缺勤'),
        ('overtime', '加班'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.PROTECT, verbose_name='员工')
    attendance_date = models.DateField('考勤日期')
    attendance_type = models.CharField('考勤类型', max_length=20, choices=TYPE_CHOICES)
    attendance_time = models.DateTimeField('考勤时间')
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='normal')
    location = models.CharField('打卡地点', max_length=200, null=True, blank=True)
    device = models.CharField('打卡设备', max_length=100, null=True, blank=True)
    remarks = models.TextField('备注', null=True, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    is_deleted = models.BooleanField('是否删除', default=False)
    history = HistoricalRecords()
    
    class Meta:
        verbose_name = '考勤记录'
        verbose_name_plural = verbose_name
        ordering = ['-attendance_date', '-attendance_time']
        db_table = 'emp_attendance'
    
    def __str__(self):
        return f'{self.employee} - {self.attendance_date} - {self.get_attendance_type_display()}'

class PerformanceEvaluation(models.Model):
    """
    绩效评估模型
    用于记录员工的绩效评估信息
    """
    PERIOD_CHOICES = [
        ('monthly', '月度'),
        ('quarterly', '季度'),
        ('yearly', '年度'),
    ]
    
    RESULT_CHOICES = [
        ('excellent', '优秀'),
        ('good', '良好'),
        ('fair', '一般'),
        ('poor', '差'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.PROTECT, verbose_name='员工')
    evaluation_period = models.CharField('评估周期', max_length=20, choices=PERIOD_CHOICES)
    start_date = models.DateField('开始日期')
    end_date = models.DateField('结束日期')
    work_quality_score = models.DecimalField('工作质量得分', max_digits=5, decimal_places=2)
    work_efficiency_score = models.DecimalField('工作效率得分', max_digits=5, decimal_places=2)
    responsibility_score = models.DecimalField('责任心得分', max_digits=5, decimal_places=2)
    teamwork_score = models.DecimalField('团队协作得分', max_digits=5, decimal_places=2)
    innovation_score = models.DecimalField('创新能力得分', max_digits=5, decimal_places=2)
    total_score = models.DecimalField('总分', max_digits=5, decimal_places=2)
    result = models.CharField('评估结果', max_length=20, choices=RESULT_CHOICES)
    achievements = models.TextField('主要成就')
    improvements = models.TextField('需改进方面')
    evaluator = models.ForeignKey(User, on_delete=models.PROTECT, related_name='evaluations_made', verbose_name='评估人')
    reviewed_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='evaluations_reviewed', null=True, blank=True, verbose_name='复核人')
    remarks = models.TextField('备注', null=True, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    is_deleted = models.BooleanField('是否删除', default=False)
    history = HistoricalRecords()
    
    class Meta:
        verbose_name = '绩效评估'
        verbose_name_plural = verbose_name
        ordering = ['-end_date']
        db_table = 'emp_performance_evaluation'
    
    def __str__(self):
        return f'{self.employee} - {self.get_evaluation_period_display()} - {self.end_date}'