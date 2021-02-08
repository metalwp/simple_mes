import json
import os
import xlrd
import re

from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse, JsonResponse
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt

from apps.product_manager.models import ProductModel
from apps.bom_manager.models import MaterialModel, BOM, Bom_MaterialModel
from apps.order_manager.models import Order
from apps.process_manager.models import ProcessStep, ProcessStep_MaterialModel
from simple_mes import settings

# Create your views here.


def index(request):
    products = ProductModel.objects.filter_without_isdelete().all()
    # boms = BOM.objects.filter_without_isdelete()
    user = request.user
    if user.is_authenticated:
        return render(request, "bom_manager/index.html", locals())
    else:
        request.session['errMsg'] = '请先登陆！'
        return redirect(reverse('account:login'))


def getBomData(request):
    model = BOM
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
            total = model.objects.filter_without_isdelete().count()
            objs = model.objects.filter_without_isdelete().order_by(sort_str)[(pageNumber - 1) * pageSize:(pageNumber) * pageSize]
        else:
            objs = model.objects.filter_without_isdelete().filter(Q(product_model__name__contains=search_kw)).order_by(sort_str) \
                        [(pageNumber - 1) * pageSize: pageNumber * pageSize]
            # 获取查询结果的总条数
            total = model.objects.filter_without_isdelete().filter(Q(product_model__name__contains=search_kw)).order_by(sort_str) \
                        [(pageNumber - 1) * pageSize: pageNumber * pageSize].count()
        rows = []
        data = {"total": total, "rows": rows}
        for obj in objs:
            if not obj.product_model.is_delete:
                rows.append({"id": obj.id,
                             'erp_no': obj.erp_no,
                             'product_name': obj.product_model.name,
                             'model_name': obj.product_model.model,
                             'bom_version': obj.version,
                             'remark': obj.remark})
        return JsonResponse(data)


def addBomData(request):
    model = BOM
    if request.method == "POST":
        # 获取前端数据
        product_id = request.POST.get('productSelect')
        version = request.POST.get('versionInput')
        remark = request.POST.get('remarkText')
        erp_no = request.POST.get('erpInput')

        # 数据校验
        if not all([product_id, version, erp_no]):
            return JsonResponse({"ret": False, "errMsg": '数据不能为空！', "rows": [], "total": 0})
        # 校验版本格式
        if not re.match(r'^V(\d{1,2})\.(\d{3})$', version):
            return JsonResponse({"ret": False, "errMsg": '版本格式不正确！', "rows": [], "total": 0})
        # 校验物料号格式
        if not re.match(r'^[A-Z]\d{9}V\d{4}A$', erp_no):
            return JsonResponse({"ret": False, "errMsg": '物料号格式不正确！', "rows": [], "total": 0})

        # 业务逻辑    
        try:
            product_model = ProductModel.objects.get(id=product_id)
            orders = Order.objects.filter_without_isdelete().filter(product_model=product_model)
            for order in orders:
                if order.status == 0 or order.status == 1:
                    return_dict = {"ret": False, "errMsg": '该产品存在未完成的订单，不能修改BOM！', "rows": [], "total": 0}
                    return HttpResponse(json.dumps(return_dict))

            steps = ProcessStep.objects.filter_without_isdelete().filter(process_route=product_model.process_route) \
                .filter(category=1)
            for step in steps:
                ships = ProcessStep_MaterialModel.objects.filter(process_step=step)
                for ship in ships:
                    ship.delete()

            boms = BOM.objects.filter_without_isdelete().filter(erp_no=erp_no)
            if boms:
                return JsonResponse({"ret": False, "errMsg": '该ERP号已经使用！', "rows": [], "total": 0})
            model.objects.create(product_model=product_model,
                                 version=version,
                                 erp_no=erp_no,
                                 remark=remark)
        except Exception as e:
            return_dict = {"ret": False, "errMsg": str(e), "rows": [], "total": 0}
            return JsonResponse(return_dict)

        return_dict = {"ret": True, "errMsg": "", "rows": [], "total": 0}
        #返回响应
        return JsonResponse(return_dict)


