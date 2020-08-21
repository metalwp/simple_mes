from django.db import models

# Create your models here.


class Station(models.Model):
    """工站"""
    station_category_choice = (
                                (0, '无'),
                                (1, '组装'),
                                (2, '测试'),
                                (3, '标定'),
                                (4, '检验'),
                                (5, '其他'))
    num = models.CharField('工站编号', max_length=32, null=True, blank=True, help_text="本行为系统自动创建")
    name = models.CharField('工站名称', max_length=100)
    category = models.PositiveSmallIntegerField('工位类型', choices=station_category_choice, default=0)
    c_time = models.DateTimeField('创建时间', auto_now_add=True)
    m_time = models.DateTimeField('修改时间', auto_now=True)
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


class Fixture(models.Model):
    """工装信息"""
    station = models.ForeignKey(Station, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="工站")
    num = models.CharField("工装编号", max_length=20, unique=True)
    name = models.CharField("工装名称", max_length=20, unique=True)
    c_time = models.DateTimeField("创建时间", auto_now_add=True)
    m_time = models.DateTimeField('修改时间', auto_now=True)
    remarks = models.CharField('备注', max_length=100, null=True, blank=True)

    class Meta:
        # db_table = ''
        # managed = True
        verbose_name = '工装'
        verbose_name_plural = '工装'
    
    def __str__(self):
        return self.num + " " + self.name


class TestStandard(models.Model):
    fixture = models.ForeignKey(Fixture, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="工装")
    num = models.PositiveIntegerField("测试项编号")
    name =  models.CharField("测试项名称", max_length=20, unique=True)
    upper = models.FloatField("上限")
    lower = models.FloatField("下限")
    version = models.CharField("版本", max_length=10)
    c_time = models.DateTimeField("创建时间", auto_now_add=True)
    m_time = models.DateTimeField('修改时间', auto_now=True)
    
    def __str__(self):
        return self.num + " " + self.name

    class Meta:
        verbose_name = '测试标准'
        verbose_name_plural = '测试标准'
        unique_together = ('fixture', 'version', 'num')  # 联合约束



