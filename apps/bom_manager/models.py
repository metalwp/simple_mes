from django.db import models

from db.base_model import BaseModel

# Create your models here.


class BOM(BaseModel):
    product_model = models.ForeignKey("product_manager.ProductModel", on_delete=models.SET_NULL, blank=True, null=True, verbose_name='产品型号')
    version = models.CharField('BOM版本', max_length=10)
    remark = models.CharField('备注', max_length=200, null=True, blank=True)
    erp_no = models.CharField('物料号', max_length=100)  # unique=True

    class Meta:
        db_table = 'sm_bom'
        verbose_name = 'BOM'
        verbose_name_plural = 'BOM'

    def __str__(self):
        return self.product_model.name + ' ' + self.version
        # return self.version


class MaterialModel(BaseModel):
    CATEGORY_CHOICE = (
        (0, '无'),
        (1, '钣金零件'),
        (2, '底盘总成'),
        (3, '电子电气'),
        (4, '金属标件'),
        (5, '塑料标件'),
        (6, '塑料零件'),
        (7, '其他'),)
        
    bom = models.ManyToManyField("BOM", through='Bom_MaterialModel')
    name = models.CharField('物料名称', max_length=100)
    model = models.CharField('型号描述', max_length=200, blank=True, null=True)
    erp_no = models.CharField('物料号', max_length=30)
    category = models.SmallIntegerField('类别', choices=CATEGORY_CHOICE, default=0)
    is_traced = models.BooleanField("是否追溯", default=False)

    class Meta:
        verbose_name = '物料型号'
        verbose_name_plural = '物料型号'
        db_table = 'sm_material_model'
        unique_together = ('is_delete', 'erp_no')

    def __str__(self):
        return self.erp_no + ' ' + self.name


class Bom_MaterialModel(models.Model):
    bom = models.ForeignKey("BOM", on_delete=models.CASCADE)
    material_model = models.ForeignKey("MaterialModel", on_delete=models.CASCADE)
    quantity = models.DecimalField('用量', max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'sm_bom_material_model'



