import os
import json
import xlrd
import re

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.db.models import Q

from apps.Inspection.models import Inspection, GeneralMaterial, GMInspectRecord, TraceMaterial, TMInspectRecord
from apps.bom_manager.models import MaterialModel
from simple_mes import settings

# Create your views here.


def material_index(request):
    categorys = MaterialModel.CATEGORY_CHOICE
    return render(request, 'Inspection/material_index.html', locals())


def getMaterialData(request):
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
            total = MaterialModel.objects.filter_without_isdelete().count()
            objs = MaterialModel.objects.filter_without_isdelete().order_by(sort_str)[
                    (pageNumber - 1) * pageSize:(pageNumber) * pageSize]
        else:
            total = MaterialModel.objects.filter_without_isdelete().filter(Q(name__contains=search_kw)).count()
            objs = MaterialModel.objects.filter_without_isdelete().filter(Q(name__contains=search_kw)).order_by(sort_str)[
                    (pageNumber - 1) * pageSize:(pageNumber) * pageSize]
        rows = []
        for obj in objs:
            rows.append({'id': obj.id,
                         'name': obj.name,
                         'model': obj.model,
                         'erp_no': obj.erp_no,
                         'category': obj.category,
                         })

        data = {"total": total, "rows": rows}
        return JsonResponse(data)


def material_detail(request, material_id):
    material = MaterialModel.objects.get(id=material_id)
    modes = Inspection.MODE_CHOICE
    categorys = Inspection.CATEGORY_CHOICE
    return render(request, 'Inspection/material_detail.html', locals())


def getInspectionData(request, material_id):
    model = Inspection
    if request.method == "GET":
        pageSize = int(request.GET.get('pageSize'))
        pageNumber = int(request.GET.get('pageNumber'))
        sortName = request.GET.get('sortName')
        sortOrder = request.GET.get('sortOrder')
        search_kw = request.GET.get('search_kw')

        try:
            material = MaterialModel.objects.get(id=material_id)
        except Exception as e:
            return_dict = {"ret": False, "errMsg": str(e), "rows": [], "total": 0}
            return JsonResponse(return_dict)

        if not search_kw:
            total = model.objects.filter_without_isdelete().filter(material_model=material).count()
            objs = model.objects.filter_without_isdelete().filter(material_model=material)[
                   (pageNumber - 1) * pageSize:(pageNumber) * pageSize]
        else:
            objs = model.objects.filter_without_isdelete().filter(material_model=material).filter(Q(name__contains=search_kw)) \
                [(pageNumber - 1) * pageSize: pageNumber * pageSize]
            # 获取查询结果的总条数
            total = model.objects.filter_without_isdelete().filter(material_model=material).filter(Q(name__contains=search_kw)) \
                [(pageNumber - 1) * pageSize: pageNumber * pageSize].count()
        rows = []
        data = {"total": total, "rows": rows}
        for obj in objs:
            rows.append({'id': obj.id,
                         'num': obj.num,
                         'name': obj.name,
                         'category': obj.category,
                         'mode': obj.mode,
                         'upper': obj.upper,
                         'lower': obj.lower,
                         'm_time': obj.m_time.strftime("%Y-%m-%d-%H:%M:%S"),
                         'c_time': obj.c_time.strftime("%Y-%m-%d-%H:%M:%S"),
                         })
        return JsonResponse(data)


def addInspectionData(request, material_id):
    if request.method == "POST":
        num = request.POST.get('numInput')
        name = request.POST.get('nameInput')
        category = request.POST.get('categorySelect')
        mode = request.POST.get('modeSelect')
        upper = float(request.POST.get('upperInput'))
        lower = float(request.POST.get('lowerInput'))
        # 数据校验
        if not all([num, name, category, mode, upper, lower]):
            return JsonResponse({"ret": False, "errMsg": '数据不能为空！', "rows": [], "total": 0})

        if upper < lower:
            return JsonResponse({"ret": False, "errMsg": "上限大于等于下限！", "rows": [], "total": 0})

        try:
            material = MaterialModel.objects.get(id=material_id)

            Inspection.objects.create(num=num,
                                      name=name,
                                      upper=upper,
                                      lower=lower,
                                      material_model=material,
                                      category=category,
                                      mode=mode)
        except Exception as e:
            return JsonResponse({"ret": False, "errMsg": str(e), "rows": [], "total": 0})
        return_dict = {"ret": True, "errMsg": "", "rows": [], "total": 0}
        return JsonResponse(return_dict)


