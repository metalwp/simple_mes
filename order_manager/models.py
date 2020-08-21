from django.db import models
from product_manager.models import ProductModel

# Create your models here.

class Customer(models.Model):
    num = models.CharField('客户编号', max_length=20, unique=True)
    name = models.CharField('客户名称', max_length=100, unique=True)
    address = models.CharField("地址", max_length=100)
    contact = models.CharField("联系人", max_length=100)
    tel = models.CharField("电话", max_length=20)
    zip_code = models.CharField("邮编", max_length=20)
    email = models.EmailField("电子邮箱")
    remark = models.CharField('备注', max_length=200, null=True, blank=True) 
    c_time = models.DateTimeField('创建时间', auto_now_add=True)
    m_time = models.DateTimeField('修改时间', auto_now=True)

    def __str__(self):
        return self.num + " " + self.name
    
    class Meta:
        verbose_name = '客户'
        verbose_name_plural = '客户'

class Order(models.Model):
    order_status_choice = (
                            (0, '未开始'),
                            (1, '进行中'),
                            (2, '已完成'),
                            (3, '已挂起'),)

    num = models.CharField('订单编号', max_length=100, unique=True)
    status = models.SmallIntegerField('订单状态', choices=order_status_choice, default=0)
    product_model = models.ForeignKey(ProductModel, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='产品')
    quantity = models.SmallIntegerField('数量', default=1)
    delivery_time = models.DateField('交付时间')
    c_time = models.DateTimeField('创建时间', auto_now_add=True)
    start_time = models.DateTimeField('开始时间', null=True, blank=True)
    end_time = models.DateTimeField('结束时间', null=True, blank=True)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='客户')

    def __str__(self):
        return self.num + ' ' + self.product_model.name

    class Meta:
        verbose_name = '订单信息'
        verbose_name_plural = '订单信息'



