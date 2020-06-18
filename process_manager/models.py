from django.db import models

from product_manager.models import ProductModel
from bom_manager.models import MaterialModel
from station_manager.models import Station
# Create your models here.


class ProcessStep(models.Model):
    step_name = models.CharField('工序名称', max_length=100, unique=True)
    product_model = models.ManyToManyField(ProductModel, blank=True, verbose_name='所属产品')
    relate_material = models.ManyToManyField(MaterialModel, blank=True, verbose_name='关联物料')
    station = models.ForeignKey(Station, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='工站')
    sequence_no = models.SmallIntegerField('工序顺序号', default=0)
    process_lock = models.BooleanField('工序互锁', default=False)
    c_time = models.DateTimeField('创建时间', auto_now_add=True)
    m_time = models.DateTimeField('修改时间', auto_now=True)

    class Meta:
        verbose_name = '生产过程'
        verbose_name_plural = '生产过程'

    def __str__(self):
        return self.step_name
