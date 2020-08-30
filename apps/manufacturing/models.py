from django.db import models

from db.base_model import BaseModel


# Create your models here.

class Product(BaseModel):
    vin = models.CharField('VIN', max_length=30, help_text="本行为系统自动创建")
    order_num = models.ForeignKey('order_manager.Order', on_delete=models.SET_NULL, blank=True, null=True, verbose_name='订单')

    def __str__(self):
        return self.vin

    class Meta:
        verbose_name = '产品记录'
        verbose_name_plural = '产品记录'
        db_table = 'sm_product'
        unique_together = ('is_delete', "vin")


class ProcessRecord(BaseModel):
    result_choice = ((0, 'Fail'), (1, 'Pass'))
    product = models.ForeignKey('Product', on_delete=models.SET_NULL, blank=True, null=True, verbose_name='对应产品')
    sequence_no = models.SmallIntegerField('工序顺序号')
    result = models.SmallIntegerField('结果', choices=result_choice, null=True, blank=True, default=None)

    def __str__(self):
        return self.product.vin + ' ' + str(self.sequence_no) + ' ' + str(self.result)

    class Meta:
        verbose_name = '产品过程记录'
        verbose_name_plural = '产品过程记录'
        db_table = 'sm_process_record'


class AssemblyRecord(BaseModel):
    sn = models.CharField('SN', max_length=30)
    process_record = models.ForeignKey("ProcessRecord", on_delete=models.SET_NULL, blank=True, null=True, verbose_name='所属工序')

    def __str__(self):
        return self.sn

    class Meta:
        verbose_name = '装配记录'
        verbose_name_plural = '装配记录'
        db_table = 'sm_assembly_record'
        unique_together = ('is_delete', "sn")


class TestRecord(BaseModel):
    result_choice = ((0, 'Fail'), (1, 'Pass'))
    process_record = models.ForeignKey("ProcessRecord", on_delete=models.SET_NULL, blank=True, null=True, verbose_name='产品过程记录')
    num = models.SmallIntegerField('测试项编号')

    name = models.CharField('测试项名称', max_length=100)
    result = models.SmallIntegerField('测试项结果', choices=result_choice)

    data = models.DecimalField('测试项数据', max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name + ' ' + str(self.result)

    class Meta:
        verbose_name = '测试项记录'
        verbose_name_plural = '测试项记录'
        db_table = 'sm_test_record'


        