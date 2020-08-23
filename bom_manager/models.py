from django.db import models
from product_manager.models import ProductModel

# Create your models here.

class BOM(models.Model):
    product_model = models.OneToOneField(ProductModel, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='产品型号')
    version = models.CharField('BOM版本', max_length=30)
    remark = models.CharField('备注', max_length=200, null=True, blank=True)    
    c_time = models.DateTimeField('创建时间', auto_now_add=True)
    m_time = models.DateTimeField('修改时间', auto_now=True)    

    class Meta:
        verbose_name = 'BOM'
        verbose_name_plural = 'BOM'
        unique_together = ('product_model', 'version')  # 联合约束

    def __str__(self):
        return self.product_model.name + ' ' + self.version

class MaterialModel(models.Model):
    category_choice = (
        (0, '无'),
        (1, '钣金零件'),
        (2, '底盘总成'),
        (3, '电子电气'),
        (4, '金属标件'),
        (5, '塑料标件'),
        (6, '塑料零件'),
        (7, '其他'),)
    bom = models.ManyToManyField(BOM, blank=True, verbose_name='BOM')
    name = models.CharField('物料名称', max_length=100)
    model = models.CharField('型号描述', max_length=200, blank=True, null=True)
    erp_no = models.CharField('物料号', max_length=30)
    category = models.SmallIntegerField('类别', choices=category_choice, default=0)
    quantity = models.FloatField('用量')
    is_traced = models.BooleanField("是否追溯", default=False)

    c_time = models.DateTimeField('创建时间', auto_now_add=True)
    m_time = models.DateTimeField('修改时间', auto_now=True)

    class Meta:
        verbose_name = '物料型号'
        verbose_name_plural = '物料型号'

    def __str__(self):
        return self.erp_no + ' ' + self.name


class Inspection(models.Model):
    material_model = models.ManyToManyField(MaterialModel, blank=True, verbose_name='物料型号')
    num = models.CharField('检验编号', max_length=100, unique=True)
