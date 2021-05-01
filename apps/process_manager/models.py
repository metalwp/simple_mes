from django.db import models

from db.base_model import BaseModel

# Create your models here.


class AssembleLine(BaseModel):
    name = models.CharField('生产线名称', max_length=100)
    remark = models.CharField('备注', max_length=200, null=True, blank=True)

    class Meta:
        verbose_name = '生产线'
        verbose_name_plural = '生产线'
        db_table = 'sm_assemble_line'

    def __str__(self):
        return self.name


class ProcessRoute(BaseModel):
    name = models.CharField('工艺路线名称', max_length=100)
    assemble_line = models.ForeignKey("AssembleLine", on_delete=models.SET_NULL, null=True, blank=True, verbose_name="生产线")
    remark = models.CharField('备注', max_length=200, null=True, blank=True)
    
    class Meta:
        verbose_name = '工艺路线'
        verbose_name_plural = '工艺路线'
        db_table = 'sm_process_route'

    def __str__(self):
        return self.name


class ProcessStep(BaseModel):
    CATEGORY_CHOICE = (
        (0, '无'),
        (1, "组装"),  #
        (2, "测试（设备）"),
        (3, "标定"),  #
        (4, "检验"),  #
        (5, "标签打印"),  #
        (6, "VIN生成"),  #
        (7, "其他"),
    )

    name = models.CharField('工序名称', max_length=100)
    fixture = models.ForeignKey('station_manager.Fixture', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="工装")
    material = models.ManyToManyField("bom_manager.MaterialModel", through='ProcessStep_MaterialModel')
    sequence_no = models.SmallIntegerField('工序顺序号', null=True, blank=True, default=None)
    process_lock = models.BooleanField('工序互锁', default=False)
    process_route = models.ForeignKey("ProcessRoute", on_delete=models.SET_NULL, null=True, blank=True, verbose_name="工艺路线")
    remark = models.CharField('备注', max_length=200, null=True, blank=True)
    category = models.SmallIntegerField('工序类型', choices=CATEGORY_CHOICE, default=0)
    
    class Meta:
        verbose_name = '工序'
        verbose_name_plural = '工序'
        db_table = 'sm_process_step'
        unique_together = ('sequence_no', 'process_route')

    def __str__(self):
        return self.name
    # def validate_unique(self, exclude=None):
    #     if StudentType.objects.exclude(id=self.id).filter(department=self.department, \
    #                                                       major__isnull=True, type=self.type).exists():
    #         raise ValidationError("该人员类型已经存在!")
    #     super(StudentType, self).validate_unique(exclude)


class ProcessStep_MaterialModel(models.Model):
    process_step = models.ForeignKey("ProcessStep", on_delete=models.CASCADE)
    material_model = models.ForeignKey("bom_manager.MaterialModel", on_delete=models.CASCADE)
    quantity = models.DecimalField('用量', max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'sm_processstep_material_model'