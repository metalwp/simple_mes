from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.db.models import Q
from django.http import JsonResponse

from station_manager.models import Station

# Create your views here.


class IndexView(ListView):
    """视图类"""
    model = Station
    template_name = "station_manager/index.html"
    context_object_name = 'stations'

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['categorys'] = self.model.station_category_choice
        return context

    # def get_queryset(self):
    #     print(self.request.GET.dict())
    #     if self.request.GET:
    #         pageSize = int(self.request.GET.get('pageSize'))
    #         pageNumber = int(self.request.GET.get('pageNumber'))
    #         sortName = self.request.GET.get('sortName')
    #         sortOrder = self.request.GET.get('sortOrder')
    #         search_kw = self.request.GET.get('search_kw')
    #         if search_kw:
    #             total = self.model._default_manager.all().count()
    #             stations = self.model._default_manager.order_by('id')[
    #                        (pageNumber - 1) * pageSize:(pageNumber) * pageSize]
    #         else:
    #             stations = self.model._default_manager.filter(Q(station_name__contains=search_kw)) \
    #                 [(pageNumber - 1) * pageSize: pageNumber * pageSize]
    #             # 获取查询结果的总条数
    #             total = self.model._default_manager.filter(Q(station_name__contains=search_kw)) \
    #                 [(pageNumber - 1) * pageSize: pageNumber * pageSize].count()
    #         rows = []
    #         data = {"total": total, "rows": rows}
    #         for station in stations:
    #             rows.append({'id': station.id, 'station_no': station.station_no, 'station_name': station.station_name,
    #                          'station_category': station.station_category, 'c_time': station.c_time,
    #                          'm_time': station.m_time, 'remarks': station.remarks})
    #         return JsonResponse(data)
    #     else:
    #         return super(IndexView, self).get_queryset()


def getData(request):
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
            total = Station.objects.all().count()
            stations = Station.objects.all().order_by(sort_str)[
                       (pageNumber - 1) * pageSize:(pageNumber) * pageSize]
        else:
            stations = Station.objects.filter(Q(station_name__contains=search_kw)).order_by(sort_str) \
                [(pageNumber - 1) * pageSize: pageNumber * pageSize]
            # 获取查询结果的总条数
            total = Station.objects.filter(Q(station_name__contains=search_kw)).order_by(sort_str) \
                [(pageNumber - 1) * pageSize: pageNumber * pageSize].count()
        rows = []
        data = {"total": total, "rows": rows}
        for station in stations:
            rows.append({'id': station.id, 'station_no': station.station_no, 'station_name': station.station_name,
                         'station_category': station.station_category, 'c_time': station.c_time.strftime("%Y-%m-%d-%H:%M:%S"),
                         'm_time': station.m_time.strftime("%Y-%m-%d-%H:%M:%S"), 'remarks': station.remarks})
        return JsonResponse(data)


def deleteData(request):
    return_dict = {"ret": True, "errMsg": "", "rows": [], "total": 0}
    id = request.POST.get('id')
    try:
        station = Station.objects.get(id=id)
        station.delete()
        return JsonResponse(return_dict)
    except Exception as e:
        return_dict = {"ret": False, "errMsg": str(e), "rows": [], "total": 0}
        return JsonResponse(return_dict)

category_choice = ((0, 'NON'),
                               (1, 'IQC'),
                               (2, 'IQC'),
                               (3, 'EOL'),
                               (4, 'ASY'),
                               (5, 'PQC'),
                               (6, 'OQC'),
                               (7, 'WHS'))

def addData(request):
    if request.method == "POST":
        name = request.POST.get('nameInput')
        category_id = request.POST.get('categorySelect')
        remarks = request.POST.get('remarksText')
        try:
            cate_str = ''
            for choice in category_choice:
                if int(category_id) == choice[0]:
                    cate_str = choice[1]
                    break
            station_no = genStationNo(cate_str)
            Station.objects.create(station_no=station_no, station_name=name,
                                   station_category=category_id, remarks=remarks)
        except Exception as e:
            return_dict = {"ret": False, "errMsg": str(e), "rows": [], "total": 0}
            return JsonResponse(return_dict)

        return_dict = {"ret": True, "errMsg": "", "rows": [], "total": 0}
        return JsonResponse(return_dict)


def updateData(request):
    if request.method == 'POST':
        id = request.POST.get('idUpdateInput')
        station_name = request.POST.get('nameUpdateInput')
        station_category = request.POST.get('categoryUpdateSelect')
        remarks = request.POST.get('remarksUpdateText')
        station = Station.objects.get(id=id)

        if station_category != station.station_category:
            print(11111)
            cate_str = ''
            for choice in category_choice:
                if int(station_category) == choice[0]:
                    cate_str = choice[1]
                    break
            station_no = genStationNo(cate_str)
            station.station_no = station_no
        station.station_name = station_name
        station.remarks = remarks
        station.station_category = station_category
        station.save()
        return_dict = {"ret": True, "errMsg": "", "rows": [], "total": 0}
        return JsonResponse(return_dict)


def genStationNo(cate_str):
    """生成工站号"""
    station = Station.objects.filter(station_no__contains=cate_str).order_by("-c_time").first()
    if station:
        serial_number = int(station.station_no[3:]) + 1
    else:
        serial_number = 1
    station_no = cate_str + "{0:03d}".format(serial_number)  # EOL001
    return station_no