from django.db import models

from db.base_model import BaseModel


# Create your models here.


class ProductCategory(BaseModel):
    name = models.CharField('分类名称', unique=True, max_length=30)  # unique=True
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True, null=True, verbose_name='父类')

    class Meta:
        db_table = 'sm_product_category'
        verbose_name = '产品分类'
        verbose_name_plural = '产品分类'

    def __str__(self):
        return self.name


class ProductModel(BaseModel):
    name = models.CharField('产品名称', max_length=30)
    model = models.CharField('产品型号', max_length=30)
    category = models.ForeignKey("ProductCategory", on_delete=models.SET_NULL, blank=True, null=True, verbose_name='产品分类')
    erp_no = models.CharField('物料号', unique=True, max_length=100)  # unique=True
    process_route = models.ForeignKey('process_manager.ProcessRoute', on_delete=models.SET_NULL, blank=True, null=True, verbose_name='工艺路线')

    class Meta:
        verbose_name = '产品配置'
        verbose_name_plural = '产品配置'
        db_table = 'sm_product_model'

    def __str__(self):
        return self.erp_no + " " + self.name









