import json

from django.shortcuts import render, redirect, reverse
from django.http import JsonResponse
from django.db.models import Q

from apps.product_manager.models import ProductModel
from apps.station_manager.models import Station, Fixture
from apps.process_manager.models import ProcessStep, ProcessRoute, ProcessStep_MaterialModel
from apps.bom_manager.models import MaterialModel, Bom_MaterialModel

# Create your views here.


def ps_index(request):
    fixtures = Fixture.objects.filter_without_isdelete()
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
        obj = model.objects.get(id=id)
        obj.delete()
        return JsonResponse(return_dict)
    except Exception as e:
        return_dict = {"ret": False, "errMsg": str(e), "rows": [], "total": 0}
        return JsonResponse(return_dict)


def addPSData(request):
    if request.method == "POST":
        name = request.POST.get('nameInput')
        fixture_id = request.POST.get('fixtureSelect')
        remark = request.POST.get('remarkText')
        if request.POST.get('lockInput') == 'on':
            lock = True
        else:
            lock = False
        try:
            fixture = Fixture.objects.get(id=fixture_id)
        except Exception:
            fixture = None
        try:
            ProcessStep.objects.create(name=name, fixture=fixture, process_lock=lock, remark=remark)
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
        if request.POST.get('u_lockInput') == 'on':
            lock = True
        else:
            lock = False
        try:
            fixture = Fixture.objects.get(id=fixture_id)
            step = ProcessStep.objects.get(id=id)
            step.name = name
            step.fixture = fixture
            step.process_lock = lock
            step.remark = remark
            step.save()
        except Exception as e:
            return_dict = {"ret": False, "errMsg": str(e), "rows": [], "total": 0}
            return JsonResponse(return_dict)
        return_dict = {"ret": True, "errMsg": "", "rows": [], "total": 0}
        return JsonResponse(return_dict)


def ps_detail(request, step_id):
    step = ProcessStep.objects.get(pk=step_id)
    route = step.process_route
    if not route:
        return redirect(reverse('process_manager:ps_index'), aaa='1231')
    productmodel = route.productmodel_set.all().first()
    if not productmodel:
        return redirect(reverse('process_manager:ps_index'), aaa='1231')
    bom = productmodel.bom
    ships = Bom_MaterialModel.objects.filter(bom=bom, material_model__is_traced=True)
    # ships = Bom_MaterialModel.objects.filter(is_traced=True).values_list('material_model', 'id').distinct()
    # for ship in ships:
    #     print(ship)
    # materials = MaterialModel.objects.filter(bom_materialmodel__is_traced=True).values_list('erp_no', 'name', ).distinct()
    # for material in materials:
    #     print(material)
    categorys = MaterialModel.CATEGORY_CHOICE
    return render(request, "process_manager/ps_detail.html", locals())


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
            step = ProcessStep.objects.get(id=step_id)
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
            step1 = ProcessStep.objects.get(id=step_id)
            material = MaterialModel.objects.get(id=material_id)
            route = step1.process_route
            steps = ProcessStep.objects.filter(process_route=route)
            count = float(quantity)
            for step in steps:
                ships = ProcessStep_MaterialModel.objects.filter(process_step=step, material_model=material)
                for ship in ships:
                    count += float(ship.quantity)

            productmodel = route.productmodel_set.all().first()
            bom = productmodel.bom
            ship = Bom_MaterialModel.objects.filter(bom=bom, material_model=material).first()
            if count > float(ship.quantity):
                return_dict = {"ret": False, "errMsg": '输入用量超过BOM总用量！', "rows": [], "total": 0}
                return JsonResponse(return_dict)

            obj = ProcessStep_MaterialModel.objects.create(process_step=step1, material_model=material, quantity=quantity)
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
            model.objects.create(name=name, remark=remark)
        except Exception as e:
            return JsonResponse({"ret": False, "errMsg": str(e), "rows": [], "total": 0})
        return_dict = {"ret": True, "errMsg": "", "rows": [], "total": 0}
        return JsonResponse(return_dict)


def deletePRData(request):
    return_dict = {"ret": True, "errMsg": "", "rows": [], "total": 0}
    id = request.POST.get('id')
    try:
        obj = ProcessRoute.objects.get(id=id)
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
            obj = model.objects.get(id=id)
            obj.name = name
            obj.remark = remark
            obj.save()
        except Exception as e:
            return_dict = {"ret": False, "errMsg": str(e), "rows": [], "total": 0}
            return JsonResponse(return_dict)
        return_dict = {"ret": True, "errMsg": "", "rows": [], "total": 0}
        return JsonResponse(return_dict)


def pr_detail(request, route_id):
    route = ProcessRoute.objects.get(pk=route_id)
    steps = ProcessStep.objects.filter_without_isdelete().filter(process_route=None)
    selected_steps = ProcessStep.objects.filter_without_isdelete().filter(process_route=route).order_by('sequence_no')
    return render(request, "process_manager/pr_detail.html", locals())


def pr_edit(request, route_id):
    if request.method == "POST":
        receive_data = json.loads(request.body.decode())
        print(receive_data)
        try:
            route = ProcessRoute.objects.get(id=route_id)
            steps = ProcessStep.objects.filter_without_isdelete().filter(process_route=route)
            for step in steps:
                step.sequence_no=None
                step.process_route=None
                step.save()
        except Exception as e:
            return_dict = {"ret": False, "errMsg": str(e), "rows": [], "total": 0}
            return JsonResponse(return_dict)

        for data in receive_data:
            sequence_no = data['seq']
            name = data['step_name']
            try:
                step = ProcessStep.objects.get(name=name)
                step.process_route = route
                step.sequence_no = sequence_no
                step.save()
            except Exception as e:
                return_dict = {"ret": False, "errMsg": str(e), "rows": [], "total": 0}
                return JsonResponse(return_dict)

        return_dict = {"ret": True, "errMsg": "", "rows": [], "total": 0}
        return JsonResponse(return_dict)