def updateBomData(request):
    model = BOM
    if request.method == 'POST':
        id = request.POST.get('u_idInput')
        product_id = request.POST.get('u_productSelect')
        version = request.POST.get('u_versionInput')
        remark = request.POST.get('u_remarkText')
        erp_no = request.POST.get('u_erpInput')

         # 数据校验
        if not all([id, product_id, version, erp_no]):
            return JsonResponse({"ret": False, "errMsg": '数据不能为空！', "rows": [], "total": 0})
        # 校验版本格式
        if not re.match(r'^V(\d{1,2})\.(\d{3})$', version):
            return JsonResponse({"ret": False, "errMsg": '版本格式不正确！', "rows": [], "total": 0})
        # 校验物料号格式
        if not re.match(r'^[A-Z]\d{9}V\d{4}A$', erp_no):
            return JsonResponse({"ret": False, "errMsg": '物料号格式不正确！', "rows": [], "total": 0})

        try:
            product = ProductModel.objects.get(id=product_id)
            orders = Order.objects.filter_without_isdelete().filter(product_model=product)
            for order in orders:
                if order.status == 0 or order.status == 1:
                    return_dict = {"ret": False, "errMsg": '该产品存在未完成的订单，不能修改BOM！', "rows": [], "total": 0}
                    return HttpResponse(json.dumps(return_dict))

            steps = ProcessStep.objects.filter_without_isdelete().filter(process_route=product.process_route) \
                .filter(category=1)
            for step in steps:
                ships = ProcessStep_MaterialModel.objects.filter(process_step=step)
                for ship in ships:
                    ship.delete()
            mat, created = model.objects.update_or_create(id=id, defaults={"product_model": product,
                                                                            "version": version,
                                                                            "remark": remark})
        except Exception as e:
            return_dict = {"ret": False, "errMsg": str(e), "rows": [], "total": 0}
            return JsonResponse(return_dict)


        return_dict = {"ret": True, "errMsg": '', "rows": [], "total": 0}
        return JsonResponse(return_dict)


def deleteBomData(request):
        model = BOM
        id = request.POST.get('id')
        try:
            bom = model.objects.get(id=id)
        except Exception as e:
            return_dict = {"ret": True, "errMsg": str(e), "rows": [], "total": 0}
            return JsonResponse(return_dict)
        orders = Order.objects.filter_without_isdelete().filter(product_model=bom.product_model)
        for order in orders:
            if order.status == 0 or order.status == 1:
                return_dict = {"ret": False, "errMsg": '该产品存在未完成的订单，不能修改BOM！', "rows": [], "total": 0}
                return HttpResponse(json.dumps(return_dict))

        steps = ProcessStep.objects.filter_without_isdelete().filter(process_route=bom.product_model.process_route) \
            .filter(category=1)
        for step in steps:
            ships = ProcessStep_MaterialModel.objects.filter(process_step=step)
            for ship in ships:
                ship.delete()

        bom.delete()
        return_dict = {"ret": True, "errMsg": "", "rows": [], "total": 0}
        return JsonResponse(return_dict)


def detail(request, bom_id):
    bom = BOM.objects.get(id=bom_id)
    bom_id = bom_id
    product = bom.product_model
    categorys = MaterialModel.CATEGORY_CHOICE
    user = request.user
    if user.is_authenticated:
        return render(request, 'bom_manager/detail.html', locals())
    else:
        request.session['errMsg'] = '请先登陆！'
        return redirect(reverse('account:login'))


def get(request, bom_id):
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

        bom = BOM.objects.filter_without_isdelete().get(pk=bom_id)
        if not search_kw:
            total = bom.bom_materialmodel_set.all().count()
            ships = bom.bom_materialmodel_set.all().order_by(sort_str)[(pageNumber - 1) * pageSize:(pageNumber) * pageSize]
        else:
            total = bom.bom_materialmodel_set.filter(Q(material_model__name__contains=search_kw) |\
                                                     Q(material_model__erp_no__contains=search_kw)).count()
            ships = bom.bom_materialmodel_set.filter(Q(material_model__name__contains=search_kw)
                                                     |Q(material_model__erp_no__contains=search_kw)).order_by(sort_str) \
                                                    [(pageNumber - 1) * pageSize:(pageNumber) * pageSize]
        rows = []
        for ship in ships:
            rows.append({'id': ship.material_model.id, 
                        'name': ship.material_model.name,
                        'model': ship.material_model.model,
                        'erp_no': ship.material_model.erp_no,
                        'category': ship.material_model.category,
                        'quantity': ship.quantity,
                        'is_traced': ship.material_model.is_traced,
                        'c_time': ship.material_model.c_time.strftime("%Y-%m-%d-%H:%M:%S"),
                        'm_time': ship.material_model.m_time.strftime("%Y-%m-%d-%H:%M:%S")})

        data = {"total": total, "rows": rows}
        # print(data)
        return JsonResponse(data)


