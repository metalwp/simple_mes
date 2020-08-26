from django.db import models

# Create your models here.

class GeneralMaterial(models.Model):
    erp = models.CharField('物料号', max_length=20)
    batch_num = models.CharField('批次号', max_length=20)
    total_quantity = models.FloatField('来料总数量')
    qualified_quantity = models.FloatField('来料合格数量')
    used_quantity = models.FloatField('使用数量', default=0)
    c_time = models.DateTimeField('创建时间', auto_now_add=True)
    m_time = models.DateTimeField('修改时间', auto_now=True)

    def __str__(self):
        return self.erp + ' ' + self.batch_num

    class Meta:
        verbose_name = '一般物料信息'
        verbose_name_plural = '一般物料信息'


class GMInspectRecord(models.Model):
    general_material = models.ForeignKey(GeneralMaterial, on_delete=models.SET_DEFAULT, null=True, blank=True, verbose_name='所属一般物料')
    num = models.CharField('检验编号', max_length=20)
    name = models


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