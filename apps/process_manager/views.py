import json
import xlrd
import os

from django.shortcuts import render, redirect, reverse
from django.http import JsonResponse, HttpResponse
from django.db.models import Q
from django.core import serializers
from django.contrib.auth.decorators import login_required

from apps.product_manager.models import ProductModel
from apps.station_manager.models import Station, Fixture
from apps.process_manager.models import ProcessStep, ProcessRoute, ProcessStep_MaterialModel
from apps.bom_manager.models import MaterialModel, Bom_MaterialModel, BOM
from apps.Inspection.models import Inspection
from apps.account.models import Menu, Permission
from simple_mes import settings

# Create your views here.


@login_required
def ps_index(request):
    fixtures = Fixture.objects.filter_without_isdelete()
    categorys = ProcessStep.CATEGORY_CHOICE
    if request.session.get('err'):
        errMsg = request.session.get('err')
    return render(request, 'process_manager/ps_index.html', locals())


def getPSData(request):
    model = ProcessStep
    if request.method == "GET":
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
            objs = model.objects.filter_without_isdelete().filter(Q(name__contains=search_kw)).order_by(sort_str) \
                [(pageNumber - 1) * pageSize: pageNumber * pageSize]
            # 获取查询结果的总条数
            total = model.objects.filter_without_isdelete().filter(Q(name__contains=search_kw)).order_by(sort_str) \
                [(pageNumber - 1) * pageSize: pageNumber * pageSize].count()

        rows = []
        data = {"total": total, "rows": rows}
        if request.session.get('err'):
            request.session['err'] = None
        for obj in objs:
            if not obj.fixture:
                fixture = None
            else:
                fixture = obj.fixture.name
            if not obj.process_route:
                route = None
            else:
                route = obj.process_route.name
            rows.append({'id': obj.id,
                         'name': obj.name,
                         'fixture': fixture,
                         'sequence_no': obj.sequence_no,
                         'process_lock': obj.process_lock,
                         'category': obj.category,
                         'process_route': route,
                         'remark': obj.remark,
                         'c_time': obj.c_time.strftime("%Y-%m-%d-%H:%M:%S"),
                         'm_time': obj.m_time.strftime("%Y-%m-%d-%H:%M:%S")})
        return JsonResponse(data)


def deletePSData(request):
    model = ProcessStep
    return_dict = {"ret": True, "errMsg": "", "rows": [], "total": 0}
    id = request.POST.get('id')
    try:
        obj = model.objects.filter_without_isdelete().get(id=id)
    except Exception as e:
        return_dict = {"ret": False, "errMsg": str(e), "rows": [], "total": 0}
        return JsonResponse(return_dict)

    if obj.category == 1 or obj.category == 3 or obj.category == 4 or obj.category == 5 or obj.category == 6:
        try:
            parent = Menu.objects.get(title="生产过程")
            menu = Menu.objects.get(title=obj.name, parent=parent)
            permission = Permission.objects.get(title=obj.name)
            menu.delete()
            permission.delete()
        except Exception as e:
            print(e)
    obj.sequence_no = None
    obj.delete()

    return JsonResponse(return_dict)


def addPSData(request):
    if request.method == "POST":
        name = request.POST.get('nameInput')
        fixture_id = request.POST.get('fixtureSelect')
        remark = request.POST.get('remarkText')
        category = request.POST.get('categorySelect')
        if request.POST.get('lockInput') == 'on':
            lock = True
        else:
            lock = False
        try:
            fixture = Fixture.objects.filter_without_isdelete().get(id=fixture_id)
        except Exception:
            fixture = None

        try:
            tmp = ProcessStep.objects.filter_without_isdelete().filter(name=name)
            if tmp:
                return_dict = {"ret": False, "errMsg": "工序名称不能重复！", "rows": [], "total": 0}
                return JsonResponse(return_dict)

            step = ProcessStep.objects.create(name=name, fixture=fixture, process_lock=lock, remark=remark,
                                              category=category)
            if step.category == "1" or step.category == "3" or step.category == "4" \
                    or step.category == "5" or step.category == "6":
                parent = Menu.objects.get(title="生产过程")
                menu = Menu.objects.create(title=name, icon=None, parent=parent)
                Permission.objects.create(title=name, url=("/manufacturing/assemble/" + str(step.id) + "/"), menu=menu, parent=None)
        except Exception as e:
            return_dict = {"ret": False, "errMsg": str(e), "rows": [], "total": 0}
            return JsonResponse(return_dict)

        return_dict = {"ret": True, "errMsg": "", "rows": [], "total": 0}
        return JsonResponse(return_dict)


