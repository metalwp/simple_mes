import json
import re

from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.views.generic import View

from .models import ProductModel, ProductCategory, VinRule, VinRuleItem
from apps.process_manager.models import ProcessRoute
from apps.bom_manager.models import BOM
from apps.order_manager.models import Order


# Create your views here.


@login_required
def pc_index(request):
    product_category = ProductCategory.objects.filter_without_isdelete()
    return render(request, 'product_manager/pc_index.html', locals())


def getPcData(request):
    if request.method == 'GET':
        # 收取前端数据
        pageSize = int(request.GET.get('pageSize'))
        pageNumber = int(request.GET.get('pageNumber'))
        # searchText = request.GET.get('searchText')
        sortName = request.GET.get('sortName')
        sortOrder = request.GET.get('sortOrder')
        search_kw = request.GET.get('search_kw')
        if sortOrder == 'asc':
            sort_str = sortName
        else:
            sort_str = '-' + sortName

        if not search_kw:
            total = ProductCategory.objects.filter_without_isdelete().count()
            categorys = ProductCategory.objects.filter_without_isdelete().order_by(sort_str)[(pageNumber - 1) * pageSize:(pageNumber) * pageSize]
        else:
            categorys = ProductCategory.objects.filter_without_isdelete().filter(Q(name__contains=search_kw)).order_by(sort_str) \
                        [(pageNumber - 1) * pageSize:(pageNumber) * pageSize]
            # 获取查询结果的总条数
            total = ProductCategory.objects.filter_without_isdelete().filter(Q(name__contains=search_kw)).order_by(sort_str) \
                        [(pageNumber - 1) * pageSize:(pageNumber) * pageSize].count()
        rows = []
        data = {"total": total, "rows": rows}
        for category in categorys:
            if category.parent:
                rows.append({'id': category.id,
                             'name': category.name,
                             'parent': category.parent.name,
                             'c_time': category.c_time.strftime("%Y-%m-%d-%H:%M:%S"),
                             'm_time': category.m_time.strftime("%Y-%m-%d-%H:%M:%S")})
            else:
                rows.append({'id': category.id,
                             'name': category.name,
                             'parent': None,
                             'c_time': category.c_time.strftime("%Y-%m-%d-%H:%M:%S"),
                             'm_time': category.m_time.strftime("%Y-%m-%d-%H:%M:%S")})
        return HttpResponse(json.dumps(data), content_type="application/json")
    else:
        return HttpResponse('Error!')


def addPcData(request):
    if request.method == "POST":
        # 收取前端数据
        c_name = request.POST.get('c_name')
        p_id = request.POST.get('p_name')

        # 校验数据有效性
        if not c_name:
            return JsonResponse( {"ret": False, "errMsg": '数据不能为空！', "rows": [], "total": 0})

        # 业务处理
        if p_id:
            parent = ProductCategory.objects.get(id=p_id)
        else:
            parent = None
        try:
            category = ProductCategory(name=c_name, parent=parent)
            category.save()
        except Exception as e:
            return JsonResponse( {"ret": False, "errMsg": str(e), "rows": [], "total": 0})

        #返回应答
        return JsonResponse( {"ret": True, "errMsg": '', "rows": [], "total": 0})


def updatePcData(request):
    if request.method == "POST":
        # 收取前端数据
        id = request.POST.get('update_id')
        c_name = request.POST.get('update_c_name')
        p_id = request.POST.get('update_p_name')

        # 校验数据有效性
        if not c_name:
            return JsonResponse({"ret": False, "errMsg": '数据不能为空！', "rows": [], "total": 0})

        # 业务处理
        if p_id:
            parent = get_object_or_404(ProductCategory, id=p_id)
        else:
            parent = None
        try:
            pc, created = ProductCategory.objects.update_or_create(id=id, defaults={'name': c_name,
                                                                                'parent': parent})
        except Exception as e:
            return JsonResponse( {"ret": False, "errMsg": str(e), "rows": [], "total": 0})

        # 返回应答
        return JsonResponse({"ret": True, "errMsg": '', "rows": [], "total": 0})