def updateInspectionData(request, material_id):
    if request.method == 'POST':
        id = request.POST.get('u_idInput')
        num = request.POST.get('u_numInput')
        name = request.POST.get('u_nameInput')
        upper = float(request.POST.get('u_upperInput'))
        lower = float(request.POST.get('u_lowerInput'))
        category = request.POST.get('u_categorySelect')
        mode = request.POST.get('u_modeSelect')

        # 数据校验
        if not all([num, name, upper, lower, category, mode]):
            return JsonResponse({"ret": False, "errMsg": '数据不能为空！', "rows": [], "total": 0})
        if upper < lower:
            return JsonResponse({"ret": False, "errMsg": "上限大于等于下限！", "rows": [], "total": 0})

        try:
            obj = Inspection.objects.get(id=id)
            obj.num = num
            obj.name = name
            obj.upper = upper
            obj.lower = lower
            obj.category = category
            obj.mode = mode
            obj.save()
        except Exception as e:
            return_dict = {"ret": False, "errMsg": str(e), "rows": [], "total": 0}
            return JsonResponse(return_dict)
        return_dict = {"ret": True, "errMsg": "", "rows": [], "total": 0}
        return JsonResponse(return_dict)


def deleteInspectionData(request, material_id):
    return_dict = {"ret": True, "errMsg": "", "rows": [], "total": 0}
    id = request.POST.get('id')
    try:
        obj = Inspection.objects.get(id=id)
        obj.delete()
        return JsonResponse(return_dict)
    except Exception as e:
        return_dict = {"ret": False, "errMsg": str(e), "rows": [], "total": 0}
        return JsonResponse(return_dict)


def writeToDB(**kwargs):
    filename = kwargs.get('filename')
    material_id = kwargs.get('material_id')
    excel = xlrd.open_workbook(settings.UPLOAD_ROOT + "/" + filename)
    sheet = excel.sheet_by_name('检验标准')
    nrows = sheet.nrows
    ncols = sheet.ncols
    c_list = Inspection.CATEGORY_CHOICE
    m_list = Inspection.MODE_CHOICE

    try:
        material = MaterialModel.objects.get(id=material_id)
    except Exception as e:
        raise e

    obj_list = []
    for i in range(1, nrows):
        row = sheet.row_values(i)
        if not all([row[0], row[1], row[2], row[3], row[4], row[5]]):
            raise Exception("excel文档的第" + str(i + 1) + "存在异常！")
        num = row[0].strip()
        name = row[1].strip()
        category_str = row[2].strip()
        mode_str = row[3].strip()
        category = None
        mode = None
        for c in c_list:
            if category_str == c[1]:
                category = c[0]
                break
        for m in m_list:
            if mode_str == m[1]:
                mode = m[0]
                break
        if type(row[4]) == str:
            upper = float(row[4].strip())
        else:
            upper = row[4]
        if type(row[5]) == str:
            lower = float(row[5].strip())
        else:
            lower = row[5]

        obj_list.append([num, name, category, mode, upper, lower])
    old_teststandards = Inspection.objects.filter_without_isdelete().filter(material_model=material)
    for old in old_teststandards:
        old.delete()

    for obj in obj_list:
        try:
            Inspection.objects.create(num=obj[0], name=obj[1], category=obj[2], mode=obj[3], upper=obj[4], lower=obj[5],
                                      material_model=material)
        except Exception as e:
            raise e