def updatePSData(request):
    if request.method == "POST":
        id = request.POST.get('u_idInput')
        name = request.POST.get('u_nameInput')
        fixture_id = request.POST.get('u_fixtureSelect')
        remark = request.POST.get('u_remarkText')
        category = request.POST.get('u_categorySelect')

        if request.POST.get('u_lockInput') == 'on':
            lock = True
        else:
            lock = False
        try:
            if fixture_id:
                fixture = Fixture.objects.filter_without_isdelete().get(id=fixture_id)
            else:
                fixture = None
            tmp = ProcessStep.objects.filter_without_isdelete().filter(name=name).exclude(id=id)
            if tmp:
                return_dict = {"ret": False, "errMsg": "工序名称不能重复！", "rows": [], "total": 0}
                return JsonResponse(return_dict)
            step = ProcessStep.objects.filter_without_isdelete().get(id=id)
        except Exception as e:
            return_dict = {"ret": False, "errMsg": str(e), "rows": [], "total": 0}
            return JsonResponse(return_dict)
        if step.category == 1 or step.category == 3 or step.category == 4 \
                or step.category == 5 or step.category == 6:
            try:
                parent = Menu.objects.get(title="生产过程")
                menu = Menu.objects.get(title=step.name, parent=parent)
                permission = Permission.objects.get(title=step.name)
                menu.title = name
                menu.save()
                permission.title = name
                permission.save()
            except Exception as e:
                print(e)
        step.name = name
        step.fixture = fixture
        step.process_lock = lock
        step.remark = remark
        step.category = category
        step.save()

        return_dict = {"ret": True, "errMsg": "", "rows": [], "total": 0}
        return JsonResponse(return_dict)


@login_required
def ps_detail(request, step_id):
    step = ProcessStep.objects.filter_without_isdelete().get(pk=step_id)
    route = step.process_route
    steps = ProcessStep.objects.filter_without_isdelete().filter(process_route=route, category=1)

    if not route:
        request.session['err'] = '该工序未与工艺路线关联！'
        return redirect(reverse('process_manager:ps_index'))

    productmodel = route.productmodel_set.all().first()

    if not productmodel:
        request.session['err'] = '该工艺路线未与产品关联！'
        return redirect(reverse('process_manager:ps_index'))
    bom = BOM.objects.filter_without_isdelete().filter(product_model=productmodel).order_by('-erp_no').first()
    ships = Bom_MaterialModel.objects.filter(bom=bom, material_model__is_traced=True)
    # for step in steps:
    #     ship2s = ProcessStep_MaterialModel.objects.filter(process_step=step)
    #     for ship2 in ship2s:
    #         ship1s.get(material_model=ship2.material_model).quantity

    material_categorys = MaterialModel.CATEGORY_CHOICE

    if step.category == 1:  # 装配工序
        return render(request, "process_manager/assembly_step_detail.html", locals())
    elif step.category == 2:  # 测试工序
        request.session['err'] = '该工序无配置项！'
        return redirect(reverse('process_manager:ps_index'))
    elif step.category == 3 or step.category == 4:  # 标定/检验工序
        inspection_categorys = Inspection.CATEGORY_CHOICE
        inspection_modes = Inspection.MODE_CHOICE
        return render(request, "process_manager/inspect_step_detail.html", locals())
    elif step.category == 5:  # 标签打印工序
        return HttpResponse('后续添加标签模板导入')
    elif step.category == 6:  # VIN生成工序
        return redirect(reverse('product_manager:VinRuleItemIndex', args=[productmodel.id]))
    else:
        return HttpResponse('无')


