from django.db import models

from db.base_model import BaseModel


# Create your models here.

class Product(BaseModel):
    vin = models.CharField('VIN', max_length=30, unique=True, help_text="本行为系统自动创建")
    order_num = models.ForeignKey('order_manager.Order', on_delete=models.SET_NULL, blank=True, null=True, verbose_name='订单')

    def __str__(self):
        return self.vin

    class Meta:
        verbose_name = '产品记录'
        verbose_name_plural = '产品记录'
        db_table = 'sm_product'


class ProcessRecord(BaseModel):
    RESULT_CHOICE = ((0, 'Fail'), (1, 'Pass'))
    product = models.ForeignKey('Product', on_delete=models.SET_NULL, blank=True, null=True, verbose_name='对应产品')
    sequence_no = models.SmallIntegerField('工序顺序号')
    result = models.SmallIntegerField('结果', choices=RESULT_CHOICE, null=True, blank=True, default=None)

    def __str__(self):
        return self.product.vin + ' ' + str(self.sequence_no) + ' ' + str(self.result)

    class Meta:
        verbose_name = '产品过程记录'
        verbose_name_plural = '产品过程记录'
        db_table = 'sm_process_record'

    
class HistoryRecord(BaseModel):
    sn = models.CharField('SN',  max_length=30)
    process_record = models.ForeignKey("ProcessRecord", on_delete=models.SET_NULL, blank=True, null=True, verbose_name='所属工序')
    material_model = models.ForeignKey('bom_manager.MaterialModel', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='物料型号')

    def __str__(self):
        return self.sn

    class Meta:
        verbose_name = '历史装配记录'
        verbose_name_plural = '历史装配记录'
        db_table = 'sm_history_record'


class AssemblyRecord(BaseModel):
    sn = models.CharField('SN', null=True, max_length=30)
    process_record = models.ForeignKey("ProcessRecord", on_delete=models.SET_NULL, blank=True, null=True, verbose_name='所属工序')
    material_model = models.ForeignKey('bom_manager.MaterialModel', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='物料型号')
    
    def __str__(self):
        return self.sn

    class Meta:
        verbose_name = '装配记录'
        verbose_name_plural = '装配记录'
        db_table = 'sm_assembly_record'


class TestRecord(BaseModel):
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

    process_record = models.ForeignKey("ProcessRecord", on_delete=models.SET_NULL, blank=True, null=True, verbose_name='产品过程记录')
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
        return self.name + ' ' + str(self.result)

    class Meta:
        verbose_name = '测试项记录'
        verbose_name_plural = '测试项记录'
        db_table = 'sm_test_record'


class RepairRecord(BaseModel):
    CATEGORY_CHOICE = (
        (0, "追溯物料返修"),
        (1, "非追溯物料返修")
    )
    product = models.ForeignKey('Product', on_delete=models.SET_NULL, blank=True, null=True, verbose_name='对应产品')
    category = models.SmallIntegerField('返修类型', choices=CATEGORY_CHOICE, default=0)
    origin_sn = models.CharField('原SN', null=True, blank=True, max_length=30)
    new_sn = models.CharField('新SN', null=True, blank=True, max_length=30)
    record = models.TextField('返修记录', blank=True, null=True, max_length=1000)
    material_model = models.ForeignKey('bom_manager.MaterialModel', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='物料型号')

    def __str__(self):
        return self.origin_sn + ' ' + self.new_sn

    class Meta:
        verbose_name = '返修记录'
        verbose_name_plural = '返修记录'
        db_table = 'sm_repair_record'

