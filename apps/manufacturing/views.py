import datetime
import re
import json

from django.shortcuts import render, redirect, reverse
from django.http import JsonResponse, HttpResponse

from apps.order_manager.models import Order
from apps.process_manager.models import ProcessStep, ProcessStep_MaterialModel
from apps.manufacturing.models import Product, ProcessRecord, HistoryRecord, AssemblyRecord, TestRecord
from apps.Inspection.models import TraceMaterial, Inspection
from apps.bom_manager.models import MaterialModel, BOM
from apps.product_manager.models import VinRule, VinRuleItem

# Create your views here.


def index(request, step_id):
    if request.method == "GET":
        try:
            order = Order.objects.filter_without_isdelete().get(status=1)
            categorys = MaterialModel.CATEGORY_CHOICE
            inspection_categorys = Inspection.CATEGORY_CHOICE
            inspection_modes = Inspection.MODE_CHOICE
            step = ProcessStep.objects.filter_without_isdelete().get(id=step_id)
        except Exception as e:
            return HttpResponse(str(e))
        route = order.product_model.process_route
        # step = ProcessStep.objects.filter_without_isdelete().get(process_route=route, sequence_no=sequence_no)
        # step = ProcessStep.objects.filter_without_isdelete().get(id=step_id)

        user = request.user
        print(step.category)
        if user.is_authenticated:
            if step.category == 1:  # 组装
                return render(request, 'manufacturing/assemble_index.html', locals())
            elif step.category == 3 or step.category == 4:  # 标定 检验
                return render(request, 'manufacturing/process_inspection_index.html', locals())
            elif step.category == 5:  # 标签打印
                return HttpResponse('标签打印页面待补充！')
            elif step.category == 6:  # VIN生成
                return render(request, 'manufacturing/vin_index.html', locals())
            else:  # 其他
                return HttpResponse('其他！')
        else:
            request.session['errMsg'] = '请先登陆！'
            return redirect(reverse('account:login'))