def getMaterialDate(request, step_id):
    if request.method == "GET":
        pageSize = int(request.GET.get('pageSize'))
        pageNumber = int(request.GET.get('pageNumber'))
        sortName = request.GET.get('sortName')
        sortOrder = request.GET.get('sortOrder')
        search_kw = request.GET.get('search_kw')

        if sortOrder == 'asc':
            sort_str = sortName
        else:
            sort_str = '-' + sortName
        try:
            step = ProcessStep.objects.filter_without_isdelete().get(id=step_id)
        except Exception as e:
            return_dict = {"ret": False, "errMsg": str(e), "rows": [], "total": 0}
            return JsonResponse(return_dict)

        if not search_kw:
            total = step.processstep_materialmodel_set.all().count()
            ships = step.processstep_materialmodel_set.all().order_by(sort_str)[
                   (pageNumber - 1) * pageSize:(pageNumber) * pageSize]
        else:
            total = step.processstep_materialmodel_set.filter(Q(material_model__name__contains=search_kw)).count()
            ships = step.processstep_materialmodel_set.filter(Q(material_model__name__contains=search_kw)).order_by(sort_str)[
                    (pageNumber - 1) * pageSize:(pageNumber) * pageSize]

        rows = []
        data = {"total": total, "rows": rows}
        for ship in ships:

            rows.append({'id': ship.id,
                         'erp_no': ship.material_model.erp_no,
                         'name': ship.material_model.name,
                         'category': ship.material_model.category,
                         'model': ship.material_model.model,
                         'quantity': ship.quantity,
                         })
        return JsonResponse(data)


def addMaterialDate(request, step_id):
    if request.method == "POST":
        material_id = request.POST.get('materialSelect')
        quantity = request.POST.get('quantityInput')

        if not all([material_id, quantity]):
            return_dict = {"ret": False, "errMsg": '输入信息不能为空！', "rows": [], "total": 0}
            return JsonResponse(return_dict)

        try:
            step1 = ProcessStep.objects.filter_without_isdelete().get(id=step_id)
            material = MaterialModel.objects.filter_without_isdelete().get(id=material_id)
            route = step1.process_route
            steps = ProcessStep.objects.filter(process_route=route)
            count = float(quantity)
            for step in steps:
                ships = ProcessStep_MaterialModel.objects.filter(process_step=step, material_model=material)
                for ship in ships:
                    count += float(ship.quantity)

            productmodel = ProductModel.objects.filter_without_isdelete().get(process_route=route)
            # bom = BOM.objects.filter_without_isdelete().get(product_model=productmodel)
            bom = BOM.objects.filter_without_isdelete().filter(product_model=productmodel).order_by("-erp_no").first()
            ship = Bom_MaterialModel.objects.filter(bom=bom, material_model=material).first()
            if count > float(ship.quantity):
                return_dict = {"ret": False, "errMsg": '输入用量超过BOM总用量！', "rows": [], "total": 0}
                return JsonResponse(return_dict)


            try:
                obj = ProcessStep_MaterialModel.objects.get(process_step=step1, material_model=material)
                obj.quantity = float(obj.quantity) + float(quantity)
                obj.save()
            except ProcessStep_MaterialModel.DoesNotExist:
                obj = ProcessStep_MaterialModel.objects.create(process_step=step1, material_model=material,
                                                               quantity=quantity)

        except Exception as e:
            return_dict = {"ret": False, "errMsg": str(e), "rows": [], "total": 0}
            return JsonResponse(return_dict)

        return_dict = {"ret": True, "errMsg": "", "rows": [], "total": 0}
        return JsonResponse(return_dict)


def deleteMaterialDate(request, step_id):
    return_dict = {"ret": True, "errMsg": "", "rows": [], "total": 0}
    id = request.POST.get('id')
    try:
        obj = ProcessStep_MaterialModel.objects.get(id=id)
        obj.delete()
        return JsonResponse(return_dict)
    except Exception as e:
        return_dict = {"ret": False, "errMsg": str(e), "rows": [], "total": 0}
        return JsonResponse(return_dict)


def refresh_options(request, step_id):
    if request.method == "POST":
        step = ProcessStep.objects.filter_without_isdelete().get(pk=step_id)
        route = step.process_route
        steps = ProcessStep.objects.filter_without_isdelete().filter(process_route=route, category=1)
        productmodel = ProductModel.objects.filter_without_isdelete().get(process_route=route)
        bom = BOM.objects.filter_without_isdelete().filter(product_model=productmodel).order_by("-erp_no").first()
        ship1s = Bom_MaterialModel.objects.filter(bom=bom, material_model__is_traced=True)
        ship1s_list = list(ship1s)
        ship2s_list = []
        for s in steps:
            ship2s = ProcessStep_MaterialModel.objects.filter(process_step=s)
            if ship2s:
                ship2s_list = ship2s_list + list(ship2s)
        for ship2 in ship2s_list:
            for ship1 in ship1s_list:
                if ship1.material_model == ship2.material_model:
                    ship1.quantity = ship1.quantity - ship2.quantity
                    if ship1.quantity == 0:
                        ship1s_list.remove(ship1)
        list1 = []
        for ship1 in ship1s_list:
            list1.append({'id': ship1.material_model.id,
                          'erp_no': ship1.material_model.erp_no,
                          'quantity': float(ship1.quantity),
                          'name': ship1.material_model.name})
        qs_json = json.dumps(list1)
        return HttpResponse(qs_json, content_type='application/json')