def writeToDB(filename, bom_id):
    bom = BOM.objects.filter_without_isdelete().get(pk=bom_id)
    excel = xlrd.open_workbook(settings.UPLOAD_ROOT + "/" + filename)
    sheet = excel.sheet_by_name('部件清单')
    nrows = sheet.nrows
    ncols = sheet.ncols
    # print(nrows, ncols)
    category_choice = MaterialModel.CATEGORY_CHOICE
    tmp_list = [x[1] for x in category_choice]
    materials_list = []
    for i in range(1, nrows):
        row = sheet.row_values(i)
        erp_no = row[1].strip()
        if (not erp_no) or (not re.match(r'^[A-Z]\d{9}V\d{4}A$', erp_no)):
            raise Exception("excel文档的第" + str(i+1) + "存在异常！")
        name = str(row[2]).replace(" ", "").strip()
        model = str(row[3]).replace(" ", "").strip()
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

    ships = Bom_MaterialModel.objects.filter(bom=bom)
    for ship in ships:
        ship.delete()

    for mat in materials_list:
        try:
            material, created = MaterialModel.objects.update_or_create(erp_no=mat[0], defaults={"name": mat[1],
                                                                                                "model": mat[2],
                                                                                                "category": mat[3],
                                                                                                'is_traced': mat[4]})
            Bom_MaterialModel.objects.create(bom=bom, material_model=material, quantity=mat[5])
        except Exception as e:
            raise e

        # if not created:
        #     try:
        #         ship = material.bom_materialmodel_set.get(bom=bom)
        #     except Bom_MaterialModel.DoesNotExist:
        #         ship = None
        # if ship:
        #     ship.quantity = mat[5]
        #     ship.save()
        # else:
        #     Bom_MaterialModel.objects.create(bom=bom, material_model=material, quantity=mat[5])

        
def upload(request, bom_id):
    file = request.FILES.get('uploadFile')

    bom = BOM.objects.filter_without_isdelete().get(id=bom_id)
    orders = Order.objects.filter_without_isdelete().filter(product_model=bom.product_model)
    for order in orders:
        if order.status == 0 or order.status == 1:
            return_dict = {"ret": False, "errMsg": '该产品存在未完成的订单，不能修改BOM！', "rows": [], "total": 0}
            return HttpResponse(json.dumps(return_dict))

    steps = ProcessStep.objects.filter_without_isdelete().filter(process_route=bom.product_model.process_route) \
        .filter(category=1)
    for step in steps:
        ships = ProcessStep_MaterialModel.objects.filter(process_step=step)
        for ship in ships:
            ship.delete()

    if not os.path.exists(settings.UPLOAD_ROOT):
        os.makedirs(settings.UPLOAD_ROOT)
    try:
        if file is None:
            return_dict = {"ret": False, "errMsg": '请选择文件', "rows": [], "total": 0}
            return HttpResponse(json.dumps(return_dict))
        with open(settings.UPLOAD_ROOT + "/" + file.name, 'wb') as f:
            for i in file.readlines():
                f.write(i)

        writeToDB(file.name, bom_id)

        return_dict = {"ret": True, "errMsg": "", "rows": [], "total": 0}
        return HttpResponse(json.dumps(return_dict))
    except Exception as e:
        return_dict = {"ret": False, "errMsg": str(e), "rows": [], "total": 0}
        return HttpResponse(json.dumps(return_dict))


def delete(request, bom_id):
    bom = BOM.objects.filter_without_isdelete().get(id=bom_id)
    orders = Order.objects.filter_without_isdelete().filter(product_model=bom.product_model)
    for order in orders:
        if order.status == 0 or order.status == 1:
            return_dict = {"ret": False, "errMsg": '存在未完成的订单，不能修改BOM！', "rows": [], "total": 0}
            return HttpResponse(json.dumps(return_dict))
    material_id = request.POST.get('id')  # 获取的物料id
    ships = Bom_MaterialModel.objects.filter(bom__id=bom_id, material_model__id=material_id)
    if len(ships)==1:
        ships[0].delete()
    else:
        return_dict = {"ret": False, "errMsg": '该物料查询异常！', "rows": [], "total": 0}
        return JsonResponse(return_dict)

    return_dict = {"ret": True, "errMsg": "", "rows": [], "total": 0}
    return JsonResponse(return_dict)


