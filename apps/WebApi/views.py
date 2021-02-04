import re
import json

from django.shortcuts import render
from .service.xgmes import XGMes
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from apps.bom_manager.models import MaterialModel
from apps.Inspection.models import Inspection, TraceMaterial, TMInspectRecord
from apps.order_manager.models import Order
from apps.product_manager.models import VinRule, VinRuleItem
from apps.manufacturing.models import Product, ProcessRecord, AssemblyRecord, TestRecord
from apps.process_manager.models import ProcessStep
from apps.station_manager.models import Fixture, TestStandard

@csrf_exempt
def getMatInsDataXG(request):
    if request.method == 'POST':
        vin = request.POST.get('vin')
        ip = "http://192.168.10.2:8989/"
        res = {}
        try:
            datadict = XGMes.getPrductData(ip, vin)
        except Exception as e:
            res['code'] = 1
            res['msg'] = str(e)
            return JsonResponse(res, safe=False)
        res['code'] = 0
        res['msg'] = 'success'
        res['data'] = datadict
        return JsonResponse(res, safe=False)


@csrf_exempt
def getMaterialStandard(request):
    if request.method == 'POST':
        sn = request.POST.get('sn')
        if not all([sn]):
            return JsonResponse({"code": 1, "msg": "sn格式不正确！", "data": []})
        if not re.match(r'^[A-Z]\d{9}\d{2}\d{2}[1-9,A-C]\d{2}[1-9,A-Z]{2}\d{4}$', sn):
            return JsonResponse({"code": 1, "msg": "sn格式不正确！", "data": []})

        tmp_erp = sn[:10] + 'V' + sn[10:12]
        material_models = MaterialModel.objects.filter_without_isdelete().filter(erp_no__startswith=tmp_erp,
                                                                                 is_traced=True)
        if not material_models:
            return JsonResponse({"code": 1, "msg": '未找到此物料编号！', "data": []})

        material_model = None
        for model in material_models:
            if not material_model:
                material_model = model
            else:
                if int(material_model.erp_no[13:15]) < int(model.erp_no[13:15]):
                    material_model = model
        objs = Inspection.objects.filter_without_isdelete().filter(material_model=material_model)
        resdict = {}
        if objs:
            resdict['code'] = 0
            resdict['msg'] = 'success'
            data = []
            for obj in objs:
                item = {}
                item['num'] = obj.num
                item['name'] = obj.name
                item['category'] = obj.category
                item['mode'] = obj.mode
                item['upper'] = obj.upper
                item['lower'] = obj.lower
                data.append(item.copy())
            resdict['data'] = data
        else:
            resdict['code'] = 1
            resdict['msg'] = '未找到检验标准'
            resdict['data'] = []
        return JsonResponse(resdict, safe=False)


@csrf_exempt
def getMaterialResult(request):
    if request.method == 'POST':
        sn = request.POST.get('sn')
        if not all([sn]):
            return JsonResponse({"code": 1, "msg": "sn格式不正确！", "data": []})
        if not re.match(r'^[A-Z]\d{9}\d{2}\d{2}[1-9,A-C]\d{2}[1-9,A-Z]{2}\d{4}$', sn):
            return JsonResponse({"code": 1, "msg": "sn格式不正确！", "data": []})
        try:
            material = TraceMaterial.objects.filter_without_isdelete().get(sn=sn)
        except TraceMaterial.DoesNotExist:
            return JsonResponse({"code": 1, "msg": "该sn不存在！", "data": []})
        objs = TMInspectRecord.objects.filter_without_isdelete().filter(trace_material=material)
        resdict = {}
        if objs:
            resdict['code'] = 0
            resdict['msg'] = 'success'
            data = []
            for obj in objs:
                item = {}
                item['num'] = obj.num
                item['name'] = obj.name
                item['category'] = obj.category
                item['mode'] = obj.mode
                item['upper'] = obj.upper
                item['lower'] = obj.lower
                item['result'] = obj.result
                item['data'] = obj.data
                item['operator'] = obj.operator
                data.append(item.copy())
            resdict['data'] = data
        else:
            resdict['code'] = 1
            resdict['msg'] = '未找到检验标准'
            resdict['data'] = []
        return JsonResponse(resdict, safe=False)


