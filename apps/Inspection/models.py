from django.db import models

from db.base_model import BaseModel


# Create your models here.
class Inspection(BaseModel):
    MODE_CHOICE = (
            (0, "无"),
            (1, "目视"),
            (2, "测量工具"),
            (3, "手动设备"),
            (4, "自动设备"))
        
    CATEGORY_CHOICE = (
            (0, "无"),
            (1, "外观"),
            (2, "功能"),
            (3, "性能"))

    material_model = models.ForeignKey("bom_manager.MaterialModel", on_delete=models.SET_NULL, null=True, blank=True, verbose_name='物料型号')
    process_step = models.ForeignKey('process_manager.ProcessStep', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='所属工序')
    num = models.CharField('检验编号',  max_length=20)
    name = models.CharField('检验名称', max_length=50)
    category = models.SmallIntegerField('检验类型', choices=CATEGORY_CHOICE, default=0)
    mode = models.SmallIntegerField('检验方式', choices=MODE_CHOICE, default=0)
    upper = models.DecimalField('上限', max_digits=10, decimal_places=2)
    lower = models.DecimalField('下限', max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = '检验项'
        verbose_name_plural = '检验项'
        db_table = 'sm_inspection'

    def __str__(self):
        return self.num + ' ' + self.name


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
    MODE_CHOICE = (
        (0, "无"),
        (1, "目视"),
        (2, "测量工具"),
        (3, "手动设备"),
        (4, "自动设备"))

    CATEGORY_CHOICE = (
        (0, "无"),
        (1, "外观"),
        (2, "功能"),
        (3, "性能"))

    general_material = models.ForeignKey("GeneralMaterial", on_delete=models.SET_NULL, null=True, blank=True, verbose_name='所属一般物料')
    num = models.CharField('检验项编号', max_length=20)
    name = models.CharField('检验项名称', max_length=20)
    category = models.SmallIntegerField('检验类型', choices=CATEGORY_CHOICE, default=0)
    mode = models.SmallIntegerField('检验方式', choices=MODE_CHOICE, default=0)
    qualified_quantity = models.DecimalField('检验项合格数量', max_digits=10, decimal_places=2, default=0)
    data = models.CharField('检测数据记录', max_length=200)
    operator = models.ForeignKey('account.User', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='检验员')
    upper = models.DecimalField('上限', max_digits=10, decimal_places=2)
    lower = models.DecimalField('下限', max_digits=10, decimal_places=2)

    def __str__(self):
        return self.num + ' ' + self.data

    class Meta:
        verbose_name = '一般物料检测项'
        verbose_name_plural = '一般物料检测项'
        db_table = 'sm_gminspect_record'


class TraceMaterial(BaseModel):
    STATUS_CHOICE = (
        (0, "未检验"),
        (1, "检验中"),
        (2, "检验OK"),
        (3, "检验NG"),
    )
    USED_CHOICE = (
        (0, "未使用"),
        (1, "已使用")
    )
    material_model = models.ForeignKey('bom_manager.MaterialModel', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='所属物料型号')
    status = models.SmallIntegerField('检验状态', choices=STATUS_CHOICE, default=0)
    sn = models.CharField('SN', max_length=30)
    is_used = models.SmallIntegerField('是否使用', choices=USED_CHOICE, default=0)
    batch_num = models.CharField('批次号', max_length=20, null=True, blank=True)

    def __str__(self):
        return self.sn

    class Meta:
        verbose_name = '追溯物料信息'
        verbose_name_plural = verbose_name
        db_table = 'sm_trace_material'


class TMInspectRecord(BaseModel):
    RESULT_CHOICE = (
        (0, "Fail"),
        (1, "Pass")
    )

    MODE_CHOICE = (
        (0, "无"),
        (1, "目视"),
        (2, "测量工具"),
        (3, "手动设备"),
        (4, "自动设备"))

    CATEGORY_CHOICE = (
        (0, "无"),
        (1, "外观"),
        (2, "功能"),
        (3, "性能"))

    trace_material = models.ForeignKey("TraceMaterial", on_delete=models.SET_NULL, null=True, blank=True, verbose_name='所属一般物料')
    num = models.CharField('检验项编号', max_length=20)
    name = models.CharField('检验项名称', max_length=20)
    category = models.SmallIntegerField('检验类型', choices=CATEGORY_CHOICE, default=0)
    mode = models.SmallIntegerField('检验方式', choices=MODE_CHOICE, default=0)
    result = models.SmallIntegerField('检验项结果', choices=RESULT_CHOICE, default=0)
    data = models.DecimalField('检验项数据', max_digits=10, decimal_places=2)
    operator = models.ForeignKey('account.User', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='检验员')
    upper = models.DecimalField('上限', max_digits=10, decimal_places=2)
    lower = models.DecimalField('下限', max_digits=10, decimal_places=2)

    def __str__(self):
        return self.num + ' ' + str(self.result) + ' ' + self.data

    class Meta:
        verbose_name = '追溯物料检测项'
        verbose_name_plural = verbose_name
        db_table = 'sm_tminspect_record'