# def getOrderInfo(request, sequence_no):
#     if request.method == "POST":
#         info = {}
#         rows = []
#         vin_or_sn = request.POST.get('snInput')
#         current_vin = request.POST.get('product_vin')
#
#         try:
#             order = Order.objects.get(status=1)
#         except Order.DoesNotExist:
#             return JsonResponse({"ret": False, "errMsg": '订单未打开！', "rows": [], "total": 0})
#
#         if vin_or_sn:
#             if len(vin_or_sn) == 18:
#                 vin = vin_or_sn
#                 if not re.match(r'^IDP[A-Z]{3}\d{6}[1-9,A-Z][1-9,A-C]\d{4}$', vin):
#                     return JsonResponse({"ret": False, "errMsg": 'VIN格式不正确！', "rows": [], "total": 0})
#                 try:
#                     product = Product.objects.get(vin=vin, order_num=order)
#                 except Product.DoesNotExist:
#                     return JsonResponse({"ret": False, "errMsg": '该VIN不属于该订单！', "rows": [], "total": 0})
#                 info['product_vin'] = vin
#                 route = order.product_model.process_route
#                 step = ProcessStep.objects.get(process_route=route, sequence_no=sequence_no)
#                 if step.process_lock:
#                     try:
#                         r = ProcessRecord.objects.get(product=product, sequence_no=int(sequence_no)-1)
#                         if not r.result:
#                             return JsonResponse({"ret": False, "errMsg": '请先完成上道工序！', "rows": [], "total": 0})
#                     except ProcessRecord.DoesNotExist:
#                         return JsonResponse({"ret": False, "errMsg": '请先完成上道工序！', "rows": [], "total": 0})
#                 try:
#                     process_record = ProcessRecord.objects.get(product=product, sequence_no=sequence_no)
#                 except ProcessRecord.DoesNotExist:
#                     process_record = ProcessRecord.objects.create(product=product, sequence_no=sequence_no)
#
#                 info['date'] = process_record.m_time
#                 step_record = AssemblyRecord.objects.filter_without_isdelete().filter(process_record=process_record)
#                 if not step_record:
#                     product = Product.objects.get(vin=vin)
#                     route = product.order_num.product_model.process_route
#                     step = ProcessStep.objects.get(process_route=route, sequence_no=sequence_no)
#
#                     step_materialmodel_ship2 = ProcessStep_MaterialModel.objects.filter(process_step=step)
#                     for ship in step_materialmodel_ship2:
#                         for i in range(int(ship.quantity)):
#                             AssemblyRecord.objects.create(process_record=process_record,
#                                                           material_model=ship.material_model)
#                     info['status'] = '进行中'
#                 elif step_record.filter(sn=None):
#                     info['status'] = '进行中'
#                 else:
#                     info['status'] = '已完成'
#
#             elif len(vin_or_sn) == 23:
#                 sn = vin_or_sn
#
#                 # 检验sn格式是否合法
#                 if not re.match(r'^[A-Z]\d{9}\d{2}\d{2}[1-9,A-C]\d{2}[1-9,A-Z]{2}\d{4}$', sn):
#                     return JsonResponse({"ret": False, "errMsg": 'SN格式不正确！', "rows": [], "total": 0})
#
#                 # 通过sn在数据库找到该物料，如果找不到返回错误；如果找到，校验该物料is_used是否为True
#                 try:
#                     material = TraceMaterial.objects.get(sn=sn)
#                     if material.is_used:
#                         return JsonResponse({"ret": False, "errMsg": '该物料已被其他产品使用！', "rows": [], "total": 0})
#                 except TraceMaterial.DoesNotExist:
#                     return JsonResponse({"ret": False, "errMsg": '该物料不存在！', "rows": [], "total": 0})
#
#                 # 获取物料型号，判度该物料型号是否在
#                 tmp_erp = sn[:10] + 'V' + sn[10:12]
#                 material_models = MaterialModel.objects.filter_without_isdelete().filter(erp_no__startswith=tmp_erp,
#                                                                                          is_traced=True)
#                 if not material_models:
#                     return JsonResponse({"ret": False, "errMsg": '未找到此物料编号！', "rows": [], "total": 0})
#                 material_model = None
#                 for model in material_models:
#                     if not material_model:
#                         material_model = model
#                     else:
#                         if int(material_model.erp_no[13:15]) < int(model.erp_no[13:15]):
#                             material_model = model
#
#                 try:
#                     product = Product.objects.get(vin=current_vin)
#                     route = product.order_num.product_model.process_route
#                     step = ProcessStep.objects.get(process_route=route, sequence_no=sequence_no)
#                     step_materialmodel_ship = ProcessStep_MaterialModel.objects.get(process_step=step, material_model=material_model)
#                     step_materialmodel_ship2 = ProcessStep_MaterialModel.objects.filter(process_step=step)
#                     step_total_quantity = 0
#                     if step_materialmodel_ship2:
#                         for ship in step_materialmodel_ship2:
#                             step_total_quantity += ship.quantity
#                 except Product.DoesNotExist:
#                     product = None
#                 except ProcessStep_MaterialModel.DoesNotExist:
#                     return JsonResponse({"ret": False, "errMsg": '该物料不属于本工序！', "rows": [], "total": 0})
#
#                 if product:
#                     info['product_vin'] = current_vin
#                     try:
#                         process_record = ProcessRecord.objects.get(product=product, sequence_no=sequence_no)
#
#                     except ProcessRecord.DoesNotExist:
#                         process_record = ProcessRecord.objects.create(product=product, sequence_no=sequence_no)
#                     info['date'] = process_record.m_time
#
#                     assembly_record = AssemblyRecord.objects.filter_without_isdelete().filter(sn=None,
#                                                                                               process_record=process_record,
#                                                                                               material_model=material_model)
#                     if not assembly_record:
#                         return JsonResponse({"ret": False, "errMsg": '该物料已经全部装配完毕！', "rows": [], "total": 0})
#
#                     else:
#                         record = assembly_record.first()
#                         record.sn = sn
#                         record.save()
#                         material.is_used = True
#                         material.save()
#
#                     assembly_record = AssemblyRecord.objects.filter_without_isdelete().filter(sn=None,
#                                                                                               process_record=process_record)
#                     if not assembly_record:
#                         process_record.result = True
#                         process_record.save()
#
#                 else:
#                     return JsonResponse({"ret": False, "errMsg": '请先输入VIN！', "rows": [], "total": 0})
#                     # info['product_vin'] = ''
#                     # info['date'] = ''
#
#             else:
#                 return JsonResponse({"ret": False, "errMsg": '输入长度不正确！', "rows": [], "total": 0})
#         try:
#             order = Order.objects.get(status=1)
#         except (Order.DoesNotExist, Order.MultipleObjectsReturned):
#             errMsg = '无打开订单或打开订单超过1个！'
#             return render(request, 'manufacturing/vin_index.html', locals())
#
#         product_model = order.product_model
#         info['product_erp'] = product_model.erp_no
#         info['product_name'] = product_model.name
#         info['product_model'] = product_model.model
#         info['order_num'] = order.num
#         info['order_quantity'] = order.quantity
#
#         products = Product.objects.filter_without_isdelete().filter(order_num=order.num)
#         step_pass_quantity = 0
#         for product in products:
#             try:
#                 ProcessRecord.objects.get(product=product, sequence_no=sequence_no, result=True)
#                 step_pass_quantity += 1
#             except ProcessRecord.DoesNotExist:
#                 continue
#
#         info['finish_quantity'] = step_pass_quantity
#         info['finish_rate'] = '{:.2%}'.format(step_pass_quantity/order.quantity)
#         info['user'] = 'user'
#
#         data = {"ret": True, "errMsg": "", "total": 0, "rows": rows, 'info': info}
#
#         return JsonResponse(data)