def deletePcData(request):
    if request.method == "POST":
        # 收取前端数据
        _id = request.POST.get('id')

        # 校验数据有效性
        if not _id:
            return JsonResponse({"ret": False, "errMsg": '数据不能为空！', "rows": [], "total": 0})

        # 业务处理
        try:
            catagory = ProductCategory.objects.filter_without_isdelete().get(id=_id)
            product_model = ProductModel.objects.filter_without_isdelete().filter(catagory=catagory)
            if product_model:
                return JsonResponse({"ret": False, "errMsg": "该产品类型已创建产品型号，无法删除！", "rows": [], "total": 0})
            else:
                catagory.delete()
        except Exception as e:
            return JsonResponse({"ret": False, "errMsg": str(e), "rows": [], "total": 0})

        # 返回应答
        return JsonResponse({"ret": True, "errMsg": '', "rows": [], "total": 0})


@login_required
def pm_index(request):
    products = ProductModel.objects.filter_without_isdelete()
    categorys = ProductCategory.objects.filter_without_isdelete()
    process_routes = ProcessRoute.objects.filter_without_isdelete()
    vin_rules = VinRule.objects.filter_without_isdelete().filter(product_model=None)
    vin_rules2 = VinRule.objects.filter_without_isdelete().all()

    return render(request, 'product_manager/pm_index.html', locals())


def getPmData(request):
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
            total = ProductModel.objects.filter_without_isdelete().count()
            products = ProductModel.objects.filter_without_isdelete().order_by(sort_str)[(pageNumber - 1) * pageSize:(pageNumber) * pageSize]
        else:
            products = ProductModel.objects.filter_without_isdelete().filter(Q(name__contains=search_kw)).order_by(sort_str) \
                        [(pageNumber - 1) * pageSize: pageNumber * pageSize]
            # 获取查询结果的总条数
            total = ProductModel.objects.filter_without_isdelete().filter(Q(name__contains=search_kw)).order_by(sort_str) \
                        [(pageNumber - 1) * pageSize: pageNumber * pageSize].count()
        rows = []
        data = {"total": total, "rows": rows}
        for product in products:
            if product.category:
                category = product.category.name
            else:
                category = None
            if product.process_route:
                process_route = product.process_route.name
            else:
                process_route = None
            rows.append({'id': product.id,
                         'name': product.name,
                         'model': product.model,
                         'category': category,
                         'process_route': process_route,
                         "vin_rule": product.vin_rule.name if product.vin_rule else None,
                         'c_time': product.c_time.strftime("%Y-%m-%d-%H:%M:%S"),
                         'm_time': product.m_time.strftime("%Y-%m-%d-%H:%M:%S")})

        return HttpResponse(json.dumps(data), content_type="application/json")
    else:
        return HttpResponse('Error!')


def addPmData(request):
    if request.method == "POST":
        name = request.POST.get('nameInput')
        modal = request.POST.get('modalInput')
        #erp_no = request.POST.get('erpInput')
        category_id = request.POST.get('categorySelect')
        process_route_id = request.POST.get('processRouteSelect')
        vin_rule_id = request.POST.get('ruleSelect')

        if not all([name, modal]):
            return JsonResponse({"ret": False, "errMsg": '数据不能为空！', "rows": [], "total": 0})
        # 校验物料号格式
        # if not re.match(r'^[A-Z]\d{9}V\d{4}A$', erp_no):
        #     return JsonResponse({"ret": False, "errMsg": '物料号格式不正确！', "rows": [], "total": 0})

        if category_id:
            try:
                category = ProductCategory.objects.filter_without_isdelete().get(id=category_id)
            except Exception as e:
                return JsonResponse({"ret": False, "errMsg": str(e), "rows": [], "total": 0})
        else:
            category = None

        if vin_rule_id:
            try:
                vin_rule = VinRule.objects.filter_without_isdelete().get(id=vin_rule_id)
            except Exception as e:
                return JsonResponse({"ret": False, "errMsg": str(e), "rows": [], "total": 0})
        else:
            vin_rule = None

        if process_route_id:
            try:
                process_route = ProcessRoute.objects.filter_without_isdelete().get(id=process_route_id)
                if process_route.productmodel_set.all().filter(is_delete=False):
                    return JsonResponse({"ret": False, "errMsg": "该工艺路线已被其他产品使用，请新建工艺路线！", "rows": [], "total": 0})
            except Exception as e:
                return JsonResponse({"ret": False, "errMsg": str(e), "rows": [], "total": 0})
        else:
            process_route = None
        try:
            product = ProductModel(name=name,
                                   model=modal,
                                   category=category,
                                   process_route=process_route,
                                   vin_rule=vin_rule
                                   )
            product.save()
        except Exception as e:
            return JsonResponse({"ret": False, "errMsg": str(e), "rows": [], "total": 0})

        # 返回应答
        return JsonResponse({"ret": True, "errMsg": '', "rows": [], "total": 0})



