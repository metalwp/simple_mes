from django.db import models

from db.base_model import BaseModel

# Create your models here.


class Station(BaseModel):
    """工站"""
    STATION_CATEGORY_CHOICE = (
                                (0, '无'),
                                (1, '组装'),
                                (2, '测试'),
                                (3, '标定'),
                                (4, '检验'),
                                (5, '其他'))
    num = models.CharField('工站编号', unique=True, max_length=32)
    name = models.CharField('工站名称', max_length=100, unique=True)
    category = models.PositiveSmallIntegerField('工位类型', choices=STATION_CATEGORY_CHOICE, default=0)
    ip_address = models.GenericIPAddressField('IP地址', null=True, blank=True)
    remarks = models.CharField('备注', max_length=100, null=True, blank=True)

    class Meta:
        verbose_name = '工站信息'
        verbose_name_plural = '工站信息'
        db_table = 'sm_station'

    def __str__(self):
        return self.num + ' ' + self.name

    # def save(self, *args, **kwargs):
    #     if self.pk:
    #         self.station_no = str(self.location.location_code) + '50' + str(self.id) + '/' + str(localtime)
    #     super(Station, self).save(*args, **kwargs)


class Fixture(BaseModel):
    """工装信息"""
    station = models.ForeignKey("Station", on_delete=models.SET_NULL, null=True, blank=True, verbose_name="工站")
    num = models.CharField("工装编号", unique=True, max_length=20)
    name = models.CharField("工装名称", unique=True, max_length=20)
    remarks = models.CharField('备注', max_length=100, null=True, blank=True)

    class Meta:
        verbose_name = '工装'
        verbose_name_plural = '工装'
        db_table = 'sm_fixture'

    
    def __str__(self):
        return self.num + " " + self.name


class TestStandard(BaseModel):
    fixture = models.ForeignKey("Fixture", on_delete=models.SET_NULL, null=True, blank=True, verbose_name="工装")
    num = models.PositiveIntegerField("测试项编号")
    name =  models.CharField("测试项名称", max_length=20)
    upper = models.DecimalField("上限", max_digits=10, decimal_places=2)
    lower = models.DecimalField("下限", max_digits=10, decimal_places=2)
    version = models.CharField("版本", max_length=10)
    
    def __str__(self):
        return str(self.num) + " " + self.name

    class Meta:
        verbose_name = '测试标准'
        verbose_name_plural = '测试标准'
        db_table = 'sm_teststandard'
        unique_together = ( 'fixture', 'version', 'num')  # 联合约束