def getOrderInfo(request, step_id):
    if request.method == "POST":
        vin_or_sn = request.POST.get('snInput')
        current_vin = request.POST.get('product_vin')

        try:
            order = Order.objects.filter_without_isdelete().get(status=1)
        except Order.DoesNotExist:
            return JsonResponse({"ret": False, "errMsg": '订单未打开！', "rows": [], "total": 0})
        # route = order.product_model.process_route
        digit_num = 0
        re_str = ""
        vin_rule = order.product_model.vin_rule
        vin_rule_items = VinRuleItem.objects.filter_without_isdelete().filter(vin_rule=vin_rule)
        for item in vin_rule_items:
            if int(item.rule) == 5:
                re_str = item.content
            elif int(item.rule) == 6:
                digit_num = int(item.content)
        # step = ProcessStep.objects.filter_without_isdelete().get(process_route=route, sequence_no=sequence_no)
        step = ProcessStep.objects.filter_without_isdelete().get(id=step_id)

        if step.category == 6:
            data = vinGenStepProcess(order, step.sequence_no)
            return JsonResponse(data)
        else:
            if len(vin_or_sn) == digit_num:
                vin = vin_or_sn
                if not re.match(re_str, vin):
                    return JsonResponse({"ret": False, "errMsg": 'VIN格式不正确！', "rows": [], "total": 0})
                try:
                    product = Product.objects.filter_without_isdelete().get(vin=vin, order_num=order)
                except Product.DoesNotExist:
                    return JsonResponse({"ret": False, "errMsg": '该VIN不属于该订单！', "rows": [], "total": 0})

                if step.process_lock and (int(step.sequence_no) > 1):
                    try:
                        r = ProcessRecord.objects.filter_without_isdelete().get(product=product, sequence_no=int(step.sequence_no) - 1)
                        if not r.result:
                            return JsonResponse({"ret": False, "errMsg": '请先完成上道工序！', "rows": [], "total": 0})
                    except ProcessRecord.DoesNotExist:
                        return JsonResponse({"ret": False, "errMsg": '请先完成上道工序！', "rows": [], "total": 0})

                if step.category == 1:  # 装配工序
                    data = assemblyStepVinProcess(vin, order, product, step.sequence_no)
                    return JsonResponse(data)

                elif step.category == 3 or step.category == 4:  # 标定或检验工序

                    data = inspectStepProcesss(vin, order, product, step, step.sequence_no)
                    return JsonResponse(data)

            elif len(vin_or_sn) == 23:
                sn = vin_or_sn
                data = assemblyStepMatProcess(sn, current_vin, step.sequence_no, order)
                return JsonResponse(data)

            else:
                if current_vin:
                    try:
                        product = Product.objects.filter_without_isdelete().get(vin=current_vin, order_num=order)
                    except Product.DoesNotExist:
                        return JsonResponse({"ret": False, "errMsg": '该VIN不属于该订单！', "rows": [], "total": 0})
                    data = inspectStepProcesss(current_vin, order, product, step, step.sequence_no)
                    return JsonResponse(data)
                else:
                    # return JsonResponse({"ret": False, "errMsg": '输入长度不正确！', "rows": [], "total": 0})
                    return JsonResponse({"ret": True})