def getInspectionData(request, step_id):
    model = Inspection
    if request.method == "GET":
        pageSize = int(request.GET.get('pageSize'))
        pageNumber = int(request.GET.get('pageNumber'))
        sortName = request.GET.get('sortName')
        sortOrder = request.GET.get('sortOrder')
        search_kw = request.GET.get('search_kw')

        try:
            process_step = ProcessStep.objects.filter_without_isdelete().get(id=step_id)
        except Exception as e:
            return_dict = {"ret": False, "errMsg": str(e), "rows": [], "total": 0}
            return JsonResponse(return_dict)

        if not search_kw:
            total = model.objects.filter_without_isdelete().filter(process_step=process_step).count()
            objs = model.objects.filter_without_isdelete().filter(process_step=process_step)[
                   (pageNumber - 1) * pageSize:(pageNumber) * pageSize]
        else:
            objs = model.objects.filter_without_isdelete().filter(process_step=process_step).filter(Q(name__contains=search_kw)) \
                [(pageNumber - 1) * pageSize: pageNumber * pageSize]
            # 获取查询结果的总条数
            total = model.objects.filter_without_isdelete().filter(process_step=process_step).filter(Q(name__contains=search_kw)) \
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


def addInspectionData(request, step_id):
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
            process_step = ProcessStep.objects.filter_without_isdelete().get(id=step_id)

            Inspection.objects.create(num=num,
                                      name=name,
                                      upper=upper,
                                      lower=lower,
                                      process_step=process_step,
                                      category=category,
                                      mode=mode)
        except Exception as e:
            return JsonResponse({"ret": False, "errMsg": str(e), "rows": [], "total": 0})
        return_dict = {"ret": True, "errMsg": "", "rows": [], "total": 0}
        return JsonResponse(return_dict)


def updateInspectionData(request, step_id):
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
            obj = Inspection.objects.filter_without_isdelete().get(id=id)
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


def deleteInspectionData(request, step_id):
    return_dict = {"ret": True, "errMsg": "", "rows": [], "total": 0}
    id = request.POST.get('id')
    try:
        obj = Inspection.objects.filter_without_isdelete().get(id=id)
        obj.delete()
        return JsonResponse(return_dict)
    except Exception as e:
        return_dict = {"ret": False, "errMsg": str(e), "rows": [], "total": 0}
        return JsonResponse(return_dict)


def writeToDB(**kwargs):
    filename = kwargs.get('filename')
    step_id = kwargs.get('step_id')
    excel = xlrd.open_workbook(settings.UPLOAD_ROOT + "/" + filename)
    sheet = excel.sheet_by_name('检验标准')
    nrows = sheet.nrows
    ncols = sheet.ncols
    c_list = Inspection.CATEGORY_CHOICE
    m_list = Inspection.MODE_CHOICE

    try:
        process_step = ProcessStep.objects.filter_without_isdelete().get(id=step_id)
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
    old_teststandards = Inspection.objects.filter_without_isdelete().filter(process_step=process_step)
    for old in old_teststandards:
        old.delete()

    for obj in obj_list:
        try:
            Inspection.objects.create(num=obj[0], name=obj[1], category=obj[2], mode=obj[3], upper=obj[4], lower=obj[5],
                                      process_step=process_step)
        except Exception as e:
            raise e


def uploadInspection(request, step_id):
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
        writeToDB(filename=file.name, step_id=step_id)
        return_dict = {"ret": True, "errMsg": "", "rows": [], "total": 0}
        return HttpResponse(json.dumps(return_dict))
    except Exception as e:
        return_dict = {"ret": False, "errMsg": str(e), "rows": [], "total": 0}
        return HttpResponse(json.dumps(return_dict))


@login_required
def pr_index(request):
    product = ProductModel.objects.all()
    return render(request, "process_manager/pr_index.html", locals())