@csrf_exempt
def updateMaterialResult(request):
    if request.method == 'POST':
        sn = request.POST.get('sn')
        data_json = request.POST.get('data')
        if not all([sn, data_json]):
            return JsonResponse({"code": 1, "msg": 'SN不能为空！', "data": []})
        if not re.match(r'^[A-Z]\d{9}\d{2}\d{2}[1-9,A-C]\d{2}[1-9,A-Z]{2}\d{4}$', sn):
            return JsonResponse({"code": 1, "msg": 'SN格式不正确！', "data": []})

        tmp_erp = sn[:10] + 'V' + sn[10:12]
        material_model = MaterialModel.objects.filter_without_isdelete().filter(erp_no__startswith=tmp_erp,
                                                                                 is_traced=True).order_by('-erp_no').first()
        if not material_model:
            return JsonResponse({"code": 1, "msg": '未找对应的ERP！', "data": []})

        # data = [{'num': "1", "name": "检验项1", "result": 1, "data": 11.2, "operator": None},
        # {'num': "2", "name": "检验项2", "result": 1, "data": 11.3, "operator": None}]
        data = eval(data_json)
        try:
            trace_material = TraceMaterial.objects.filter_without_isdelete().get(sn=sn)
        except TraceMaterial.DoesNotExist:
            return JsonResponse({"code": 1, "msg": '未找到此SN物料！', "data": []})

        for row in data:
            try:
                inspection = Inspection.objects.filter_without_isdelete().filter(material_model=material_model).\
                    get(name=row["name"], num=row["num"], mode=4)
            except Inspection.DoesNotExist:
                return JsonResponse({"code": 1, "msg": '未找到相应的检验标准！', "data": []})
            try:
                record = TMInspectRecord.objects.filter_without_isdelete().get(trace_material=trace_material,
                                                                               name=row["name"],
                                                                               num=row["num"],
                                                                               mode=4)
                record.result = row['result']
                record.data = row['data']
                record.operator = row['operator']
                record.save()
            except TMInspectRecord.DoesNotExist:
                TMInspectRecord.objects.create(trace_material=trace_material,
                                               num=inspection.num,
                                               name=inspection.name,
                                               category=inspection.category,
                                               mode=inspection.mode,
                                               result=row['result'],
                                               data=row['data'],
                                               operator=row['operator'],
                                               upper=inspection.upper,
                                               lower=inspection.lower,)

        all_records = TMInspectRecord.objects.filter_without_isdelete().filter(trace_material=trace_material)
        all_inspections = Inspection.objects.filter_without_isdelete().filter(material_model=material_model)
        if len(all_records) != len(all_inspections):
            status = 1
        else:
            status = 2
            for record in all_records:
                if record.result == 0:
                    status = 3
                    break

        trace_material.status = status
        trace_material.save()

        return JsonResponse({"code": 0, "msg": 'success', "data": []})


