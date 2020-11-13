import json
import re

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.contrib.auth.decorators import login_required

from .models import ProductModel, ProductCategory
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
                rows.append({'id': category.id, 'name': category.name, 'parent': category.parent.name,
                             'c_time': category.c_time.strftime("%Y-%m-%d %H:%M:%S"), 'm_time': category.m_time.strftime("%Y-%m-%d %H:%M:%S")})
            else:
                rows.append({'id': category.id, 'name': category.name,
                             'parent': None,
                             'c_time': category.c_time.strftime("%Y-%m-%d %H:%M:%S"), 'm_time': category.m_time.strftime("%Y-%m-%d %H:%M:%S")})
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
            rows.append({'id': product.id, 'erp_no': product.erp_no, 'name': product.name, 'model': product.model,
                         'category': category, 'process_route': process_route,
                         'c_time': product.c_time.strftime("%Y-%m-%d %H:%M:%S"), 'm_time': product.m_time.strftime("%Y-%m-%d %H:%M:%S")})

        return HttpResponse(json.dumps(data), content_type="application/json")
    else:
        return HttpResponse('Error!')


def addPmData(request):
    if request.method == "POST":
        name = request.POST.get('nameInput')
        modal = request.POST.get('modalInput')
        erp_no = request.POST.get('erpInput')
        category_id = request.POST.get('categorySelect')
        process_route_id = request.POST.get('processRouteSelect')

        if not all([name, modal, erp_no]):
            return JsonResponse({"ret": False, "errMsg": '数据不能为空！', "rows": [], "total": 0})
        # 校验物料号格式
        if not re.match(r'^[A-Z]\d{9}V\d{4}A$', erp_no):
            return JsonResponse({"ret": False, "errMsg": '物料号格式不正确！', "rows": [], "total": 0})

        if category_id:
            try:
                category = ProductCategory.objects.filter_without_isdelete().get(id=category_id)
            except Exception as e:
                return JsonResponse({"ret": False, "errMsg": str(e), "rows": [], "total": 0})
        else:
            category = None

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
            product_model = ProductModel.objects.filter_without_isdelete().get(erp_no=erp_no)
        except ProductModel.DoesNotExist:
            product_model = None
        if product_model is None:
            try:
                product = ProductModel(name=name, model=modal, erp_no=erp_no, category=category,
                                       process_route=process_route)
                product.save()
            except Exception as e:
                return JsonResponse({"ret": False, "errMsg": str(e), "rows": [], "total": 0})

            # 返回应答
            return JsonResponse({"ret": True, "errMsg": '', "rows": [], "total": 0})
        else:
            return JsonResponse({"ret": False, "errMsg": "该产品型号已存在！", "rows": [], "total": 0})


def updatePmData(request):
    if request.method == "POST":
        # 收取前端数据
        id = request.POST.get('idInputUpdate')
        name = request.POST.get('nameInputUpdate')
        model = request.POST.get('modelInputUpdate')
        erp_no = request.POST.get('erpInputUpdate')
        category_id = request.POST.get('categorySelectUpdate')
        process_route_id = request.POST.get('processRouteSelectUpdate')

        # 校验数据有效性
        if not all([name, model, erp_no]):
            return JsonResponse({"ret": False, "errMsg": '数据不能为空！', "rows": [], "total": 0})

        # 业务处理
        if category_id:
            category = get_object_or_404(ProductCategory, id=category_id)
        else:
            category = None

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
            pm, created = ProductModel.objects.update_or_create(id=id, defaults={'name': name,
                                                                                 'model': model,
                                                                                 'category': category,
                                                                                 'erp_no': erp_no,
                                                                                 'process_route': process_route})
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
                product_model.delete()
                for bom in boms:
                    bom.delete()
                # 返回应答
                return JsonResponse({"ret": True, "errMsg": '', "rows": [], "total": 0})

        except Exception as e:
            return JsonResponse({"ret": False, "errMsg": str(e), "rows": [], "total": 0})