def getPRData(request):
    model = ProcessRoute
    if request.method == "GET":
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
            objs = model.objects.filter_without_isdelete().filter(Q(name__contains=search_kw)).order_by(sort_str) \
                [(pageNumber - 1) * pageSize: pageNumber * pageSize]
            # 获取查询结果的总条数
            total = model.objects.filter_without_isdelete().filter(Q(name__contains=search_kw)).order_by(sort_str) \
                [(pageNumber - 1) * pageSize: pageNumber * pageSize].count()
        rows = []
        data = {"total": total, "rows": rows}
        for obj in objs:
            rows.append({'id': obj.id, 
                                        'name': obj.name,
                                        'remark': obj.remark,
                                        'm_time': obj.m_time.strftime("%Y-%m-%d-%H:%M:%S"), 
                                         'c_time': obj.c_time.strftime("%Y-%m-%d-%H:%M:%S"),
                                        })
        return JsonResponse(data)


def addPRData(request):
    model = ProcessRoute
    if request.method == "POST":
        name = request.POST.get('nameInput')
        remark = request.POST.get('remarkText')
        # 数据校验
        if not name:
            return JsonResponse({"ret": False, "errMsg": '数据不能为空！', "rows": [], "total": 0})
        try:
            tmp = model.objects.filter_without_isdelete().filter(name=name)
            if tmp:
                return_dict = {"ret": False, "errMsg": "工艺路线名称不能重复！", "rows": [], "total": 0}
                return JsonResponse(return_dict)
            model.objects.create(name=name, remark=remark)
        except Exception as e:
            return JsonResponse({"ret": False, "errMsg": str(e), "rows": [], "total": 0})
        return_dict = {"ret": True, "errMsg": "", "rows": [], "total": 0}
        return JsonResponse(return_dict)


def deletePRData(request):
    return_dict = {"ret": True, "errMsg": "", "rows": [], "total": 0}
    id = request.POST.get('id')
    try:
        obj = ProcessRoute.objects.filter_without_isdelete().get(id=id)
        obj.delete()
        return JsonResponse(return_dict)
    except Exception as e:
        return_dict = {"ret": False, "errMsg": str(e), "rows": [], "total": 0}
        return JsonResponse(return_dict)


def updatePRData(request):
    model = ProcessRoute
    if request.method == 'POST':
        id = request.POST.get('u_idInput')
        name = request.POST.get('u_nameInput')
        remark = request.POST.get('u_remarkText')
        
        # 数据校验
        if not all([name,  id]):
            return JsonResponse({"ret": False, "errMsg": '数据不能为空！', "rows": [], "total": 0})
        
        try:
            tmp = model.objects.filter_without_isdelete().filter(name=name)
            if tmp:
                return_dict = {"ret": False, "errMsg": "工艺路线名称不能重复！", "rows": [], "total": 0}
                return JsonResponse(return_dict)
            obj = model.objects.filter_without_isdelete().get(id=id)
            obj.name = name
            obj.remark = remark
            obj.save()
        except Exception as e:
            return_dict = {"ret": False, "errMsg": str(e), "rows": [], "total": 0}
            return JsonResponse(return_dict)
        return_dict = {"ret": True, "errMsg": "", "rows": [], "total": 0}
        return JsonResponse(return_dict)


@login_required
def pr_detail(request, route_id):
    route = ProcessRoute.objects.filter_without_isdelete().get(pk=route_id)
    steps = ProcessStep.objects.filter_without_isdelete().filter(process_route=None)
    selected_steps = ProcessStep.objects.filter_without_isdelete().filter(process_route=route).order_by('sequence_no')

    return render(request, "process_manager/pr_detail.html", locals())


def pr_edit(request, route_id):
    if request.method == "POST":
        receive_data = json.loads(request.body.decode())
        try:
            route = ProcessRoute.objects.filter_without_isdelete().get(id=route_id)
            steps = ProcessStep.objects.filter_without_isdelete().filter(process_route=route)
            for step in steps:
                step.sequence_no = None
                step.process_route = None
                step.save()
        except Exception as e:
            return_dict = {"ret": False, "errMsg": str(e), "rows": [], "total": 0}
            return JsonResponse(return_dict)

        for data in receive_data:
            sequence_no = data['seq']
            name = data['step_name']
            try:
                step = ProcessStep.objects.filter_without_isdelete().get(name=name)
                step.process_route = route
                step.sequence_no = sequence_no
                step.save()
            except Exception as e:
                return_dict = {"ret": False, "errMsg": str(e), "rows": [], "total": 0}
                return JsonResponse(return_dict)

        return_dict = {"ret": True, "errMsg": "", "rows": [], "total": 0}
        return JsonResponse(return_dict)