def uploadInspection(request, material_id):
    file = request.FILES.get('uploadFile')

    if not os.path.exists(settings.UPLOAD_ROOT):
        os.makedirs(settings.UPLOAD_ROOT)
    try:
        if file is None:
            return_dict = {"ret": False, "errMsg": '请选择文件', "rows": [], "total": 0}
            return JsonResponse(return_dict)
        with open(settings.UPLOAD_ROOT + "/" + file.name, 'wb') as f:
            for i in file.readlines():
                f.write(i)
        writeToDB(filename=file.name, material_id=material_id)
        return_dict = {"ret": True, "errMsg": "", "rows": [], "total": 0}
        return HttpResponse(json.dumps(return_dict))
    except Exception as e:
        return_dict = {"ret": False, "errMsg": str(e), "rows": [], "total": 0}
        return HttpResponse(json.dumps(return_dict))


def gminspection_index(request):
    material_categorys = MaterialModel.CATEGORY_CHOICE
    inspection_categorys = Inspection.CATEGORY_CHOICE
    inspection_modes = Inspection.MODE_CHOICE
    return render(request, 'Inspection/gminspection_index.html', locals())


def getMaterialInfo(request):
    if request.method == "POST":
        erp_no = request.POST.get('erpInput')
        batch_num = request.POST.get('batchInput')

        if not all([erp_no, batch_num]):
            return JsonResponse({"ret": False, "errMsg": "数据不能为空！", "rows": [], "total": 0})
        if not re.match(r'^[A-Z]\d{9}V\d{4}A$', erp_no):
            return JsonResponse({"ret": False, "errMsg": '物料号格式不正确！', "rows": [], "total": 0})
        if len(batch_num) != 6:
            return JsonResponse({"ret": False, "errMsg": '批次号应为6位！', "rows": [], "total": 0})

        try:
            material_model = MaterialModel.objects.get(erp_no=erp_no, is_delete=False)
        except MaterialModel.DoesNotExist:
            return JsonResponse({"ret": False, "errMsg": '未找到此物料！', "rows": [], "total": 0})
        try:
            material = GeneralMaterial.objects.get(material_model=material_model, batch_num=batch_num)
        except GeneralMaterial.DoesNotExist:
            material = None
        batch_quantity = '' if not material else material.total_quantity
        batch_num = batch_num if not material else material.batch_num
        date = '' if not material else material.m_time
        if material:
            pass_rate = '{:.2%}'.format(material.qualified_quantity/material.total_quantity)
        else:
            pass_rate = ''

        info = {'erp_no': material_model.erp_no,
                'name': material_model.name,
                'category': material_model.category,
                'model': material_model.model,
                'batch_num': batch_num,
                'batch_quantity': batch_quantity,
                'pass_rate': pass_rate,
                'user': 'user',
                'date': date
                }
        rows = []
        data = {"ret": True, "errMsg": "", "total": 0, "rows": rows, 'info': info}

        return JsonResponse(data)


def getGMInspectionData(request):
    if request.method == "GET":
        # pageSize = int(request.POST.get('pageSize'))
        # pageNumber = int(request.POST.get('pageNumber'))
        # sortName = request.POST.get('sortName')
        # sortOrder = request.POST.get('sortOrder')
        erp_no = request.GET.get('erp_no')
        batch_num = request.GET.get('batch_num')
        try:
            material_model = MaterialModel.objects.get(erp_no=erp_no)
        except MaterialModel.DoesNotExist:
            return JsonResponse({"ret": False, "errMsg": '该物料未找到！', "rows": [], "total": 0})
        try:
            objs = Inspection.objects.filter_without_isdelete().filter(material_model=material_model)
        except Exception as e:
            return JsonResponse({"ret": False, "errMsg": str(e), "rows": [], "total": 0})

        rows = []
        data = {"ret": True, "errMsg": "", "total": 0, "rows": rows, 'info': {}}
        for obj in objs:
            rows.append({'id': obj.id,
                         'num': obj.num,
                         'name': obj.name,
                         'category': obj.category,
                         'mode': obj.mode,
                         'upper': obj.upper,
                         'lower': obj.lower,
                         'm_time': obj.m_time.strftime("%Y-%m-%d-%H:%M:%S"),
                         'c_time': obj.c_time.strftime("%Y-%m-%d-%H:%M:%S"),
                         })
        return JsonResponse(data)


def tminspection_index(request):
    pass