def assemblyStepMatProcess(sn, current_vin, sequence_no, order):
    info = {}
    rows = []
    # 检验sn格式是否合法
    if not re.match(r'^[A-Z]\d{9}\d{2}\d{2}[1-9,A-C]\d{2}[1-9,A-Z]{2}\d{4}$', sn):
        return {"ret": False, "errMsg": 'SN格式不正确！', "rows": [], "total": 0}

    # 通过sn在数据库找到该物料，如果找不到返回错误；如果找到，校验该物料is_used是否为True
    try:
        material = TraceMaterial.objects.filter_without_isdelete().get(sn=sn)
        if material.is_used:
            return {"ret": False, "errMsg": '该物料已被其他产品使用！', "rows": [], "total": 0}
    except TraceMaterial.DoesNotExist:
        return {"ret": False, "errMsg": '该物料不存在！', "rows": [], "total": 0}

    # 获取物料型号，判度该物料型号是否在
    tmp_erp = sn[:10] + 'V' + sn[10:12]
    material_models = MaterialModel.objects.filter_without_isdelete().filter(erp_no__startswith=tmp_erp,
                                                                             is_traced=True)
    if not material_models:
        return {"ret": False, "errMsg": '未找到此物料编号！', "rows": [], "total": 0}
    #  如果存在找到最新的ERP号的物料型号
    material_model = None
    for model in material_models:
        if not material_model:
            material_model = model
        else:
            if int(material_model.erp_no[13:15]) < int(model.erp_no[13:15]):
                material_model = model

    try:
        product = Product.objects.filter_without_isdelete().get(vin=current_vin)
        route = product.order_num.product_model.process_route
        step = ProcessStep.objects.filter_without_isdelete().get(process_route=route, sequence_no=sequence_no)
        step_materialmodel_ship = ProcessStep_MaterialModel.objects.get(process_step=step,
                                                                        material_model=material_model)
        step_materialmodel_ship2 = ProcessStep_MaterialModel.objects.filter(process_step=step)
        step_total_quantity = 0
        if step_materialmodel_ship2:
            for ship in step_materialmodel_ship2:
                step_total_quantity += ship.quantity
    except Product.DoesNotExist:
        product = None
    except ProcessStep_MaterialModel.DoesNotExist:
        return {"ret": False, "errMsg": '该物料不属于本工序！', "rows": [], "total": 0}

    if product:
        info['product_vin'] = current_vin
        try:
            process_record = ProcessRecord.objects.filter_without_isdelete().get(product=product, sequence_no=sequence_no)

        except ProcessRecord.DoesNotExist:
            process_record = ProcessRecord.objects.create(product=product, sequence_no=sequence_no)
        info['date'] = process_record.m_time

        assembly_record = AssemblyRecord.objects.filter_without_isdelete().filter(sn=None,
                                                                                  process_record=process_record,
                                                                                  material_model=material_model)
        if not assembly_record:
            return {"ret": False, "errMsg": '该物料已经全部装配完毕！', "rows": [], "total": 0}

        else:
            record = assembly_record.first()
            record.sn = sn
            record.save()
            material.is_used = True
            material.save()

        assembly_record = AssemblyRecord.objects.filter_without_isdelete().filter(sn=None,
                                                                                  process_record=process_record)
        if not assembly_record:
            process_record.result = True
            info['status'] = '已完成'
            process_record.save()

        product_model = order.product_model
        bom = BOM.objects.filter_without_isdelete().filter(product_model=order.product_model).order_by(
            "-erp_no").first()
        info['product_erp'] = bom.erp_no
        info['product_name'] = product_model.name
        info['product_model'] = product_model.model
        info['order_num'] = order.num
        info['order_quantity'] = order.quantity

        products = Product.objects.filter_without_isdelete().filter(order_num=order.num)
        step_pass_quantity = 0
        for product in products:
            try:
                ProcessRecord.objects.filter_without_isdelete().get(product=product, sequence_no=sequence_no, result=True)
                step_pass_quantity += 1
            except ProcessRecord.DoesNotExist:
                continue

        info['finish_quantity'] = step_pass_quantity
        info['finish_rate'] = '{:.2%}'.format(step_pass_quantity / order.quantity)
        info['user'] = 'user'

        data = {"ret": True, "errMsg": "", "total": 0, "rows": rows, 'info': info}
        return data

    else:
        return {"ret": False, "errMsg": '请先输入VIN！', "rows": [], "total": 0}


