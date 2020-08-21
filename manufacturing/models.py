from django.db import models

# Create your models here.

class Product(models.Model):
    vin = models.CharField('VIN', max_length=30, unique=True, help_text="本行为系统自动创建")
    order = models.ForeignKey('Order', on_delete=models.SET_NULL, blank=True, null=True, verbose_name='订单')
    start_time = models.DateTimeField('开始时间')
    end_time = models.DateTimeField('结束时间')

    def __str__(self):
        return self.vin

    class Meta:
        verbose_name = '产品记录'
        verbose_name_plural = '产品记录'


class ProductRecord(models.Model):
    product = models.ForeignKey('Product', on_delete=models.SET_NULL, blank=True, null=True, verbose_name='对应产品')
    sequence_no = models.SmallIntegerField('工序顺序号', default=0)
    step_name = models.CharField('工序名称', max_length=100, unique=True)
    start_time = models.DateTimeField('开始时间')
    end_time = models.DateTimeField('结束时间')

    def __str__(self):
        return self.product.vin + ' ' + self.step_name

    class Meta:
        verbose_name = '产品过程记录'
        verbose_name_plural = '产品过程记录'


class Material(models.Model):
    sn = models.CharField('序列号', max_length=30, unique=True)
    is_used = models.BooleanField('是否已装配', default=False)
    iqc_checked = models.BooleanField('是否IQC检验', default=False)
    batch_no = models.CharField('批次号', max_length=30, blank=True, null=True)
    c_time = models.DateTimeField('创建时间', auto_now_add=True)
    m_time = models.DateTimeField('修改时间', auto_now=True)
    product_record = models.ForeignKey('ProductRecord', on_delete=models.SET_NULL, blank=True, null=True, verbose_name='产品过程记录')

    def __str__(self):
        return self.sn

    class Meta:
        verbose_name = '物料信息'
        verbose_name_plural = '物料信息'


class TestRecord(models.Model):
    vin = models.CharField('VIN', max_length=30)
    total_result = models.BooleanField('总结果', default=False)
    item_name = models.CharField('测试项名称', max_length=100, unique=True)
    item_result = models.BooleanField('测试项结果', default=False)
    item_data = models.CharField('测试项数据', max_length=100)
    item_upper = models.CharField('测试标准上限', max_length=100)
    item_lower = models.CharField('测试标准下限', max_length=100)
    c_time = models.DateTimeField('创建时间', auto_now_add=True)
    m_time = models.DateTimeField('修改时间', auto_now=True)
    product_record = models.ForeignKey('ProductRecord', on_delete=models.SET_NULL, blank=True, null=True, verbose_name='产品过程记录')

    def __str__(self):
        return self.vin + ' ' + self.item_name

    class Meta:
        verbose_name = '测试记录'
        verbose_name_plural = '测试记录'


class IqcRecord(models.Model):
    sn = models.CharField('序列号', max_length=30)
    total_result = models.BooleanField('总结果', default=False)
    item_name = models.CharField('测试项名称', max_length=100, unique=True)
    item_result = models.BooleanField('测试项结果', default=False)
    item_data = models.CharField('测试项数据', max_length=100)
    item_upper = models.CharField('测试标准上限', max_length=100)
    item_lower = models.CharField('测试标准下限', max_length=100)
    c_time = models.DateTimeField('创建时间', auto_now_add=True)
    m_time = models.DateTimeField('修改时间', auto_now=True)
    material = models.ForeignKey('Material', on_delete=models.SET_NULL, blank=True, null=True, verbose_name='所属物料')

    def __str__(self):
        return self.sn + ' ' + self.item_name

    class Meta:
        verbose_name = '检验记录'
        verbose_name_plural = '检验记录'