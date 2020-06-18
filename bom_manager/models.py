from django.db import models
from product_manager.models import ProductModel

# Create your models here.


class MaterialModel(models.Model):
    product_model = models.ForeignKey(ProductModel, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='产品型号')
    bom_version = models.CharField('BOM版本', max_length=30)
    name = models.CharField('物料名称', max_length=100)
    erp_no = models.CharField('物料号', max_length=30, unique=True)
    quantity = models.FloatField('用量')
    is_traced = models.BooleanField("是否追溯", default=False)
    c_time = models.DateTimeField('创建时间', auto_now_add=True)
    m_time = models.DateTimeField('修改时间', auto_now=True)

    class Meta:
        verbose_name = '物料型号'
        verbose_name_plural = '物料型号'
        unique_together = ('product_model', 'bom_version')  # 联合约束

    def __str__(self):
        return self.erp_no + ' ' + self.name