def add(request, bom_id):
    if request.method == "POST":
        name = request.POST.get('nameInput')
        model = request.POST.get('modelText')
        category = request.POST.get('categorySelect')
        erp_no = request.POST.get('erpInput')
        quantity = request.POST.get('quantityInput')
        trace = request.POST.get('traceInput')

        bom = BOM.objects.filter_without_isdelete().get(id=bom_id)
        orders = Order.objects.filter_without_isdelete().filter(product_model=bom.product_model)
        for order in orders:
            if order.status == 0 or order.status == 1:
                return_dict = {"ret": False, "errMsg": '存在未完成的订单，不能修改BOM！', "rows": [], "total": 0}
                return HttpResponse(json.dumps(return_dict))

        # 数据校验
        if not all([name, model, category, erp_no, quantity]):
            return JsonResponse({"ret": False, "errMsg": '数据不能为空！', "rows": [], "total": 0})
        # 校验物料号格式
        if not re.match(r'^[A-Z]\d{9}V\d{4}A$', erp_no):
            return JsonResponse({"ret": False, "errMsg": '物料号格式不正确！', "rows": [], "total": 0})
        if float(quantity) < 1:
            return JsonResponse({"ret": False, "errMsg": '用量应大于1 ！', "rows": [], "total": 0})

        if category:
            category = int(category)
        else:
            category = 0
        quantity = float(request.POST.get('quantityInput'))
        if trace == 'on':
            is_traced = True
        else:
            is_traced = False

        try:
            obj = MaterialModel.objects.filter_without_isdelete().get(erp_no=erp_no)
        except MaterialModel.DoesNotExist:
            obj = None
        try:
            bom = BOM.objects.filter_without_isdelete().get(pk=bom_id)
            if not obj:
                obj = MaterialModel.objects.create(name=name, model=model, category=category, erp_no=erp_no)
            obj.bom.add(bom)
        except Exception as e:
            return_dict = {"ret": False, "errMsg": str(e), "rows": [], "total": 0}
            return HttpResponse(json.dumps(return_dict))
        return_dict = {"ret": True, "errMsg": "", "rows": [], "total": 0}
        return HttpResponse(json.dumps(return_dict))


def update(request, bom_id):
    if request.method == "POST":
        id = request.POST.get('u_idInput')
        name = request.POST.get('u_nameInput')
        model = request.POST.get('u_modelText')
        category = request.POST.get('u_categorySelect')
        erp_no = request.POST.get('u_erpInput')
        quantity = request.POST.get('u_quantityInput')
        trace = request.POST.get('u_traceInput')

        bom = BOM.objects.filter_without_isdelete().get(id=bom_id)
        orders = Order.objects.filter_without_isdelete().filter(product_model=bom.product_model)
        for order in orders:
            if order.status == 0 or order.status == 1:
                return_dict = {"ret": False, "errMsg": '存在未完成的订单，不能修改BOM！', "rows": [], "total": 0}
                return HttpResponse(json.dumps(return_dict))

        # 数据校验
        if not all([id, name, model, category, erp_no, quantity]):
            return JsonResponse({"ret": False, "errMsg": '数据不能为空！', "rows": [], "total": 0})
        # 校验物料号格式
        if not re.match(r'^[A-Z]\d{9}V\d{4}A$', erp_no):
            return JsonResponse({"ret": False, "errMsg": '物料号格式不正确！', "rows": [], "total": 0})
        if float(quantity) < 1:
            return JsonResponse({"ret": False, "errMsg": '用量应大于1！', "rows": [], "total": 0})
        
        if request.POST.get('u_categorySelect'):
            category = int(request.POST.get('u_categorySelect'))
        else:
            category = 0
        quantity = float(quantity)
        if trace == 'on':
            is_traced = True
        else:
            is_traced = False
        try:
            obj = MaterialModel.objects.filter_without_isdelete().get(id=id)
            obj.name = name
            obj.model = model
            obj.category = category
            obj.erp_no = erp_no
            obj.quantity = quantity
            obj.is_traced = is_traced
            obj.save()
        except Exception as e:
            return_dict = {"ret": False, "errMsg": str(e), "rows": [], "total": 0}
            return HttpResponse(json.dumps(return_dict))
        return_dict = {"ret": True, "errMsg": "", "rows": [], "total": 0}
        return HttpResponse(json.dumps(return_dict))



















