@csrf_exempt
def getCarBindMat(request):
    if request.method == 'POST':
        vin = request.POST.get('vin')

        try:
            order = Order.objects.filter_without_isdelete().get(status=1)
        except Order.DoesNotExist:
            return JsonResponse({"code": 1, "msg": '订单未打开！', "data": []})
        digit_num = 0
        re_str = ""
        vin_rule = order.product_model.vin_rule
        vin_rule_items = VinRuleItem.objects.filter_without_isdelete().filter(vin_rule=vin_rule)
        for item in vin_rule_items:
            if int(item.rule) == 5:
                re_str = item.content
            elif int(item.rule) == 6:
                digit_num = int(item.content)
        if len(vin) != digit_num:
            return JsonResponse({"code": 1, "msg": 'vin长度不正确', "data": []})
        if not re.match(re_str, vin):
            return JsonResponse({"code": 1, "msg": 'vin格式不正确', "data": []})

        process_route = order.product_model.process_route
        process_steps = ProcessStep.objects.filter_without_isdelete().filter(process_route=process_route, category=1)
        try:
            product = Product.objects.filter_without_isdelete().get(vin=vin)
        except Product.DoesNotExist:
            return JsonResponse({"code": 1, "msg": '未找到此vin', "data": []})
        res_list = []
        for step in process_steps:
            tmp_dict = {"工序号": step.sequence_no, "工序名称": step.name, "结果": 0, "info": []}
            try:
                process_record = ProcessRecord.objects.filter_without_isdelete().get(product=product, sequence_no=step.sequence_no)
                assembly_records = AssemblyRecord.objects.filter_without_isdelete().filter(process_record=process_record)
                if assembly_records:
                    for r in assembly_records:
                        tmp = {"epr_no": r.material_model.erp_no, "sn": r.sn}
                        tmp_dict['info'].append(tmp.copy())
                        tmp.clear()
                res_list.append(tmp_dict.copy())
                tmp_dict.clear()

            except ProcessRecord.DoesNotExist:
                res_list.append(tmp_dict.copy())
                tmp_dict.clear()

        return JsonResponse({"code": 0, "msg": 'success', "data": res_list})


        # a = [{"工序号": 1, "工序名称": "组装工序1", "结果": 0,
        #       "data": [{"epr_no": "Z00000000V1000A", "sn": "Z1401000801021120AA0003"},
        #               {"epr_no": "Z00000000V1000A", "sn": "Z1401000801021120AA0003"}]},
        #      {"工序号": 2, "工序名称": "组装工序2", "结果": 0,
        #       "data": [{"epr_no": "Z00000000V1000A", "sn": "Z1401000801021120AA0003"},
        #                {"epr_no": "Z00000000V1000A", "sn": "Z1401000801021120AA0003"}]}
        #      ]


@csrf_exempt
def getPreProcessResult(request):
    if request.method == 'POST':
        vin = request.POST.get('vin')
        curProcessNo = int(request.POST.get('curProcessNo'))

        try:
            order = Order.objects.filter_without_isdelete().get(status=1)
        except Order.DoesNotExist:
            return JsonResponse({"code": 1, "msg": '订单未打开！', "data": []})
        digit_num = 0
        re_str = ""
        vin_rule = order.product_model.vin_rule
        vin_rule_items = VinRuleItem.objects.filter_without_isdelete().filter(vin_rule=vin_rule)
        for item in vin_rule_items:
            if int(item.rule) == 5:
                re_str = item.content
            elif int(item.rule) == 6:
                digit_num = int(item.content)
        if len(vin) != digit_num:
            return JsonResponse({"code": 1, "msg": 'vin长度不正确', "data": []})
        if not re.match(re_str, vin):
            return JsonResponse({"code": 1, "msg": 'vin格式不正确', "data": []})

        res_dict = {}
        process_route = order.product_model.process_route
        process_step = ProcessStep.objects.filter_without_isdelete().get(process_route=process_route, sequence_no=curProcessNo)
        res_dict['curStepLock'] = process_step.process_lock
        try:
            product = Product.objects.filter_without_isdelete().get(vin=vin)
        except Product.DoesNotExist:
            return JsonResponse({"code": 1, "msg": '未找到此vin', "data": []})
        if curProcessNo > 1:
            try:
                process_record = ProcessRecord.objects.filter_without_isdelete().get(product=product,
                                                                                     sequence_no=curProcessNo - 1)
                res_dict['preStepRes'] = process_record.result
            except ProcessRecord.DoesNotExist:
                res_dict['preStepRes'] = 0
        else:
            res_dict['preStepRes'] = 1
        return JsonResponse({"code": 0, "msg": 'success', "data": res_dict})


