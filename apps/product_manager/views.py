import json

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q


from .models import ProductModel, ProductCategory
from apps.process_manager.models import ProcessRoute


# Create your views here.


def pc_index(request):
    product_category = ProductCategory.objects.all()
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
            total = ProductCategory.objects.all().count()
            categorys = ProductCategory.objects.all().order_by(sort_str)[(pageNumber - 1) * pageSize:(pageNumber) * pageSize]
        else:
            categorys = ProductCategory.objects.filter(Q(name__contains=search_kw)).order_by(sort_str) \
                        [(pageNumber - 1) * pageSize:(pageNumber) * pageSize]
            # 获取查询结果的总条数
            total = ProductCategory.objects.filter(Q(name__contains=search_kw)).order_by(sort_str) \
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
            catagory = ProductCategory.objects.get(id=_id)
            # category = get_object_or_404(ProductCategory, id=_id)
            catagory.delete()
        except Exception as e:
            return JsonResponse({"ret": False, "errMsg": str(e), "rows": [], "total": 0})

        # 返回应答
        return JsonResponse({"ret": True, "errMsg": '', "rows": [], "total": 0})


def pm_index(request):
    products = ProductModel.objects.all()
    categorys = ProductCategory.objects.all()
    process_routes = ProcessRoute.objects.all()
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
            total = ProductModel.objects.all().count()
            products = ProductModel.objects.order_by(sort_str)[(pageNumber - 1) * pageSize:(pageNumber) * pageSize]
        else:
            products = ProductModel.objects.filter(Q(name__contains=search_kw)).order_by(sort_str) \
                        [(pageNumber - 1) * pageSize: pageNumber * pageSize]
            # 获取查询结果的总条数
            total = ProductModel.objects.filter(Q(name__contains=search_kw)).order_by(sort_str) \
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

        if category_id:
            try:
                category = ProductCategory.objects.get(id=category_id)
            except Exception as e:
                return JsonResponse({"ret": False, "errMsg": str(e), "rows": [], "total": 0})
        else:
            category = None

        if process_route_id:
            try:
                process_route = ProcessRoute.objects.get(id=process_route_id)
            except Exception as e:
                return JsonResponse({"ret": False, "errMsg": str(e), "rows": [], "total": 0})
        else:
            process_route = None
        try:
            product = ProductModel(name=name, model=modal, erp_no=erp_no, category=category,
                                   process_route=process_route)
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
        erp_no = request.POST.get('erpInputUpdate')
        category_id = request.POST.get('categorySelectUpdate')
        process_route_id = request.POST.get('processRouteSelectUpdate')
        print(request.POST)

        # 校验数据有效性
        if not all([name, model, erp_no]):
            return JsonResponse({"ret": False, "errMsg": '数据不能为空！', "rows": [], "total": 0})

        # 业务处理
        if category_id:
            category = get_object_or_404(ProductCategory, id=category_id)
        else:
            category = None

        if process_route_id:
            process_route = get_object_or_404(ProcessRoute, id=process_route_id)
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
            product = ProductModel.objects.get(id=_id)
            # category = get_object_or_404(ProductCategory, id=_id)
            product.delete()
        except Exception as e:
            return JsonResponse({"ret": False, "errMsg": str(e), "rows": [], "total": 0})

        # 返回应答
        return JsonResponse({"ret": True, "errMsg": '', "rows": [], "total": 0})