def inspectStepProcesss(vin, order, product, step, sequence_no):
    info = {}
    rows = []
    try:
        process_record = ProcessRecord.objects.filter_without_isdelete().get(product=product, sequence_no=sequence_no)
    except ProcessRecord.DoesNotExist:
        process_record = ProcessRecord.objects.create(product=product, sequence_no=sequence_no)

    step_record = TestRecord.objects.filter_without_isdelete().filter(process_record=process_record)
    route = product.order_num.product_model.process_route
    step = ProcessStep.objects.filter_without_isdelete().get(process_route=route, sequence_no=sequence_no)
    inspections = Inspection.objects.filter_without_isdelete().filter(process_step=step)
    if not step_record:
        info['status'] = '进行中'
    else:
        result = 1
        for record in step_record.order_by('-c_time')[0:inspections.count()]:
            if record.result == 0:
                result = 0
                break
        if result == 1:
            info['status'] = '已完成'
        else:
            info['status'] = '进行中'

    info['product_vin'] = vin
    info['date'] = process_record.m_time
    product_model = order.product_model
    bom = BOM.objects.filter_without_isdelete().filter(product_model=order.product_model).order_by(
        "-erp_no").first()
    info['product_erp'] = bom.erp_no
    info['product_name'] = product_model.name
    info['product_model'] = product_model.model
    info['order_num'] = order.num
    info['order_quantity'] = order.quantity

    products = Product.objects.filter_without_isdelete().filter(order_num=order.num)
    step_pass_quantity = 0
    for product in products:
        try:
            ProcessRecord.objects.filter_without_isdelete().get(product=product, sequence_no=sequence_no, result=True)
            step_pass_quantity += 1
        except ProcessRecord.DoesNotExist:
            continue
    info['date'] = process_record.m_time
    info['finish_quantity'] = step_pass_quantity
    info['finish_rate'] = '{:.2%}'.format(step_pass_quantity / order.quantity)
    info['user'] = 'user'

    data = {"ret": True, "errMsg": "", "total": 0, "rows": rows, 'info': info}
    return data


def assemblyStepVinProcess(vin, order, product, sequence_no):
    info = {}
    rows = []
    try:
        process_record = ProcessRecord.objects.filter_without_isdelete().get(product=product, sequence_no=sequence_no)
    except ProcessRecord.DoesNotExist:
        process_record = ProcessRecord.objects.create(product=product, sequence_no=sequence_no)
    info['product_vin'] = vin
    info['date'] = process_record.m_time
    step_record = AssemblyRecord.objects.filter_without_isdelete().filter(process_record=process_record)
    if not step_record:
        route = product.order_num.product_model.process_route
        step = ProcessStep.objects.filter_without_isdelete().get(process_route=route, sequence_no=sequence_no)

        step_materialmodel_ship2 = ProcessStep_MaterialModel.objects.filter(process_step=step)
        for ship in step_materialmodel_ship2:
            for i in range(int(ship.quantity)):
                AssemblyRecord.objects.create(process_record=process_record, material_model=ship.material_model)
        info['status'] = '进行中'
    elif step_record.filter(sn=None):
        info['status'] = '进行中'
    else:
        info['status'] = '已完成'
    product_model = order.product_model
    bom = BOM.objects.filter_without_isdelete().filter(product_model=order.product_model).order_by(
        "-erp_no").first()
    info['product_erp'] = bom.erp_no
    info['product_name'] = product_model.name
    info['product_model'] = product_model.model
    info['order_num'] = order.num
    info['order_quantity'] = order.quantity

    products = Product.objects.filter_without_isdelete().filter(order_num=order.num)
    step_pass_quantity = 0
    for product in products:
        try:
            ProcessRecord.objects.filter_without_isdelete().get(product=product, sequence_no=sequence_no, result=True)
            step_pass_quantity += 1
        except ProcessRecord.DoesNotExist:
            continue

    info['finish_quantity'] = step_pass_quantity
    info['finish_rate'] = '{:.2%}'.format(step_pass_quantity / order.quantity)
    info['user'] = 'user'

    data = {"ret": True, "errMsg": "", "total": 0, "rows": rows, 'info': info}

    return data


