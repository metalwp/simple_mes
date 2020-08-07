import datetime
import time

from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, View
from django.views import View

from product_manager.models import ProductModel
from .models import Order
# Create your views here.


def index(request):
    orders = Order.objects.all()
    status_choice = Order.order_status_choice
    products = ProductModel.objects.all()
    return render(request, 'order_manager/index.html', locals())


def getOrderData(request):
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
            orders = Order.objects.order_by(sort_str)[(pageNumber - 1) * pageSize:(pageNumber) * pageSize]
        else:
            orders = Order.objects.filter(Q(product_model__product_name__contains=search_kw)).order_by(sort_str) \
                        [(pageNumber - 1) * pageSize: pageNumber * pageSize]
            # 获取查询结果的总条数
            total = Order.objects.filter(Q(product_model__product_name__contains=search_kw)).order_by(sort_str) \
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
            rows.append({'id': order.id, 'order_no': order.order_no, 'erp_no': order.product_model.erp_no,
                         'name': order.product_model.product_name, 'model': order.product_model.model_name,
                         'quantity': order.quantity, 'delivery_time': order.delivery_time,
                         'order_status': order.order_status, 'start_time': start_time, 'end_time': end_time})
        return JsonResponse(data)


def deleteOrderData(request):
    return_dict = {"ret": True, "errMsg": "", "rows": [], "total": 0}
    id = request.POST.get('id')
    order = Order.objects.get(id=id)
    order.delete()
    return JsonResponse(return_dict)


def addOrderData(request):
    if request.method == "POST":
        order_no = request.POST.get('orderNoInput')
        product_id = request.POST.get('productSelect')
        product = ProductModel.objects.get(id=product_id)
        quantity = request.POST.get('quantityInput')
        dilivery_str = request.POST.get('diliveryInput')
        dilivery_time = datetime.datetime.strptime(dilivery_str, '%Y-%m-%d').date()
        try:
            Order.objects.create(order_no=order_no, product_model=product, quantity=quantity, delivery_time=dilivery_time)
        except Exception as e:
            return_dict = {"ret": False, "errMsg": str(e), "rows": [], "total": 0}
            return JsonResponse(return_dict)

        return_dict = {"ret": True, "errMsg": "", "rows": [], "total": 0}
        return JsonResponse(return_dict)


def updateOrderData(request):
    if request.method == 'POST':
        id = request.POST.get('idUpdateInput')
        # order_no = request.POST.get('orderNoUpdateInput')
        product_id = request.POST.get('productUpdateSelect')
        product = ProductModel.objects.get(id=product_id)
        quantity = request.POST.get('quantityUpdateInput')
        status = request.POST.get('statusUpdateSelect')

        try:
            dilivery_time = None
            dilivery_str = request.POST.get('diliveryUpdateInput')
            if dilivery_str:
                dilivery_time = datetime.datetime.strptime(dilivery_str, '%Y-%m-%d').date()

            start_time = None
            start_str = request.POST.get('startUpdateInput')
            if start_str:
                start_time = datetime.datetime.strptime(start_str, '%Y-%m-%d-%H:%M:%S')

            end_time = None
            end_str = request.POST.get('endUpdateInput')
            if end_str:
                end_time = datetime.datetime.strptime(end_str, '%Y-%m-%d-%H:%M:%S')
            mat, created = Order.objects.update_or_create(id=id, defaults={"order_status": status,
                                                                           "product_model": product, "quantity": quantity,
                                                                           "delivery_time": dilivery_time, "start_time": start_time,
                                                                           "end_time": end_time})
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
    order = Order.objects.filter(order_no__contains="J" + date_str).order_by("-c_time").first()

    if order:
        serial_number = int(order.order_no[9:]) + 1
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
