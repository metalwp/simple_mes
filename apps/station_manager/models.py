from django.db import models

from db.base_model import BaseModel

# Create your models here.


class Station(BaseModel):
    """工站"""
    station_category_choice = (
                                (0, '无'),
                                (1, '组装'),
                                (2, '测试'),
                                (3, '标定'),
                                (4, '检验'),
                                (5, '其他'))
    num = models.CharField('工站编号', max_length=32, primary_key=True, unique=True)
    name = models.CharField('工站名称', max_length=100, unique=True)
    category = models.PositiveSmallIntegerField('工位类型', choices=station_category_choice, default=0)
    ip_address = models.GenericIPAddressField('IP地址', null=True, blank=True)
    remarks = models.CharField('备注', max_length=100, null=True, blank=True)

    class Meta:
        verbose_name = '工站信息'
        verbose_name_plural = '工站信息'

    def __str__(self):
        return self.num + ' ' + self.name

    # def save(self, *args, **kwargs):
    #     if self.pk:
    #         self.station_no = str(self.location.location_code) + '50' + str(self.id) + '/' + str(localtime)
    #     super(Station, self).save(*args, **kwargs)


class Fixture(BaseModel):
    """工装信息"""
    station = models.ForeignKey("Station", on_delete=models.SET_NULL, null=True, blank=True, verbose_name="工站")
    num = models.CharField("工装编号", max_length=20, primary_key=True, unique=True)
    name = models.CharField("工装名称", max_length=20, unique=True)
    remarks = models.CharField('备注', max_length=100, null=True, blank=True)

    class Meta:
        # db_table = ''
        # managed = True
        verbose_name = '工装'
        verbose_name_plural = '工装'
    
    def __str__(self):
        return self.num + " " + self.name


class TestStandard(BaseModel):
    fixture = models.ForeignKey("Fixture", on_delete=models.SET_NULL, null=True, blank=True, verbose_name="工装")
    num = models.PositiveIntegerField("测试项编号")
    name =  models.CharField("测试项名称", max_length=20, unique=True)
    upper = models.DecimalField("上限", max_digits=10, decimal_places=2)
    lower = models.DecimalField("下限", max_digits=10, decimal_places=2)
    version = models.CharField("版本", max_length=10)
    
    def __str__(self):
        return self.num + " " + self.name

    class Meta:
        verbose_name = '测试标准'
        verbose_name_plural = '测试标准'
        unique_together = ('fixture', 'version', 'num')  # 联合约束



