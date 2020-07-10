import json
import os
import xlrd

from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt


from product_manager.models import ProductModel
from bom_manager.models import MaterialModel
from simple_mes import settings

# Create your views here.


def index(request):
    product = ProductModel.objects.all()
    return render(request, "bom_manager/index.html", locals())


def detail(request, product_id):
    product = ProductModel.objects.get(pk=product_id)
    categorys = MaterialModel.category_choice
    return render(request, 'bom_manager/detail.html', locals())


def getMaterials(request, product_id):
    if request.method == 'GET':
        pageSize = int(request.GET.get('pageSize'))
        pageNumber = int(request.GET.get('pageNumber'))
        sortName = request.GET.get('sortName')
        sortOrder = request.GET.get('sortOrder')
        search_kw = request.GET.get('search_kw')
        product = ProductModel.objects.get(pk=product_id)
        if not search_kw:
            total = product.materialmodel_set.all().count()
            materials = product.materialmodel_set.order_by('id')[(pageNumber - 1) * pageSize:(pageNumber) * pageSize]
        else:
            # 获取查询结果的总条数
            total = product.materialmodel_set.filter(Q(name__contains=search_kw)) \
                        [(pageNumber - 1) * pageSize:(pageNumber) * pageSize].count()
            materials = product.materialmodel_set.filter(Q(name__contains=search_kw)) \
                        [(pageNumber - 1) * pageSize:(pageNumber) * pageSize]
        rows = []
        data = {"total": total, "rows": rows}

        for material in materials:
                rows.append({'id': material.id, 'name': material.name,
                             'model': material.model,  'erp_no': material.erp_no,
                             'category': material.category, 'quantity': material.quantity,
                             'is_traced': material.is_traced,
                             'c_time': str(material.c_time), 'm_time': str(material.m_time)})
        return HttpResponse(json.dumps(data), content_type="application/json")
    else:
        return HttpResponse('Error!')


def writeToDB(filename, product_id):
    product = ProductModel.objects.get(pk=product_id)
    excel = xlrd.open_workbook(settings.UPLOAD_ROOT + "/" + filename)
    sheet = excel.sheet_by_name('部件清单')
    nrows = sheet.nrows
    ncols = sheet.ncols
    category_choice = MaterialModel.category_choice
    tmp_list = [x[1] for x in category_choice]
    materials_list = []
    for i in range(1, nrows):
        row = sheet.row_values(i)
        erp_no = row[1].strip()
        name = row[2].strip()
        model = row[3].strip()
        if not row[4].strip():
            category = 0
        elif row[4].strip() not in tmp_list or row[4].strip() == '其他':
            category = 7
        else:
            for choice in category_choice:
                if row[4] == choice[1]:
                    category = choice[0]
                    break
        if row[5].strip() == '是':
            is_traced = True
        else:
            is_traced = False
        quantity = row[6]
        if materials_list:
            if erp_no in [x[0] for x in materials_list]:
                for material in materials_list:
                    if erp_no == material[0]:
                        material[5] = material[5] + quantity
                        break
            else:
                materials_list.append([erp_no, name, model, category, is_traced, quantity])

        else:
            materials_list.append([erp_no, name, model, category, is_traced, quantity])
    for mat in materials_list:
        try:
            material, created = MaterialModel.objects.update_or_create(erp_no=erp_no,
                                                               defaults={"product_model": product, "bom_version": '-',
                                                                         "name": mat[1], "model": mat[2],
                                                                        "category": mat[3], "quantity": mat[5],
                                                                        "is_traced": mat[4]})
        except Exception as e:
            print(e)
            return HttpResponse(e)


def upload(request, product_id):

    file = request.FILES.get('uploadFile')

    if not os.path.exists(settings.UPLOAD_ROOT):
        os.makedirs(settings.UPLOAD_ROOT)
    try:
        if file is None:
            return_dict = {"ret": False, "errMsg": '请选择文件', "rows": [], "total": 0}
            return HttpResponse(json.dumps(return_dict))
        with open(settings.UPLOAD_ROOT + "/" + file.name, 'wb') as f:
            for i in file.readlines():
                f.write(i)
        writeToDB(file.name, product_id)
    except Exception as e:
        print(e)
        return_dict = {"ret": False, "errMsg": str(e), "rows": [], "total": 0}
        return HttpResponse(json.dumps(return_dict))

    return_dict = {"ret": True, "errMsg": "", "rows": [], "total": 0}
    return HttpResponse(json.dumps(return_dict))


@csrf_exempt
def delete(request, product_id):
    return_dict = {"ret": True, "errMsg": "", "rows": [], "total": 0}
    _id = request.POST.get('id')
    material = MaterialModel.objects.get(id=_id)
    material.delete()
    return HttpResponse(json.dumps(return_dict))
