from django.db import models

from db.base_model import BaseModel


# Create your models here.

class GeneralMaterial(BaseModel):
    material_model = models.ForeignKey('bom_manager.MaterialModel', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='所属物料型号')
    batch_num = models.CharField('批次号', max_length=20)
    total_quantity = models.DecimalField('来料总数量', max_digits=10, decimal_places=2, default=0)
    qualified_quantity = models.DecimalField('来料合格数量', max_digits=10, decimal_places=2, default=0)
    used_quantity = models.DecimalField('使用数量', max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.material_model.erp_no + ' ' + self.batch_num

    class Meta:
        verbose_name = '一般物料信息'
        verbose_name_plural = verbose_name
        db_table = 'sm_general_material'


class GMInspectRecord(BaseModel):
    general_material = models.ForeignKey("GeneralMaterial", on_delete=models.SET_NULL, null=True, blank=True, verbose_name='所属一般物料')
    num = models.CharField('检验项编号', max_length=20)
    name = models.CharField('检验项名称', max_length=20)
    qualified_quantity = models.DecimalField('检验项合格数量', max_digits=10, decimal_places=2, default=0)
    data = models.DecimalField('检验项数据', max_digits=10, decimal_places=2)

    def __str__(self):
        return self.num + ' ' + self.data

    class Meta:
        verbose_name = '一般物料检测项'
        verbose_name_plural = '一般物料检测项'
        db_table = 'sm_gminspect_record'


class TraceMaterial(BaseModel):
    status_choice = (
        (0, "未检验"),
        (1, "检验中"),
        (2, "检验OK"),
        (3, "检验NG"),
    )
    used_choice = (
        (0, "未使用"),
        (1, "已使用")
    )
    material_model = models.ForeignKey('bom_manager.MaterialModel', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='所属物料型号')
    status = models.SmallIntegerField('检验状态', choices=status_choice, default=0)
    sn = models.CharField('SN', max_length=30)
    is_used = models.SmallIntegerField('是否使用', choices=used_choice, default=0)
    batch_num = models.CharField('批次号', max_length=20, null=True, blank=True)

    def __str__(self):
        return self.sn

    class Meta:
        verbose_name = '追溯物料信息'
        verbose_name_plural = verbose_name
        db_table = 'sm_trace_material'


class TMInspectRecord(BaseModel):
    result_choice = (
        (0, "Fail"),
        (1, "Pass")
    )
    trace_material = models.ForeignKey("TraceMaterial", on_delete=models.SET_NULL, null=True, blank=True, verbose_name='所属一般物料')
    num = models.CharField('检验项编号', max_length=20)
    name = models.CharField('检验项名称', max_length=20)
    result = models.SmallIntegerField('检验项结果', choices=result_choice, default=0)
    data = models.DecimalField('检验项数据', max_digits=10, decimal_places=2)

    def __str__(self):
        return self.num + ' ' + str(self.result) + ' ' + self.data

    class Meta:
        verbose_name = '追溯物料检测项'
        verbose_name_plural = verbose_name
        db_table = 'sm_tminspect_record'


