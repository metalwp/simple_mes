import datetime
import time
import re

from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, View
from django.views import View

from apps.product_manager.models import ProductModel
from .models import Order, Customer
# Create your views here.


def cm_index(request):
    customers = Customer.objects.filter_without_isdelete()
    return render(request, 'order_manager/cm_index.html', locals())


def getCustomerData(request):
    model = Customer
    # 获取前端数据
    if request.method == 'GET':
        pageSize = int(request.GET.get('pageSize'))
        pageNumber = int(request.GET.get('pageNumber'))
        sortName = request.GET.get('sortName')
        sortOrder = request.GET.get('sortOrder')
        search_kw = request.GET.get('search_kw')

        #数据校验、业务逻辑
        if sortOrder == 'asc':
            sort_str = sortName
        else:
            sort_str = '-' + sortName
        if not search_kw:
            total = model.objects.filter_without_isdelete().count()
            objs = model.objects.filter_without_isdelete().order_by(sort_str)[(pageNumber - 1) * pageSize:(pageNumber) * pageSize]
        else:
            objs = model.objects.filter_without_isdelete().filter(Q(name__contains=search_kw)).order_by(sort_str) \
                        [(pageNumber - 1) * pageSize: pageNumber * pageSize]
            # 获取查询结果的总条数
            total = model.objects.filter_without_isdelete().filter(Q(name__contains=search_kw)).order_by(sort_str) \
                        [(pageNumber - 1) * pageSize: pageNumber * pageSize].count()
        rows = []
        data = {"total": total, "rows": rows}

        for obj in objs:
            rows.append({'num': obj.num, 'name': obj.name, 'address': obj.address,
                         'contact': obj.contact, 'tel': obj.tel,
                         'zip_code': obj.zip_code, 'email': obj.email,
                         'remark': obj.remark})
        return JsonResponse(data)


def addCustomerData(request):
        model = Customer
        if request.method == "POST":
            # 获取前端数据
            name = request.POST.get('nameInput')
            address = request.POST.get('addressInput')
            contact = request.POST.get('contactInput')
            tel = request.POST.get('telInput')
            zip_code = request.POST.get('zipCodeInput')
            email = request.POST.get('emailInput')
            remark = request.POST.get('remarkText')

            # 数据校验
            if not all([name, address, contact, tel, zip_code, email]):
                return JsonResponse({"ret": False, "errMsg": '数据不能为空！', "rows": [], "total": 0})
            # 校验邮箱格式
            if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
                return JsonResponse({"ret": False, "errMsg": '邮箱格式不正确！', "rows": [], "total": 0})

            # 业务逻辑    
            try:
                model.objects.create(name=name, address=address, contact=contact, tel=tel, zip_code=zip_code, email=email, remark=remark)
            except Exception as e:
                print(str(e))
                return_dict = {"ret": False, "errMsg": str(e), "rows": [], "total": 0}
                return JsonResponse(return_dict)

            return_dict = {"ret": True, "errMsg": "", "rows": [], "total": 0}
            #返回响应
            return JsonResponse(return_dict)


def deleteCustomerData(request):
        model = Customer 
        return_dict = {"ret": True, "errMsg": "", "rows": [], "total": 0}
        num = request.POST.get('id')
        obj = model.objects.get(num=num)
        obj.delete()
        return JsonResponse(return_dict)


def updateCustomerData(request):
    model = Customer
    if request.method == 'POST':
        print(request.POST)
        num = request.POST.get('u_numInput')

        name = request.POST.get('u_nameInput')
        address = request.POST.get('u_addressInput')
        contact = request.POST.get('u_contactInput')
        tel = request.POST.get('u_telInput')
        zip_code = request.POST.get('u_zipCodeInput')
        email = request.POST.get('u_emailInput')
        remark = request.POST.get('u_remarkText')

        # 数据校验
        if not all([name, address, contact, tel, zip_code, email]):
            return JsonResponse({"ret": False, "errMsg": '数据不能为空！', "rows": [], "total": 0})
        # 校验邮箱格式
        if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return JsonResponse({"ret": False, "errMsg": '邮箱格式不正确！', "rows": [], "total": 0})

        try:
            mat, created = model.objects.update_or_create(num=num, defaults={"name": name,
                                                                        "address": address, "contact": contact,
                                                                        "tel": tel, "zip_code": zip_code,
                                                                        "email": email, 'remark': remark})
        except Exception as e:
            return_dict = {"ret": False, "errMsg": str(e), "rows": [], "total": 0}
            return JsonResponse(return_dict)

        return_dict = {"ret": True, "errMsg": '', "rows": [], "total": 0}
        return JsonResponse(return_dict)


def om_index(request):
    orders = Order.objects.filter_without_isdelete()
    status_choice = Order.order_status_choice
    products = ProductModel.objects.filter_without_isdelete()
    customers = Customer.objects.filter_without_isdelete()
    return render(request, 'order_manager/om_index.html', locals())


