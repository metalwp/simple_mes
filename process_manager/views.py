import json

from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Q

from product_manager.models import ProductModel
from station_manager.models import Station
from process_manager.models import ProcessStep

# Create your views here.


def ps_index(request):
    stations = Station.objects.all()
    return render(request, 'process_manager/ps_index.html', locals())


def getPSData(request):
    if request.method == "GET":
        pageSize = int(request.GET.get('pageSize'))
        pageNumber = int(request.GET.get('pageNumber'))
        sortName = request.GET.get('sortName')
        sortOrder = request.GET.get('sortOrder')
        search_kw = request.GET.get('search_kw')
        model = ProcessStep
        if sortOrder == 'asc':
            sort_str = sortName
        else:
            sort_str = '-' + sortName
        if not search_kw:
            total = model.objects.all().count()
            objs = model.objects.all().order_by(sort_str)[
                       (pageNumber - 1) * pageSize:(pageNumber) * pageSize]
        else:
            objs = model.objects.filter(Q(step_name__contains=search_kw)).order_by(sort_str) \
                [(pageNumber - 1) * pageSize: pageNumber * pageSize]
            # 获取查询结果的总条数
            total = model.objects.filter(Q(step_name__contains=search_kw)).order_by(sort_str) \
                [(pageNumber - 1) * pageSize: pageNumber * pageSize].count()
        rows = []
        data = {"total": total, "rows": rows}
        for obj in objs:
            rows.append({'id': obj.id, 'step_name': obj.step_name, 'station': obj.station.station_name,
                         'process_lock': obj.process_lock, 'c_time': obj.c_time.strftime("%Y-%m-%d-%H:%M:%S"),
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
        name = request.POST.get('psNameInput')
        station_id = request.POST.get('stationSelect')
        
        if request.POST.get('lockInput') == 'on':
            lock = True
        else:
            lock = False

        try:
            station = Station.objects.get(id=station_id)
            ProcessStep.objects.create(step_name=name, station=station, process_lock=lock)
        except Exception as e:
            return_dict = {"ret": False, "errMsg": str(e), "rows": [], "total": 0}
            return JsonResponse(return_dict)

        return_dict = {"ret": True, "errMsg": "", "rows": [], "total": 0}
        return JsonResponse(return_dict)


def updatePSData(request):
    if request.method == "POST":
        id = request.POST.get('idUpdateInput')
        step_name = request.POST.get('psNameUpdateInput')
        station_id = request.POST.get('stationUpdateSelect')
        if request.POST.get('lockUpdateInput') == 'on':
            lock = True
        else:
            lock = False
        try:
            station = Station.objects.get(id=station_id)
            step = ProcessStep.objects.get(id=id)
            step.step_name = step_name
            step.station = station
            step.process_lock = lock
            step.save()
            return_dict = {"ret": True, "errMsg": "", "rows": [], "total": 0}
            return JsonResponse(return_dict)
        except Exception as e:
            return_dict = {"ret": False, "errMsg": str(e), "rows": [], "total": 0}
            return JsonResponse(return_dict)


def pr_index(request):
    product = ProductModel.objects.all()
    return render(request, "process_manager/pr_index.html", locals())


def pr_detail(request, product_id): 
    product = ProductModel.objects.get(pk=product_id)
    steps = ProcessStep.objects.all()
    return render(request, "process_manager/pr_detail.html", locals())


def pr_edit(request, product_id):
    if request.method == "POST":
        print(request.body)
        receive_data = json.loads(request.body.decode())
        print(receive_data[0])
    return_dict = {"ret": True, "errMsg": "", "rows": [], "total": 0}
    return JsonResponse(return_dict)