def updatePmData(request):
    if request.method == "POST":
        # 收取前端数据
        id = request.POST.get('idInputUpdate')
        name = request.POST.get('nameInputUpdate')
        model = request.POST.get('modelInputUpdate')
        #erp_no = request.POST.get('erpInputUpdate')
        category_id = request.POST.get('categorySelectUpdate')
        process_route_id = request.POST.get('processRouteSelectUpdate')
        vin_rule_id = request.POST.get('u_ruleSelect')


        # 校验数据有效性
        if not all([name, model, ]):
            return JsonResponse({"ret": False, "errMsg": '数据不能为空！', "rows": [], "total": 0})

        # 业务处理
        if category_id:
            category = get_object_or_404(ProductCategory, id=category_id)
        else:
            category = None

        if process_route_id:
            try:
                process_route = ProcessRoute.objects.filter_without_isdelete().get(id=process_route_id)
                temp = ProductModel.objects.filter_without_isdelete().exclude(id=id).filter(process_route=process_route)

                if temp:
                    return JsonResponse({"ret": False, "errMsg": "该工艺路线已被其他产品使用，请新建工艺路线！", "rows": [], "total": 0})
            except Exception as e:
                return JsonResponse({"ret": False, "errMsg": str(e), "rows": [], "total": 0})
        else:
            process_route = None

        if vin_rule_id:
            try:
                #vin_rule = VinRule.objects.filter_without_isdelete().exclude(product_model__id=id).get(id=vin_rule_id)
                vin_rule = VinRule.objects.filter_without_isdelete().get(id=vin_rule_id)
                temp = ProductModel.objects.filter_without_isdelete().exclude(id=id).filter(vin_rule=vin_rule)
                if temp:
                    return JsonResponse({"ret": False, "errMsg": "该VIN规则已被使用！", "rows": [], "total": 0})
            except VinRule.DoesNotExist:
                return JsonResponse({"ret": False, "errMsg": "该VIN规则不存在！", "rows": [], "total": 0})

        else:
            vin_rule = None

        try:
            pm, created = ProductModel.objects.update_or_create(id=id, defaults={'name': name,
                                                                                 'model': model,
                                                                                 'category': category,
                                                                                 'process_route': process_route,
                                                                                 "vin_rule":vin_rule})
        except Exception as e:
            return JsonResponse({"ret": False, "errMsg": str(e), "rows": [], "total": 0})

        # 返回应答
        return JsonResponse({"ret": True, "errMsg": '', "rows": [], "total": 0})


def deletePmData(request):
    if request.method == "POST":
        # 收取前端数据
        _id = request.POST.get('id')

        # 校验数据有效性
        if not _id:
            return JsonResponse({"ret": False, "errMsg": '数据不能为空！', "rows": [], "total": 0})

        # 业务处理
        try:
            product_model = ProductModel.objects.filter_without_isdelete().get(id=_id)
            boms = BOM.objects.filter_without_isdelete().filter(product_model=product_model)
            orders = Order.objects.filter_without_isdelete().filter(product_model=product_model)
            if orders:
                return JsonResponse({"ret": False, "errMsg": "该产品已创建订单，无法删除！", "rows": [], "total": 0})
            else:
                product_model.vin_rule = None
                product_model.delete()
                for bom in boms:
                    bom.delete()
                # 返回应答
                return JsonResponse({"ret": True, "errMsg": '', "rows": [], "total": 0})

        except Exception as e:
            return JsonResponse({"ret": False, "errMsg": str(e), "rows": [], "total": 0})