def vinGenStepProcess(order, sequence_no):
    info = {}
    rows = []
    product_model = order.product_model
    bom = BOM.objects.filter_without_isdelete().filter(product_model=order.product_model).order_by("-erp_no").first()
    info['product_erp'] = bom.erp_no
    info['product_name'] = product_model.name
    info['product_model'] = product_model.model
    info['order_num'] = order.num
    info['order_quantity'] = order.quantity
    products = Product.objects.filter_without_isdelete().filter(order_num=order.num)
    step_pass_quantity = 0
    for product in products:
        try:
            ProcessRecord.objects.filter_without_isdelete().get(product=product, sequence_no=sequence_no, result=True)
            step_pass_quantity += 1
        except ProcessRecord.DoesNotExist:
            continue
    # info['date'] = process_record.m_time
    info['finish_quantity'] = step_pass_quantity
    info['finish_rate'] = '{:.2%}'.format(step_pass_quantity / order.quantity)
    info['user'] = 'user'

    data = {"ret": True, "errMsg": "", "total": 0, "rows": rows, 'info': info}
    return data

def getInspectionData(request, step_id):
    if request.method == "GET":
        vin = request.GET.get('vin')
        input1 = request.GET.get('input1')
        if not vin and not input1:
            return JsonResponse({"ret": True})
        product = Product.objects.filter_without_isdelete().get(vin=vin)
        try:
            order = Order.objects.filter_without_isdelete().get(status=1)
        except Order.DoesNotExist:
            return JsonResponse({"ret": False, "errMsg": '无打开工单！', "rows": [], "total": 0})
        route = order.product_model.process_route
        # step = ProcessStep.objects.filter_without_isdelete().get(process_route=route, sequence_no=sequence_no)
        step = ProcessStep.objects.filter_without_isdelete().get(id=step_id)
        inspections = Inspection.objects.filter_without_isdelete().filter(process_step=step)
        try:
            process_record = ProcessRecord.objects.filter_without_isdelete().get(product=product, sequence_no=step.sequence_no)
        except ProcessRecord.DoesNotExist:
            process_record = None
        rows = []
        data = {"ret": True, "errMsg": "", "total": 0, "rows": rows, 'info': {}}
        if process_record:
            test_records = TestRecord.objects.filter_without_isdelete().filter(process_record=process_record).order_by('-c_time')

            if test_records:
                for r in test_records[0:inspections.count()]:
                    rows.append({'id': r.id,
                                 'num': r.num,
                                 'name': r.name,
                                 'category': r.category,
                                 'mode': r.mode,
                                 'upper': r.upper,
                                 'lower': r.lower,
                                 'measure': r.data,
                                 'result': str(r.result),
                                 'm_time': r.m_time.strftime("%Y-%m-%d-%H:%M:%S"),
                                 'c_time': r.c_time.strftime("%Y-%m-%d-%H:%M:%S"),
                                 })
            else:
                for inspection in inspections:
                    rows.append({
                                 'num': inspection.num,
                                 'name': inspection.name,
                                 'category': inspection.category,
                                 'mode': inspection.mode,
                                 'upper': inspection.upper,
                                 'lower': inspection.lower,
                                 'measure': '',
                                 'result': '',
                                 })
        else:
            for inspection in inspections:
                rows.append({
                    'num': inspection.num,
                    'name': inspection.name,
                    'category': inspection.category,
                    'mode': inspection.mode,
                    'upper': inspection.upper,
                    'lower': inspection.lower,
                    'measure': '',
                    'result': '',
                })
        return JsonResponse(data)


