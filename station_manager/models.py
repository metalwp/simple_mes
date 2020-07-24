from django.db import models

# Create your models here.


class Station(models.Model):

    station_category_choice = (
                                (0, '无'),
                                (1, '来料检验（无VIN）'),
                                (2, '测试设备（无VIN）'),
                                (3, '测试设备'),
                                (4, '组装'),
                                (5, '过程检验'),
                                (6, '成品检验'),
                                (7, '入库'),)

    station_no = models.CharField('工站编号', max_length=32, null=True, blank=True, help_text="本行为系统自动创建")
    station_name = models.CharField('工站名称', max_length=100)
    station_category = models.PositiveSmallIntegerField('工位类型', choices=station_category_choice, default=0)
    c_time = models.DateTimeField('创建时间', auto_now_add=True)
    m_time = models.DateTimeField('修改时间', auto_now=True)
    remarks = models.CharField('备注', max_length=100, null=True, blank=True)

    class Meta:
        verbose_name = '工站信息'
        verbose_name_plural = '工站信息'

    def __str__(self):
        return self.station_no + ' ' + self.station_name

    # def save(self, *args, **kwargs):
    #     if self.pk:
    #         self.station_no = str(self.location.location_code) + '50' + str(self.id) + '/' + str(localtime)
    #     super(Station, self).save(*args, **kwargs)