class VinRuleView(View):

    def get(self, request):
        user = request.user
        if user.is_authenticated:
            model = VinRule
            if request.path.split('/')[-2] == 'get':
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
                    total = model.objects.filter_without_isdelete().count()
                    objs = model.objects.filter_without_isdelete().order_by(sort_str)[
                           (pageNumber - 1) * pageSize:(pageNumber) * pageSize]
                else:
                    objs = model.objects.filter_without_isdelete().filter(
                        Q(product_model__name__contains=search_kw)).order_by(sort_str) \
                        [(pageNumber - 1) * pageSize: pageNumber * pageSize]
                    # 获取查询结果的总条数
                    total = model.objects.filter_without_isdelete().filter(
                        Q(product_model__name__contains=search_kw)).order_by(sort_str) \
                        [(pageNumber - 1) * pageSize: pageNumber * pageSize].count()
                rows = []
                data = {"total": total, "rows": rows}
                for obj in objs:
                    try:
                        temp = ProductModel.objects.get(vin_rule=obj)
                    except ProductModel.DoesNotExist:
                        temp = None
                    rows.append(
                        {"id": obj.id,
                         "product_name": temp.name if temp else None,
                         "model_name": temp.model if temp else None,
                         'name': obj.name})
                return JsonResponse(data)
            else:
                products = ProductModel.objects.filter_without_isdelete().all()
                return render(request, "product_manager/vin_rule.html", locals())

        else:
            request.session['errMsg'] = '请先登陆！'
            return redirect(reverse('account:login'))

    def post(self, request):
        if request.path.split('/')[-2] == 'add':
            ret, errMsg, rows, total = self.add(request)
            return JsonResponse({"ret": ret, "errMsg": errMsg, "rows": rows, "total": total})
        elif request.path.split('/')[-2] == 'delete':
            ret, errMsg, rows, total = self.delete(request)
            return JsonResponse({"ret": ret, "errMsg": errMsg, "rows": rows, "total": total})
        elif request.path.split('/')[-2] == 'update':
            ret, errMsg, rows, total = self.update(request)
            return JsonResponse({"ret": ret, "errMsg": errMsg, "rows": rows, "total": total})

    @staticmethod
    def add(request):
        name = request.POST.get('nameInput')
        product_id = request.POST.get('productSelect')

        # 进行数据校验
        if not all([name]):
            # 数据不完整
            return False, '数据不完整！', [], 0

        try:
            obj = VinRule.objects.get(name=name)
        except VinRule.DoesNotExist:
            obj = None

        if obj:
            return False, '该名称已使用！', [], 0

        if product_id:
            try:
                product = ProductModel.objects.get(id=product_id)
            except ProductModel.DoesNotExist:
                product = None
            if product:
                if not product.vin_rule:
                    vin_rule = VinRule.objects.create(name=name)
                    product.vin_rule = vin_rule
                    product.save()
                    return True, '', [], 0
                else:
                    return False, '该产品已经绑定VIN规则！', [], 0
            else:
                return False, '该产品不存在！', [], 0
        else:
            vin_rule = VinRule.objects.create(name=name)
            return True, '', [], 0

    @staticmethod
    def delete(request):
        model = VinRule
        id = request.POST.get('id')
        try:
            obj = model.objects.get(id=id)
            obj.delete()
            return True, '', [], 0
        except Exception as e:
            return False, str(e), [], 0

    @staticmethod
    def update(request):
        id = request.POST.get("u_idInput")
        name = request.POST.get('u_nameInput')
        product_id = request.POST.get('u_productSelect')

        # 进行数据校验
        if not all([id, name]):
            # 数据不完整
            return False, '数据不完整！', [], 0

        try:
            obj1 = VinRule.objects.get(id=id)
        except VinRule.DoesNotExist:
            return False, '该VIN规则不存在！', [], 0

        if product_id:
            try:
                product = ProductModel.objects.get(id=product_id)
            except ProductModel.DoesNotExist:
                return False, '该产品不存在！', [], 0
        else:
            product = None

        objs = VinRule.objects.exclude(id=id).filter(name=name)

        if not objs:
            obj1.name = name
            if product:
                if not product.vin_rule:
                    product.vin_rule = obj1
                    product.save()
                else:
                    return False, '该产品已绑定VIN规则！', [], 0
            else:
                try:
                    temp = ProductModel.objects.get(vin_rule=obj1)
                    temp.vin_rule = None
                    temp.save()
                except ProductModel.DoesNotExist:
                    temp = None
            obj1.save()
            return True, '', [], 0
        else:
            return False, '该VIN规则名称已存在！', [], 0


