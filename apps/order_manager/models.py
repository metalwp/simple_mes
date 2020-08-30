import time

from django.db import models

from db.base_model import BaseModel, MyManager

# Create your models here.


class CustomerManager(MyManager):
    # 新建客户时不会

    def create(self, **kwargs):
        print(kwargs)
        kwargs['num'] = self.gen_cumtomer_num()
        return super(CustomerManager, self).create(**kwargs)
        # # 默认创建一个熊猫
        # '''改写创建对象语句,使用子类完成操作'''
        # animal = self.model()
        # # 创建一个模型
        # animal.a_name = a_name
        # return animal

    @staticmethod
    def gen_cumtomer_num():
        """生成订单号"""
        date_str = time.strftime("%Y%m%d", time.localtime(time.time()))
        customer = Customer.objects.filter(num__contains="CUST" + date_str).order_by("-c_time").first()

        if customer:
            serial_number = int(customer.num[11:]) + 1 #CUST20200830002
        else:
            serial_number = 1
        customer_number = "CUST" + date_str + "{0:03d}".format(serial_number)  # CUST20200830002
        return customer_number


class Customer(BaseModel):
    num = models.CharField('客户编号', primary_key=True, max_length=20)
    name = models.CharField('客户名称', max_length=100)
    address = models.CharField("地址", max_length=100)
    contact = models.CharField("联系人", max_length=100)
    tel = models.CharField("电话", max_length=20)
    zip_code = models.CharField("邮编", max_length=20)
    email = models.EmailField("电子邮箱")
    remark = models.CharField('备注', max_length=200, null=True, blank=True)

    #  Customer的自定义管理器
    objects = CustomerManager()

    def __str__(self):
        return self.num + " " + self.name
    
    class Meta:
        verbose_name = '客户信息'
        verbose_name_plural = '客户信息'
        db_table = 'sm_customer'
        unique_together = (('is_delete', "num"), ('is_delete', "name"))


class Order(BaseModel):
    order_status_choice = (
                            (0, '未开始'),
                            (1, '进行中'),
                            (2, '已完成'),
                            (3, '已挂起'),)

    num = models.CharField('订单编号', primary_key=True, max_length=100, unique=True)
    status = models.SmallIntegerField('订单状态', choices=order_status_choice, default=0)
    product_model = models.ForeignKey("product_manager.ProductModel", on_delete=models.SET_NULL, blank=True, null=True, verbose_name='产品')
    quantity = models.SmallIntegerField('数量', default=1)
    delivery_time = models.DateField('交付时间')
    start_time = models.DateTimeField('开始时间', null=True, blank=True)
    end_time = models.DateTimeField('结束时间', null=True, blank=True)
    customer = models.ForeignKey("Customer", on_delete=models.SET_NULL, null=True, blank=True, verbose_name='客户')

    def __str__(self):
        return self.num + ' ' + self.product_model.name

    class Meta:
        verbose_name = '订单信息'
        verbose_name_plural = '订单信息'
        db_table = 'sm_order'
        unique_together = ('is_delete', "num")



