from django.db import models

from bom_manager.models import MaterialModel
from station_manager.models import Station
# Create your models here.


class ProcessRoute(models.Model):
    name = models.CharField('工艺路线名称', max_length=100, unique=True)
    c_time = models.DateTimeField('创建时间', auto_now_add=True)
    m_time = models.DateTimeField('修改时间', auto_now=True)
    remark = models.CharField('备注', max_length=200, null=True, blank=True)    
    
    class Meta:
        verbose_name = '工艺路线'
        verbose_name_plural = '工艺路线'

    def __str__(self):
        return self.name


class ProcessStep(models.Model):
    name = models.CharField('工序名称', max_length=100, unique=True)
    station = models.ForeignKey(Station, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="工站")
    relate_material = models.ManyToManyField(MaterialModel, blank=True, verbose_name='关联物料')
    c_time = models.DateTimeField('创建时间', auto_now_add=True)
    m_time = models.DateTimeField('修改时间', auto_now=True)
    sequence_no = models.SmallIntegerField('工序顺序号', default=0)
    process_lock = models.BooleanField('工序互锁', default=False)
    process_route = models.ForeignKey(ProcessRoute, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="工艺路线")
    remark = models.CharField('备注', max_length=200, null=True, blank=True)    
    
    class Meta:
        verbose_name = '工序'
        verbose_name_plural = '工序'

    def __str__(self):
        return self.name