def saveInspectionData(request, step_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        vin = data.get('vin')
        rows = data.get('row')
        print(vin)
        print(rows)

        if not all([vin, rows]):
            return JsonResponse({"ret": False, "errMsg": "数据不能为空！", "rows": [], "total": 0})
        for i, row in enumerate(rows):
            try:
                if row.get('measure'):
                    tmp = float(row.get('measure'))
            except (TypeError, ValueError):
                return JsonResponse({"ret": False, "errMsg": "第" + str(i + 1) + "行的测试值数据错误！", "rows": [], "total": 0})

        try:
            product = Product.objects.filter_without_isdelete().get(vin=vin)
        except Product.DoesNotExist:
            return JsonResponse({"ret": False, "errMsg": "该VIN不存在", "rows": [], "total": 0})
        try:
            step = ProcessStep.objects.filter_without_isdelete().get(id=step_id)
        except ProcessStep.DoesNotExist:
            return JsonResponse({"ret": False, "errMsg": "该产品无此工序！", "rows": [], "total": 0})
        try:
            process_record = ProcessRecord.objects.filter_without_isdelete().get(product=product, sequence_no=step.sequence_no)
        except ProcessRecord.DoesNotExist:
            process_record = ProcessRecord.objects.create(product=product, sequence_no=step.sequence_no)

        total_result = None
        for row in rows:
            if row.get('result') == '' or row.get('result') == '0':
                total_result = False if (total_result is None) else (total_result and False)
            else:
                total_result = True if (total_result is None) else (total_result and True)

            if row.get('measure'):
                data = float(row.get('measure'))
            else:
                data = 0
            record = TestRecord.objects.create(process_record=process_record,
                                               num=row.get('num'),
                                               name=row.get('name'),
                                               category=row.get('category'),
                                               mode=row.get('mode'),
                                               operator=None,
                                               data=data,
                                               upper=float(row.get('upper')),
                                               lower=float(row.get('lower')),)

            if row.get('result') == '':
                record.result = None
            else:
                record.result = row.get('result')
            record.save()
        process_record.result = total_result
        process_record.save()

        return JsonResponse({"ret": True, "errMsg": "", "total": 0, "rows": rows})


def getProductInfo(request, step_id):
    if request.method == "GET":
        info = {}
        rows = []
        try:
            order = Order.objects.filter_without_isdelete().get(status=1)
        except (Order.DoesNotExist, Order.MultipleObjectsReturned):
            errMsg = '无打开订单或打开订单超过1个！'
            return render(request, 'manufacturing/vin_index.html', locals())

        product_model = order.product_model
        bom = BOM.objects.filter_without_isdelete().filter(product_model=order.product_model).order_by(
            "-erp_no").first()
        products = Product.objects.filter_without_isdelete().filter(order_num=order.num)

        data = {"ret": True, "errMsg": "", "total": 0, "rows": rows}
        if not products:
            return JsonResponse(data)
        else:
            for product in products:
                rows.append({'id': product.id,
                             'vin': product.vin,
                             'order_num': order.num,
                             'erp_no': bom.erp_no,
                             'name': product_model.name,
                             'model': product_model.model,
                             'c_time': product.c_time,
                             'm_time': product.m_time
                             })
            return JsonResponse(data)


def generateVIN(request, step_id):
    if request.method == "POST":
        info = {}
        try:
            order = Order.objects.filter_without_isdelete().get(status=1)
        except (Order.DoesNotExist, Order.MultipleObjectsReturned):
            errMsg = '无打开订单或打开订单超过1个！'
            return render(request, 'manufacturing/vin_index.html', locals())
        try:
            step = ProcessStep.objects.filter_without_isdelete().get(id=step_id)
        except ProcessStep.DoesNotExist:
            return JsonResponse({"ret": False, "errMsg": "该产品无此工序！", "rows": [], "total": 0})
        products = Product.objects.filter_without_isdelete().filter(order_num=order.num)
        if products.count() < order.quantity:
            vin = get_vin(order)
            if not vin:
                return_dict = {"ret": False, "errMsg": 'VIN获取失败！', "rows": [], "total": 0}
                return JsonResponse(return_dict)
            product = Product.objects.create(order_num=order, vin=vin)
            ProcessRecord.objects.create(product=product, sequence_no=step.sequence_no, result=1)
            info['vin'] = vin
            return_dict = {"ret": True, "errMsg": '', "rows": [], "total": 0, 'info': info}
            return JsonResponse(return_dict)
        else:
            return_dict = {"ret": False, "errMsg": '该订单VIN已经全部生成', "rows": [], "total": 0}
            return JsonResponse(return_dict)


def get_vin(order):
    vin = ""
    product_model = order.product_model
    vin_rule = product_model.vin_rule
    vin_rule_items = VinRuleItem.objects.filter_without_isdelete().filter(vin_rule=vin_rule).order_by('sequence_no')
    bom = BOM.objects.filter_without_isdelete().filter(product_model=order.product_model).order_by("-erp_no").first()
    year = datetime.datetime.now().year
    month = datetime.datetime.now().month
    day = datetime.datetime.now().day
    print(year, month, day)
    for item in vin_rule_items:
        if item.rule == 0:
            # 无
            vin += str(item.content).strip()
        elif item.rule == 1:
            # 日期2位YM
            year_str = ""
            month_str = ""
            YEARS = ['1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K',
                     'L',
                     'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
            MONTHS = ['1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C']
            for i, y in zip(range(2011, 2090), YEARS):  # zip会按最短的进行绑定
                if year == i:
                    year_str = y
                    break
            for j, m in zip(range(1, 13), MONTHS):  # zip会按最短的进行绑定
                if month == j:
                    month_str = m
            vin += year_str
            vin += month_str
        elif item.rule == 2:
            # 日期5位YYMDD
            year_str = str(year)[3:]
            month_str = None
            day_str = "{0:02d}".format(day)
            MONTHS = ['1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C']
            for j, m in zip(range(1, 13), MONTHS):  # zip会按最短的进行绑定
                if month == j:
                    month_str = m
            vin = vin + year_str + month_str + day_str
        elif item.rule == 3:
            # 产品总成ERP版本V后2位
            vin += bom.erp_no[11:13]
        elif item.rule == 4:
            # 流水号
            product = Product.objects.filter_without_isdelete().filter(vin__startswith=vin).order_by('-vin').first()
            if product:
                serial_number = int(product.vin[(-int(item.digit_num)):]) + 1
            else:
                serial_number = 1
            vin = vin + str(serial_number).zfill(int(item.digit_num))
    return vin


def getAssembleRecord(request, step_id):
    if request.method == "GET":
        vin = request.GET.get('vin')
        input1 = request.GET.get('input1')
        if not vin and not input1:
            return JsonResponse({})
        if not vin:
            return_dict = {"ret": False, "errMsg": 'VIN不能为空！', "rows": [], "total": 0}
            return JsonResponse(return_dict)
        else:
            product = Product.objects.filter_without_isdelete().get(vin=vin)
            try:
                step = ProcessStep.objects.filter_without_isdelete().get(id=step_id)
            except ProcessStep.DoesNotExist:
                return JsonResponse({"ret": False, "errMsg": "该产品无此工序！", "rows": [], "total": 0})
            try:
                process_record = ProcessRecord.objects.filter_without_isdelete().get(product=product, sequence_no=step.sequence_no)
            except ProcessRecord.DoesNotExist:
                process_record = None
            rows = []
            data = {"ret": True, "errMsg": "", "total": 0, "rows": rows, 'info': {}}
            if process_record:
                assembly_records = AssemblyRecord.objects.filter_without_isdelete().filter(process_record=process_record)

                if assembly_records:
                    for r in assembly_records:
                        if r.sn:
                            m = TraceMaterial.objects.filter_without_isdelete().get(sn=r.sn)
                            batch_num = m.batch_num
                        else:
                            batch_num = None
                        rows.append({'id': r.id,
                                     'sn': r.sn,
                                     'batch_num': batch_num,
                                     'erp_no': r.material_model.erp_no,
                                     'name': r.material_model.name,
                                     'model': r.material_model.model,
                                     'category': r.material_model.category,
                                     'c_time': r.c_time,
                                     'm_time': r.m_time,
                                     })
            return JsonResponse(data)




