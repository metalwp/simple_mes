from django.db import models

from db.base_model import BaseModel

# Create your models here.


class ProcessRoute(BaseModel):
    name = models.CharField('工艺路线名称', max_length=100)
    remark = models.CharField('备注', max_length=200, null=True, blank=True)    
    
    class Meta:
        verbose_name = '工艺路线'
        verbose_name_plural = '工艺路线'
        db_table = 'sm_process_route'
        unique_together = ('is_delete', "name")

    def __str__(self):
        return self.name


class ProcessStep(BaseModel):
    name = models.CharField('工序名称', max_length=100)
    fixture = models.ForeignKey('station_manager.Fixture', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="工装")
    relate_material = models.ManyToManyField("bom_manager.MaterialModel", blank=True, verbose_name='关联物料')
    sequence_no = models.SmallIntegerField('工序顺序号', null=True, blank=True, default=None)
    process_lock = models.BooleanField('工序互锁', default=False)
    process_route = models.ForeignKey("ProcessRoute", on_delete=models.SET_NULL, null=True, blank=True, verbose_name="工艺路线")
    remark = models.CharField('备注', max_length=200, null=True, blank=True)    
    
    class Meta:
        verbose_name = '工序'
        verbose_name_plural = '工序'
        db_table = 'sm_process_step'
        unique_together = ('is_delete', 'sequence_no', 'process_route')

    def __str__(self):
        return self.name

    # def validate_unique(self, exclude=None):
    #     if StudentType.objects.exclude(id=self.id).filter(department=self.department, \
    #                                                       major__isnull=True, type=self.type).exists():
    #         raise ValidationError("该人员类型已经存在!")
    #     super(StudentType, self).validate_unique(exclude)
