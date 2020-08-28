import json

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q


from .models import ProductModel, ProductCategory


# Create your views here.


def pc_index(request):
    product_category = ProductCategory.objects.all()

    return render(request, 'product_manager/pc_index.html', locals())


def getPcData(request):
    if request.method == 'GET':
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
            categorys = ProductCategory.objects.order_by(sort_str)[(pageNumber - 1) * pageSize:(pageNumber) * pageSize]
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
                rows.append({'id': category.id, 'category_name': category.name, 'parent_category': category.parent.name,
                             'c_time': category.c_time.strftime("%Y-%m-%d %H:%M:%S"), 'm_time': category.m_time.strftime("%Y-%m-%d %H:%M:%S")})
            else:
                rows.append({'id': category.id, 'category_name': category.name,
                             'parent_category': None,
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
        id = request.POST.get('update_id')
        c_name = request.POST.get('update_c_name')
        p_id = request.POST.get('update_p_name')
        if p_id:
            parent = get_object_or_404(ProductCategory, id=p_id)
            pc, created = ProductCategory.objects.update_or_create(id=id, defaults={'name': c_name,
                                                                                    'parent': parent})
        else:
            pc, created = ProductCategory.objects.update_or_create(id=id,
                                                                   defaults={'name': c_name,
                                                                             'parent': None})
        return HttpResponse(json.dumps({'status': 'success'}))


def deletePcData(request):
    return_dict = {"ret": True, "errMsg": "", "rows": [], "total": 0}
    _id = request.POST.get('id')
    catagory = ProductCategory.objects.get(id=_id)
    # category = get_object_or_404(ProductCategory, id=_id)
    catagory.delete()
    return HttpResponse(json.dumps(return_dict))


def pm_index(request):
    products = ProductModel.objects.all()
    categorys = ProductCategory.objects.all()
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
            products = ProductModel.objects.filter(Q(product_name__contains=search_kw)).order_by(sort_str) \
                        [(pageNumber - 1) * pageSize: pageNumber * pageSize]
            # 获取查询结果的总条数
            total = ProductModel.objects.filter(Q(product_name__contains=search_kw)).order_by(sort_str) \
                        [(pageNumber - 1) * pageSize: pageNumber * pageSize].count()
        rows = []
        data = {"total": total, "rows": rows}
        for product in products:
            if product.category:
                rows.append({'id': product.id, 'erp_no': product.erp_no, 'product_name': product.product_name, 'model_name': product.model_name,
                             'category': product.category.name, 'bom_version': product.bom_version,
                             'c_time': product.c_time.strftime("%Y-%m-%d %H:%M:%S"), 'm_time': product.m_time.strftime("%Y-%m-%d %H:%M:%S")})
            else:
                rows.append({'id': product.id, 'erp_no': product.erp_no, 'name': product.product_name, 'model': product.model_name,
                             'category': None, 'bom_version': product.bom_version,
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
        bom_version = request.POST.get('bomversionInput')

        if category_id:
            category = ProductCategory.objects.get(id=category_id)
            product = ProductModel(product_name=name, model_name=modal, erp_no=erp_no, category=category,
                                   bom_version=bom_version)
            product.save()
        else:
            product = ProductModel(product_name=name, model_name=modal, erp_no=erp_no, category=None,
                                   bom_version=bom_version)
            product.save()

        return HttpResponse(json.dumps({'status': 'success'}))


def updatePmData(request):
    if request.method == "POST":
        id = request.POST.get('idInputUpdate')
        name = request.POST.get('nameInputUpdate')
        model = request.POST.get('modelInputUpdate')
        erp_no = request.POST.get('erpInputUpdate')
        category_id = request.POST.get('categorySelectUpdate')
        bom_version = request.POST.get('bomversionUpdate')

        if category_id:
            category = get_object_or_404(ProductCategory, id=category_id)
            pc, created = ProductModel.objects.update_or_create(id=id, defaults={'product_name': name,
                                                                                 'model_name': model,
                                                                                 'category': category,
                                                                                 'erp_no': erp_no,
                                                                                 'bom_version': bom_version})
        else:
            pc, created = ProductModel.objects.update_or_create(id=id, defaults={'product_name': name,
                                                                                 'model_name': model,
                                                                                 'category': None,
                                                                                 'erp_no': erp_no,
                                                                                 'bom_version': bom_version})
        return HttpResponse(json.dumps({'status': 'success'}))


def deletePmData(request):
    return_dict = {"ret": True, "errMsg": "", "rows": [], "total": 0}
    _id = request.POST.get('id')
    product = ProductModel.objects.get(id=_id)
    product.delete()
    return HttpResponse(json.dumps(return_dict))















