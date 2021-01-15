from django.db import models

from db.base_model import BaseModel


# Create your models here.


class ProductCategory(BaseModel):
    name = models.CharField('分类名称', unique=True, max_length=30)  # unique=True
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True, null=True, verbose_name='父类')

    class Meta:
        db_table = 'sm_product_category'
        verbose_name = '产品分类'
        verbose_name_plural = '产品分类'

    def __str__(self):
        return self.name


class VinRule(BaseModel):
    name = models.CharField('Vin规则名称', max_length=30)

    class Meta:
        verbose_name = 'Vin规则'
        verbose_name_plural = 'Vin规则'
        db_table = 'sm_vinRule'

    def __str__(self):
        return self.name


class VinRuleItem(BaseModel):
    RULE_CHOICE = (
        (0, '无'),
        (1, "日期2位YM"),
        (2, "日期5位YYMDD"),
        (3, "产品总成ERP版本V后2位"),
        (4, "流水号"),
    )

    sequence_no = models.SmallIntegerField('vin顺序号')
    digit_num = models.SmallIntegerField('位数')
    rule = models.SmallIntegerField('规则选项', choices=RULE_CHOICE, default=0)
    content = models.CharField('内容', max_length=200, null=True, blank=True, default=None)
    vin_rule = models.ForeignKey('VinRule', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="vin规则")
    remark = models.CharField('备注', max_length=200, null=True, blank=True)

    class Meta:
        verbose_name = 'Vin规则项'
        verbose_name_plural = 'Vin规则项'
        db_table = 'sm_vinRuleItem'

    def __str__(self):
        return self.content


class ProductModel(BaseModel):
    name = models.CharField('产品名称', max_length=30)
    model = models.CharField('产品型号', max_length=30)
    category = models.ForeignKey("ProductCategory", on_delete=models.SET_NULL, blank=True, null=True, verbose_name='产品分类')

    process_route = models.ForeignKey('process_manager.ProcessRoute', on_delete=models.SET_NULL, blank=True, null=True, verbose_name='工艺路线')
    vin_rule = models.OneToOneField('VinRule', related_name='product_model', on_delete=models.SET_NULL, blank=True, null=True, verbose_name='VIN规则')

    class Meta:
        verbose_name = '产品配置'
        verbose_name_plural = '产品配置'
        db_table = 'sm_product_model'

    def __str__(self):
        return self.name