@csrf_exempt
def getFixtureStandard(request):
    if request.method == 'POST':
        fixture_num = request.POST.get('fixture_num')
        res_list = []
        try:
            fixture = Fixture.objects.filter_without_isdelete().get(num=fixture_num)
            items = TestStandard.objects.filter_without_isdelete().filter(fixture=fixture)
            for item in items:
                tmp = {}
                tmp['num'] = item.num
                tmp['name'] = item.name
                tmp['upper'] = item.upper
                tmp['lower'] = item.lower
                tmp['version'] = item.version
                res_list.append(tmp.copy())
                tmp.clear()
            return JsonResponse({"code": 0, "msg": 'success', "data": res_list})
        except Fixture.DoesNotExist:
            return JsonResponse({"code": 1, "msg": '未找到此工装号', "data": []})


@csrf_exempt
def updateCarResult(request):
    if request.method == 'POST':
        vin = request.POST.get('vin')
        curProcessNo = int(request.POST.get('curProcessNo'))
        data_json = request.POST.get('data')

        try:
            order = Order.objects.filter_without_isdelete().get(status=1)
        except Order.DoesNotExist:
            return JsonResponse({"code": 1, "msg": '订单未打开！', "data": []})
        digit_num = 0
        re_str = ""
        vin_rule = order.product_model.vin_rule
        vin_rule_items = VinRuleItem.objects.filter_without_isdelete().filter(vin_rule=vin_rule)
        for item in vin_rule_items:
            if int(item.rule) == 5:
                re_str = item.content
            elif int(item.rule) == 6:
                digit_num = int(item.content)
        if len(vin) != digit_num:
            return JsonResponse({"code": 1, "msg": 'vin长度不正确', "data": []})
        if not re.match(re_str, vin):
            return JsonResponse({"code": 1, "msg": 'vin格式不正确', "data": []})

        process_route = order.product_model.process_route
        process_step = ProcessStep.objects.filter_without_isdelete().get(process_route=process_route,
                                                                         sequence_no=curProcessNo)
        try:
            product = Product.objects.filter_without_isdelete().get(vin=vin)
        except Product.DoesNotExist:
            return JsonResponse({"code": 1, "msg": '未找到此vin', "data": []})

        try:
            process_record = ProcessRecord.objects.filter_without_isdelete().get(product=product,
                                                                                 sequence_no=curProcessNo)
        except ProcessRecord.DoesNotExist:
            process_record = ProcessRecord.objects.create(product=product, sequence_no=curProcessNo)

        # data = [{'num': "1", "name": "检验项1", "result": 1, "data": 11.2, "operator": None},
        # {'num': "2", "name": "检验项2", "result": 1, "data": 11.3, "operator": None}]
        data_list = eval(data_json)

        for data in data_list:
            try:
                teststandard = TestStandard.objects.filter_without_isdelete().filter(fixture=process_step.fixture).\
                    get(name=data["name"], num=data["num"])
            except TestStandard.DoesNotExist:
                return JsonResponse({"code": 1, "msg": '未找到相应的测试标准！', "data": []})
            try:
                testrecord = TestRecord.objects.filter_without_isdelete().get(process_record=process_record,
                                                                                 num=data["num"],
                                                                                 name=data["name"],)
                testrecord.result = data['result']
                testrecord.data = data['data']
                testrecord.operator = data['operator']
                testrecord.save()
            except TestRecord.DoesNotExist:
                TestRecord.objects.create(process_record=process_record,
                                           num=data["num"],
                                           name=data["name"],
                                           category=2,
                                           mode=4,
                                           result=data['result'],
                                           data=data['data'],
                                           operator=data['operator'],
                                           upper=teststandard.upper,
                                           lower=teststandard.lower, )

        all_records = TestRecord.objects.filter_without_isdelete().filter(process_record=process_record)
        all_teststandard = TestStandard.objects.filter_without_isdelete().filter(fixture=process_step.fixture)

        if len(all_records) != len(all_teststandard):
            process_record.result = 0
            return JsonResponse({"code": 1, "msg": '测试结果项与测试标准数量不符合', "data": []})
        else:
            result = 1
            for record in all_records:
                if record.result == 0:
                    result = 0
                    break

        process_record.result = result
        process_record.save()

        return JsonResponse({"code": 0, "msg": 'success', "data": []})