import datetime
import re

from django.shortcuts import render
from django.http import JsonResponse

from apps.order_manager.models import Order
from apps.process_manager.models import ProcessStep
from apps.manufacturing.models import Product, ProcessRecord, HistoryRecord, AssemblyRecord, TestRecord
from apps.Inspection.models import TraceMaterial

# Create your views here.


def index(request, sequence_no):
    try:
        order = Order.objects.get(status=1)
    except (Order.DoesNotExist, Order.MultipleObjectsReturned):
        return {'steps': []}
    route = order.product_model.process_route
    step = ProcessStep.objects.filter_without_isdelete().get(process_route=route, sequence_no=sequence_no)
    if step.category == 1:  # 组装
        return render(request, 'manufacturing/assemble_index.html', locals())
    elif step.category == 3:  # 标定
        return render(request, 'manufacturing/assemble_index.html', locals())
    elif step.category == 4:  # 检验
        return render(request, 'manufacturing/assemble_index.html', locals())
    elif step.category == 5:  # 标签打印
        return render(request, 'manufacturing/assemble_index.html', locals())
    elif step.category == 6:  # VIN生成
        return render(request, 'manufacturing/vin_index.html', locals())
    else:  # 其他
        return render(request, 'manufacturing/assemble_index.html', locals())


def getOrderInfo(request, sequence_no):
    if request.method == "POST":
        info = {}
        rows = []
        vin = request.POST.get('snInput')
        if vin:
            if len(vin) == 18:
                if not re.match(r'^IDP[A-Z]{3}\d{6}[1-9,A-Z][1-9,A-C]\d{4}$', vin):
                    return JsonResponse({"ret": False, "errMsg": 'VIN格式不正确！', "rows": [], "total": 0})
                try:
                    product = Product.objects.get(vin=vin)
                except Product.DoesNotExist:
                    product = None
                if product:
                    info['product_vin'] = vin
                else:
                    info['product_vin'] = ''

            if len(vin) == 24:
                sn = vin
                pass
        try:
            order = Order.objects.get(status=1)
        except (Order.DoesNotExist, Order.MultipleObjectsReturned):
            errMsg = '无打开订单或打开订单超过1个！'
            return render(request, 'manufacturing/vin_index.html', locals())

        product_model = order.product_model
        info['product_erp'] = product_model.erp_no
        info['product_name'] = product_model.name
        info['product_model'] = product_model.model
        info['order_num'] = order.num
        info['order_quantity'] = order.quantity

        products = Product.objects.filter_without_isdelete().filter(order_num=order.num)
        info['finish_quantity'] = products.count()
        info['finish_rate'] = '{:.2%}'.format(products.count()/order.quantity)
        info['user'] = 'user'
        info['date'] = order.c_time

        data = {"ret": True, "errMsg": "", "total": 0, "rows": rows, 'info': info}

        return JsonResponse(data)


def getProductInfo(request, sequence_no):
    if request.method == "GET":
        info = {}
        rows = []
        try:
            order = Order.objects.get(status=1)
        except (Order.DoesNotExist, Order.MultipleObjectsReturned):
            errMsg = '无打开订单或打开订单超过1个！'
            return render(request, 'manufacturing/vin_index.html', locals())

        product_model = order.product_model
        products = Product.objects.filter_without_isdelete().filter(order_num=order.num)

        data = {"ret": True, "errMsg": "", "total": 0, "rows": rows}
        if not products:
            return JsonResponse(data)
        else:
            for product in products:
                rows.append({'id': product.id,
                             'vin': product.vin,
                             'order_num': order.num,
                             'erp_no': product_model.erp_no,
                             'name': product_model.name,
                             'model': product_model.model,
                             })
            return JsonResponse(data)


def generateVIN(request, sequence_no):
    if request.method == "POST":
        info = {}
        try:
            order = Order.objects.get(status=1)
        except (Order.DoesNotExist, Order.MultipleObjectsReturned):
            errMsg = '无打开订单或打开订单超过1个！'
            return render(request, 'manufacturing/vin_index.html', locals())
        products = Product.objects.filter_without_isdelete().filter(order_num=order.num)
        if products.count() < order.quantity:
            vin = get_vin(order)
            if not vin:
                return_dict = {"ret": False, "errMsg": 'VIN获取失败！', "rows": [], "total": 0}
                return JsonResponse(return_dict)
            product = Product.objects.create(order_num=order, vin=vin)

            ProcessRecord.objects.create(product=product, sequence_no=sequence_no, result=1)
            info['vin'] = vin
            return_dict = {"ret": True, "errMsg": '', "rows": [], "total": 0, 'info': info}
            return JsonResponse(return_dict)
        else:
            return_dict = {"ret": False, "errMsg": '该订单VIN已经全部生成', "rows": [], "total": 0}
            return JsonResponse(return_dict)


def get_vin(order):
    year = datetime.datetime.now().year
    month = datetime.datetime.now().month
    year_str = None
    month_str = None
    YEARS = ['1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L',
             'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
    MONTHS = ['1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C']
    for i, y in zip(range(2011, 2090), YEARS):  # zip会按最短的进行绑定
        if year == i:
            year_str = y
            break
    for j, m in zip(range(1, 13), MONTHS):  # zip会按最短的进行绑定
        if month == j:
            month_str = m
            break
    if (year_str is None) or (month_str is None):
        return False

    str1 = order.product_model.model[0:3]
    str2 = order.product_model.erp_no[11:13]
    vin_start = 'IDP' + str1 + '20' + '20' + str2 + year_str + month_str

    product = Product.objects.filter_without_isdelete().filter(vin__startswith=vin_start).order_by('-c_time').first()
    if product:
        serial_number = int(product.vin[-4:]) + 1
    else:
        serial_number = 1
    vin = vin_start + "{0:04d}".format(serial_number)
    return vin


def getAssembleRecord(request, sequence_no):
    if request.method == "GET":
        vin = request.GET.get('vin')
        if not vin:
            return_dict = {"ret": False, "errMsg": 'VIN不能为空！', "rows": [], "total": 0}
            return JsonResponse(return_dict)
        else:
            product = Product.objects.get(vin=vin)
            try:
                process_record = ProcessRecord.objects.get(product=product, sequence_no=sequence_no)
            except ProcessRecord.DoesNotExist:
                process_record = None
            rows = []
            data = {"ret": True, "errMsg": "", "total": 0, "rows": rows, 'info': {}}
            if process_record:
                assembly_records = AssemblyRecord.objects.filter(process_record=process_record)

                if assembly_records:
                    for r in assembly_records:
                        m = TraceMaterial.objects.get(sn=r.sn)
                        rows.append({'id': r.id,
                                     'sn': r.sn,
                                     'batch_num': m.batch_num,
                                     'erp_no': r.material_model.erp_no,
                                     'name': r.material_model.name,
                                     'model': r.material_model.model,
                                     'category': r.material_model.category,
                                     })
            return JsonResponse(data)