class VinRuleItemView(View):

    def get(self, request, vin_rule_id):
        user = request.user
        if user.is_authenticated:
            model = VinRuleItem
            if request.path.split('/')[-2] == 'get':
                pageSize = int(request.GET.get('pageSize'))
                pageNumber = int(request.GET.get('pageNumber'))
                sortName = request.GET.get('sortName')
                sortOrder = request.GET.get('sortOrder')
                search_kw = request.GET.get('search_kw')
                if sortOrder == 'asc':
                    sort_str = sortName
                else:
                    sort_str = '-' + sortName
                vin_rule = VinRule.objects.get(id=vin_rule_id)
                if not search_kw:
                    total = model.objects.filter_without_isdelete().filter(vin_rule=vin_rule).count()
                    objs = model.objects.filter_without_isdelete().filter(vin_rule=vin_rule).order_by(sort_str)[
                           (pageNumber - 1) * pageSize:(pageNumber) * pageSize]
                else:
                    objs = model.objects.filter_without_isdelete().filter(vin_rule=vin_rule).filter(
                        Q(product_model__name__contains=search_kw)).order_by(sort_str) \
                        [(pageNumber - 1) * pageSize: pageNumber * pageSize]
                    # 获取查询结果的总条数
                    total = model.objects.filter_without_isdelete().filter(vin_rule=vin_rule).filter(
                        Q(product_model__name__contains=search_kw)).order_by(sort_str) \
                        [(pageNumber - 1) * pageSize: pageNumber * pageSize].count()
                rows = []
                data = {"total": total, "rows": rows}
                for obj in objs:
                    rows.append(
                        {"id": obj.id,
                         "sequence_no": obj.sequence_no,
                         "digit_num": obj.digit_num,
                         "rule": obj.rule,
                         "content": obj.content,
                         'remark': obj.remark})
                return JsonResponse(data)
            else:
                rule_choice = VinRuleItem.RULE_CHOICE
                vin_rule = VinRule.objects.get(id=vin_rule_id)
                return render(request, "product_manager/vin_rule_item.html", locals())
        else:
            request.session['errMsg'] = '请先登陆！'
            return redirect(reverse('account:login'))

    def post(self, request, vin_rule_id):
        if request.path.split('/')[-2] == 'add':
            ret, errMsg, rows, total = self.add(request, vin_rule_id)
            return JsonResponse({"ret": ret, "errMsg": errMsg, "rows": rows, "total": total})
        elif request.path.split('/')[-2] == 'delete':
            ret, errMsg, rows, total = self.delete(request, vin_rule_id)
            return JsonResponse({"ret": ret, "errMsg": errMsg, "rows": rows, "total": total})
        elif request.path.split('/')[-2] == 'update':
            ret, errMsg, rows, total = self.update(request, vin_rule_id)
            return JsonResponse({"ret": ret, "errMsg": errMsg, "rows": rows, "total": total})

    @staticmethod
    def add(request, vin_rule_id):
        sequence_no = request.POST.get('sequenceNoInput')
        digit_num = request.POST.get('digitNumInput')
        rule = request.POST.get('ruleSelect')
        content = request.POST.get('contentInput')
        remark = request.POST.get('remarkInput')

        # 进行数据校验
        if not all([sequence_no, digit_num, rule]):
            # 数据不完整
            return False, '数据不完整！', [], 0

        vin_rule = VinRule.objects.get(id=vin_rule_id)

        try:
            obj = VinRuleItem.objects.filter_without_isdelete().filter(vin_rule=vin_rule).get(sequence_no=sequence_no)
        except VinRuleItem.DoesNotExist:
            obj = None

        if not obj:
            VinRuleItem.objects.create(sequence_no=sequence_no,
                                       digit_num=digit_num,
                                       rule=rule,
                                       content=content if content else None,
                                       remark=remark if remark else None,
                                       vin_rule=vin_rule)
            return True, '', [], 0
        else:
            return False, '序列号不能重复！', [], 0

    @staticmethod
    def delete(request, vin_rule_id):
        model = VinRuleItem
        id = request.POST.get('id')
        try:
            obj = model.objects.get(id=id)
            obj.delete()
            return True, '', [], 0
        except Exception as e:
            return False, str(e), [], 0

    @staticmethod
    def update(request, vin_rule_id):
        print(request.POST)
        id = request.POST.get('u_idInput')
        sequence_no = request.POST.get('u_sequenceNoInput')
        digit_num = request.POST.get('u_digitNumInput')
        rule = request.POST.get('u_ruleSelect')
        content = request.POST.get('u_contentInput')
        remark = request.POST.get('u_remarkInput')

        # 进行数据校验
        if not all([id, sequence_no, digit_num, rule]):
            # 数据不完整
            return False, '数据不完整！', [], 0
        vin_rule = VinRule.objects.get(id=vin_rule_id)

        try:
            obj = VinRuleItem.objects.filter_without_isdelete().filter(vin_rule=vin_rule).exclude(id=id).get(sequence_no=sequence_no)
        except VinRuleItem.DoesNotExist:
            obj = None

        if not obj:
            item = VinRuleItem.objects.get(id=id)
            item.sequence_no = sequence_no
            item.digit_num = digit_num
            item.rule = rule
            item.content = content if content else None
            item.remark = remark if remark else None
            item.save()
            return True, '', [], 0
        else:
            return False, '序列号不能重复！', [], 0