def getOrderData(request):
    #获取订单数据视图
    if request.method == 'GET':
        pageSize = int(request.GET.get('pageSize'))
        pageNumber = int(request.GET.get('pageNumber'))
        sortName = request.GET.get('sortName')
        sortOrder = request.GET.get('sortOrder')
        search_kw = request.GET.get('search_kw')
        if sortOrder == 'asc':
            sort_str = sortName
        else:
            sort_str = '-' + sortName
        if not search_kw:
            total = Order.objects.all().count()
            orders = Order.objects.filter_without_isdelete().order_by(sort_str)[(pageNumber - 1) * pageSize:(pageNumber) * pageSize]
        else:
            orders = Order.objects.filter_without_isdelete().filter(Q(product_model__name__contains=search_kw)).order_by(sort_str) \
                        [(pageNumber - 1) * pageSize: pageNumber * pageSize]
            # 获取查询结果的总条数
            total = Order.objects.filter_without_isdelete().filter(Q(product_model__name__contains=search_kw)).order_by(sort_str) \
                        [(pageNumber - 1) * pageSize: pageNumber * pageSize].count()
        rows = []
        data = {"total": total, "rows": rows}
        for order in orders:
            if order.start_time:
                start_time = order.start_time.strftime("%Y-%m-%d-%H:%M:%S")
            else:
                start_time = ''
            if order.end_time:
                end_time = order.end_time.strftime("%Y-%m-%d-%H:%M:%S")
            else:
                end_time = ''
            rows.append({'num': order.num, 
                                        'erp_no': order.product_model.erp_no,
                                        'name': order.product_model.name, 
                                        'model': order.product_model.model,
                                        'quantity': order.quantity, 
                                        'delivery_time': order.delivery_time,
                                        'order_status': order.status, 
                                        'start_time': start_time, 
                                        'end_time': end_time,
                                        'customer': order.customer.name})
        return JsonResponse(data)


def deleteOrderData(request):
    return_dict = {"ret": True, "errMsg": "", "rows": [], "total": 0}
    id = request.POST.get('id')
    order = Order.objects.get(num=id)
    order.delete()
    return JsonResponse(return_dict)


def addOrderData(request):
    if request.method == "POST":
        # 获取前端数据
        num = request.POST.get('numInput')
        product_id = request.POST.get('productSelect')
        quantity = request.POST.get('quantityInput')
        dilivery_str = request.POST.get('diliveryInput')
        customer_num = request.POST.get('customerSelect')

        # 数据校验
        if not all([num, product_id, quantity, dilivery_str, customer_num]):
            return JsonResponse({"ret": False, "errMsg": '数据不能为空！', "rows": [], "total": 0})
        
        try:
            # 业务逻辑
            dilivery_time = datetime.datetime.strptime(dilivery_str, '%Y-%m-%d').date()
            product = ProductModel.objects.get(id=product_id)
            customer = Customer.objects.get(num=customer_num)
            Order.objects.create(num=num, product_model=product, quantity=quantity, delivery_time=dilivery_time, customer=customer)
        except Exception as e:
            return_dict = {"ret": False, "errMsg": str(e), "rows": [], "total": 0}
            return JsonResponse(return_dict)

        return_dict = {"ret": True, "errMsg": "", "rows": [], "total": 0}
        return JsonResponse(return_dict)


def updateOrderData(request):
    if request.method == 'POST':
        num = request.POST.get('u_numInput')
        product_id = request.POST.get('u_productSelect')
        quantity = request.POST.get('u_quantityInput')
        dilivery_str = request.POST.get('u_diliveryInput')
        customer_num = request.POST.get('u_customerSelect')
        status = request.POST.get('u_statusSelect')
        print(request.POST)

        if not all([num, product_id, quantity, dilivery_str, customer_num, status]):
            return JsonResponse({"ret": False, "errMsg": '数据不能为空！', "rows": [], "total": 0})

        try:
            product = ProductModel.objects.get(id=product_id)
            customer = Customer.objects.get(num=customer_num)
            dilivery_time = datetime.datetime.strptime(dilivery_str, '%Y-%m-%d').date()
            mat, created = Order.objects.update_or_create(num=num, defaults={"product_model": product,
                                                                           "quantity": quantity, "delivery_time": dilivery_time,
                                                                           "customer": customer , 'status':status})
        except Exception as e:
            return_dict = {"ret": False, "errMsg": str(e), "rows": [], "total": 0}
            return JsonResponse(return_dict)

    return_dict = {"ret": True, "errMsg": '', "rows": [], "total": 0}
    return JsonResponse(return_dict)


class GetOrderNum(View):

    # def __init__(self):
    #     super().__init__()

    def get(self, request):
        return_dict = {"ret": True, "errMsg": '', "rows": [], "total": 0, "order_num": genOrderNum()}
        return JsonResponse(return_dict)


def genOrderNum():
    """生成订单号"""
    date_str = time.strftime("%Y%m%d", time.localtime(time.time()))
    order = Order.objects.filter(num__contains="J" + date_str).order_by("-c_time").first()

    if order:
        serial_number = int(order.num[9:]) + 1
    else:
        serial_number = 1
    order_number = "J" + date_str + "{0:03d}".format(serial_number)  # J20190612001
    return order_number


class AutoSerialNumber(object):
    """创建OA单号"""

    def __init__(self):
        # J201906120001
        self.fd_apply_no = ''
        self.order = Order.objects.filter(order_no__contains="J").order_by("-order_no").first()
        if self.order:
            self.fd_apply_no = self.order.order_no
            #self.fd_apply_no = "J20190612001"
            self.date_str = self.fd_apply_no[1: 9]  # 日期字符串
            self._serial_number = self.fd_apply_no[9:]  # 流水号字符串
            self._serial_number = 0  # 流水号
        else:
            self.timed_clear_serial_number()
            

    @property
    def serial_number(self):
        return self._serial_number

    @serial_number.setter
    def serial_number(self, value):
        if isinstance(value, int):
            self._serial_number = value
        else:
            self._serial_number = 1

    def __iter__(self):
        return self

    def __next__(self):
        self.serial_number += 1
        # 生成一个固定4位数的流水号
        return "{0:03d}".format(self.serial_number)

    def __call__(self, *args, **kwargs):
        # 返回生成序列号(日期加流水号)
        return "J" + self.date_str + next(self)

    # 时间格式化,最好是用定时器来调用该方法
    def timed_clear_serial_number(self):
        """用于每天定时清除流水号"""

        self.serial_number = 1
        self.date_str = time.strftime("%Y%m%d", time.localtime(time.time()))
