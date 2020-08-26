from django.db import models

from order_manager.models import Order

# Create your models here.

class Product(models.Model):
    vin = models.CharField('VIN', max_length=30, unique=True, help_text="本行为系统自动创建")
    order_num = models.ForeignKey(Order, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='订单')
    c_time = models.DateTimeField('创建时间', auto_now_add=True)
    m_time = models.DateTimeField('修改时间', auto_now=True)

    def __str__(self):
        return self.vin

    class Meta:
        verbose_name = '产品记录'
        verbose_name_plural = '产品记录'


class ProcessRecord(models.Model):
    result_choice = {(0, 'Fail'), (1, 'Pass')}
    product = models.ForeignKey('Product', on_delete=models.SET_NULL, blank=True, null=True, verbose_name='对应产品')
    num = models.SmallIntegerField('过程编号', default=0)
    result = models.SmallIntegerField('结果', choices=result_choice, null=True, blank=True, default=None)
    c_time = models.DateTimeField('创建时间', auto_now_add=True)
    m_time = models.DateTimeField('修改时间', auto_now=True)

    def __str__(self):
        return self.product.vin + ' ' + self.num + ' ' + self.result

    class Meta:
        verbose_name = '产品过程记录'
        verbose_name_plural = '产品过程记录'


class AssemblyRecord(models.Model):
    sn = models.CharField('SN', max_length=30, unique=True)
    process_record = models.ForeignKey(ProcessRecord, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='所属工序')
    c_time = models.DateTimeField('创建时间', auto_now_add=True)
    m_time = models.DateTimeField('修改时间', auto_now=True)

    def __str__(self):
        return self.sn

    class Meta:
        verbose_name = '装配记录'
        verbose_name_plural = '装配记录'


class TestRecord(models.Model):
    result_choice = {(0, 'Fail'), (1, 'Pass')}
    process_record = models.ForeignKey(ProcessRecord, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='产品过程记录')
    num = models.SmallIntegerField('测试项编号', default=0)

    name = models.CharField('测试项名称', max_length=100)
    result = models.SmallIntegerField('测试项结果', choices=result_choice, null=True, blank=True, default=None)

    data = models.FloatField('测试项数据')
    
    c_time = models.DateTimeField('创建时间', auto_now_add=True)
    m_time = models.DateTimeField('修改时间', auto_now=True)

    def __str__(self):
        return self.name + ' ' + self.result

    class Meta:
        verbose_name = '测试项记录'
        verbose_name_plural = '测试项记录'

        