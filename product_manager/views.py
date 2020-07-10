import json

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q


from .models import ProductModel, ProductCategory


# Create your views here.


def pc_index(request):
    product_category = ProductCategory.objects.all()
    return render(request, 'product_manager/pc_index.html', locals())


@csrf_exempt
def getPcData(request):
    if request.method == 'GET':
        pageSize = int(request.GET.get('pageSize'))
        pageNumber = int(request.GET.get('pageNumber'))
        # searchText = request.GET.get('searchText')
        sortName = request.GET.get('sortName')
        sortOrder = request.GET.get('sortOrder')
        search_kw = request.GET.get('search_kw')
        if not search_kw:
            total = ProductCategory.objects.all().count()
            categorys = ProductCategory.objects.order_by('id')[(pageNumber - 1) * pageSize:(pageNumber) * pageSize]
        else:
            categorys = ProductCategory.objects.filter(Q(category_name__contains=search_kw)) \
                        [(pageNumber - 1) * pageSize:(pageNumber) * pageSize]
            # 获取查询结果的总条数
            total = ProductCategory.objects.filter(Q(category_name__contains=search_kw)) \
                        [(pageNumber - 1) * pageSize:(pageNumber) * pageSize].count()
        rows = []
        data = {"total": total, "rows": rows}
        for category in categorys:
            if category.parent_category:
                rows.append({'id': category.id, 'name': category.category_name, 'parent': category.parent_category.category_name,
                             'c_time': str(category.c_time), 'm_time': str(category.m_time)})
            else:
                rows.append({'id': category.id, 'name': category.category_name,
                             'parent': None,
                             'c_time': str(category.c_time), 'm_time': str(category.m_time)})
        return HttpResponse(json.dumps(data), content_type="application/json")
    else:
        return HttpResponse('Error!')


@csrf_exempt
def addPcData(request):
    if request.method == "POST":
        c_name = request.POST.get('c_name')
        p_id = request.POST.get('p_name')
        if p_id:
            parent = ProductCategory.objects.get(id=p_id)
            category = ProductCategory(category_name=c_name, parent_category=parent)
            category.save()
        else:
            category = ProductCategory(category_name=c_name, parent_category=None)
            category.save()

        return HttpResponse(json.dumps({'status': 'success'}))


@csrf_exempt
def updatePcData(request):
    if request.method == "POST":
        id = request.POST.get('update_id')
        c_name = request.POST.get('update_c_name')
        p_id = request.POST.get('update_p_name')
        if p_id:
            parent = get_object_or_404(ProductCategory, id=p_id)
            pc, created = ProductCategory.objects.update_or_create(id=id, defaults={'category_name': c_name,
                                                                                    'parent_category': parent})
        else:
            pc, created = ProductCategory.objects.update_or_create(id=id,
                                                                   defaults={'category_name': c_name,
                                                                             'parent_category': None})
        return HttpResponse(json.dumps({'status': 'success'}))


@csrf_exempt
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


@csrf_exempt
def getPmData(request):
    if request.method == 'GET':
        pageSize = int(request.GET.get('pageSize'))
        pageNumber = int(request.GET.get('pageNumber'))
        sortName = request.GET.get('sortName')
        sortOrder = request.GET.get('sortOrder')
        search_kw = request.GET.get('search_kw')
        if not search_kw:
            total = ProductModel.objects.all().count()
            products = ProductModel.objects.order_by('id')[(pageNumber - 1) * pageSize:(pageNumber) * pageSize]
        else:
            products = ProductModel.objects.filter(Q(product_name__contains=search_kw)) \
                        [(pageNumber - 1) * pageSize: pageNumber * pageSize]
            # 获取查询结果的总条数
            total = ProductModel.objects.filter(Q(product_name__contains=search_kw)) \
                        [(pageNumber - 1) * pageSize: pageNumber * pageSize].count()
        rows = []
        data = {"total": total, "rows": rows}
        for product in products:
            if product.category:
                rows.append({'id': product.id, 'erp_no': product.erp_no, 'name': product.product_name, 'model': product.model_name,
                             'category': product.category.category_name, 'bom_version': product.bom_version,
                             'c_time': str(product.c_time), 'm_time': str(product.m_time)})
            else:
                rows.append({'id': product.id, 'erp_no': product.erp_no, 'name': product.product_name, 'model': product.model_name,
                             'category': None, 'bom_version': product.bom_version,
                             'c_time': str(product.c_time), 'm_time': str(product.m_time)})
        return HttpResponse(json.dumps(data), content_type="application/json")
    else:
        return HttpResponse('Error!')


@csrf_exempt
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


@csrf_exempt
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


@csrf_exempt
def deletePmData(request):
    return_dict = {"ret": True, "errMsg": "", "rows": [], "total": 0}
    _id = request.POST.get('id')
    product = ProductModel.objects.get(id=_id)
    product.delete()
    return HttpResponse(json.dumps(return_dict))





















# def pc_create(request):
#     if request.method == "GET":
#         product_category_now = ProductCategory.objects.all()
#         return render(request, 'product_manager/pc_create.html', locals())
#     elif request.method == "POST":
#         if request.POST.get('submit_btn') == '保存':
#             _category_name = request.POST.get('category_name')
#             _parent_id = request.POST.get('parent_category_id')
#             if _parent_id:
#                 _parent = ProductCategory.objects.get(id=_parent_id)
#                 if _parent.category_name != _category_name:
#                     pc, created = ProductCategory.objects.update_or_create(category_name=_category_name,
#                                                                            defaults={'parent_category': _parent})
#                 else:
#                     return HttpResponse('None')
#             else:
#                 pc, created = ProductCategory.objects.update_or_create(category_name=_category_name,
#                                                                        defaults={'parent_category': None})
#             return redirect('/product_category/pc_index/')
#         else:
#             return redirect('/product_category/pc_index/')


# def pc_detail(request, category_id):
#     if request.method == 'GET':
#         category = get_object_or_404(ProductCategory, id=category_id)
#         parent = ProductCategory.objects.all()
#         return render(request, 'product_manager/pc_detail.html', locals())
#     elif request.method == "POST":
#         if request.POST.get('submit_btn') == '保存':
#             _category_id = int(request.path_info[-2])
#             _category_name = request.POST.get('category_name')
#             _parent_id = request.POST.get('parent_category_id')
#             print(_category_name)
#             print(_parent_id)
#
#             if _parent_id:
#                 _parent = ProductCategory.objects.get(id=_parent_id)
#                 print(_parent.category_name)
#                 if _parent.category_name != _category_name:
#                     pc, created = ProductCategory.objects.update_or_create(id=_category_id,
#                                                                            defaults={'category_name': _category_name,
#                                                                                      'parent_category': _parent})
#                 else:
#                     return HttpResponse('None')
#             else:
#                 pc, created = ProductCategory.objects.update_or_create(id=_category_id,
#                                                                        defaults={'category_name': _category_name,
#                                                                                  'parent_category': None})
#             return redirect('/product_category/pc_index/')
#         else:
#             return redirect('/product_category/pc_index/')


