from django.db import models

# from process_manager.models import ProcessRoute

# Create your models here.


class ProductModel(models.Model):
    name = models.CharField('产品名称', max_length=30)
    model = models.CharField('型号名称', max_length=30)
    category = models.ForeignKey("ProductCategory", on_delete=models.SET_NULL, blank=True, null=True, verbose_name='产品分类')
    erp_no = models.CharField('物料号', max_length=100, unique=True)
    process_route = models.ForeignKey('process_manager.ProcessRoute', on_delete=models.SET_NULL, blank=True, null=True, verbose_name='工艺路线')
    c_time = models.DateTimeField('创建时间', auto_now_add=True)
    m_time = models.DateTimeField('修改时间', auto_now=True)

    class Meta:
        verbose_name = '产品配置'
        verbose_name_plural = '产品配置'

    def __str__(self):
        return self.erp_no + " " + self.name


class ProductCategory(models.Model):
    name = models.CharField('分类名称', unique=True, max_length=30)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True, null=True, verbose_name='父类')
    c_time = models.DateTimeField('创建时间', auto_now_add=True)
    m_time = models.DateTimeField('修改时间', auto_now=True)

    class Meta:
        verbose_name = '产品分类'
        verbose_name_plural = '产品分类'

    def __str__(self):
        return self.name





