import json
import os
import xlrd
import re

from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.db.models import Q
from django.http import JsonResponse, HttpResponse

from apps.station_manager.models import Station, Fixture, TestStandard
from simple_mes import settings

# Create your views here.
CATEGORY_CHOICE = ((0, 'NON'),
                                                (1, 'ASY'),
                                                (2, 'EOL'),
                                                (3, 'CAL'),
                                                (4, 'INS'),
                                                (5, 'OTH'))

class IndexView(ListView):
    """视图类"""
    model = Station
    template_name = "station_manager/station_index.html"
    context_object_name = 'stations'

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['categorys'] = self.model.STATION_CATEGORY_CHOICE
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


def getStationData(request):
    model = Station
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
                                        'num': obj.num, 
                                        'name': obj.name,
                                        'category': obj.category, 
                                        'ip':obj.ip_address,
                                        'remarks': obj.remarks,
                                        'm_time': obj.m_time.strftime("%Y-%m-%d-%H:%M:%S"), 
                                         'c_time': obj.c_time.strftime("%Y-%m-%d-%H:%M:%S"),
                                        })
        return JsonResponse(data)


def deleteStationData(request):
    return_dict = {"ret": True, "errMsg": "", "rows": [], "total": 0}
    id = request.POST.get('id')
    try:
        station = Station.objects.get(id=id)
        station.delete()
        return JsonResponse(return_dict)
    except Exception as e:
        return_dict = {"ret": False, "errMsg": str(e), "rows": [], "total": 0}
        return JsonResponse(return_dict)


def addStationData(request):
    if request.method == "POST":
        name = request.POST.get('nameInput')
        ip = request.POST.get('ipInput')
        category_id = request.POST.get('categorySelect')
        remarks = request.POST.get('remarksText')

        # 数据校验
        if not all([name, category_id]):
            return JsonResponse({"ret": False, "errMsg": '数据不能为空！', "rows": [], "total": 0})
        # 校验IP格式
        if not re.match(r'^192.168.\d{1,3}\.\d{1,3}$', ip):
            return JsonResponse({"ret": False, "errMsg": 'IP格式不正确！', "rows": [], "total": 0})

        try:
            sta = Station.objects.filter_without_isdelete().filter(ip_address=ip)
        except Station.DoesNotExist:
            sta = None
        if sta:
            return JsonResponse({"ret": False, "errMsg": 'IP地址重复！', "rows": [], "total": 0})
        else:
            try:
                cate_str = ''
                for choice in CATEGORY_CHOICE:
                    if int(category_id) == choice[0]:
                        cate_str = choice[1]
                        break
                station_no = genStationNo(cate_str)
                Station.objects.create(num=station_no, name=name,
                                    category=category_id, remarks=remarks, ip_address=ip)
            except Exception as e:
                return_dict = {"ret": False, "errMsg": str(e), "rows": [], "total": 0}
                return JsonResponse(return_dict)

        return_dict = {"ret": True, "errMsg": "", "rows": [], "total": 0}
        return JsonResponse(return_dict)


def updateStationData(request):
    if request.method == 'POST':
        id = request.POST.get('u_idInput')
        name = request.POST.get('u_nameInput')
        station_category = request.POST.get('u_categorySelect')
        remarks = request.POST.get('u_remarksText')
        ip = request.POST.get('u_ipInput')
        
        # 数据校验
        if not all([name, station_category]):
            return JsonResponse({"ret": False, "errMsg": '数据不能为空！', "rows": [], "total": 0})
        # 校验IP格式
        if not re.match(r'^192.168.\d{1,3}\.\d{1,3}$', ip):
            return JsonResponse({"ret": False, "errMsg": 'IP格式不正确！', "rows": [], "total": 0})
        try:
            station = Station.objects.get(id=id)
        except Exception as e:
            return_dict = {"ret": False, "errMsg": str(e), "rows": [], "total": 0}
            return JsonResponse(return_dict)
        if ip == station.ip_address:
            sta = None
        else:
            try:
                sta = Station.objects.filter_without_isdelete().filter(ip_address=ip)
            except Station.DoesNotExist:
                sta = None
        if sta:
            return JsonResponse({"ret": False, "errMsg": 'IP地址重复！', "rows": [], "total": 0})
        else:
            try:
                if station_category != station.category:
                    cate_str = ''
                    for choice in CATEGORY_CHOICE:
                        if int(station_category) == choice[0]:
                            cate_str = choice[1]
                            break
                    station_no = genStationNo(cate_str)
                    station.num = station_no
                station.name = name
                station.remarks = remarks
                station.category = station_category
                station.ip_address = ip
                station.save()
            except Exception as e:
                return_dict = {"ret": False, "errMsg": str(e), "rows": [], "total": 0}
                return JsonResponse(return_dict)
        return_dict = {"ret": True, "errMsg": "", "rows": [], "total": 0}
        return JsonResponse(return_dict)


def genStationNo(cate_str):
    """生成工站号"""
    station = Station.objects.filter(num__contains=cate_str).order_by("-c_time").first()
    if station:
        serial_number = int(station.num[3:]) + 1
    else:
        serial_number = 1
    station_no = cate_str + "{0:03d}".format(serial_number)  # EOL001
    return station_no


def genFixtureNo():
    """生成工站号"""
    fixture = Fixture.objects.all().order_by("-c_time").first()
    if fixture:
        serial_number = int(fixture.num[3:]) + 1
    else:
        serial_number = 1
    fixture_no = 'FIX' + "{0:03d}".format(serial_number)  # FIX001
    return fixture_no


def fixture_index(request):
    fixtures = Fixture.objects.filter_without_isdelete()
    stations = Station.objects.filter_without_isdelete()
    return render(request, 'station_manager/fixture_index.html', locals())


def getFixtureData(request):
    model = Fixture
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
                                        'num': obj.num, 
                                        'name': obj.name,
                                        'station': obj.station.name, 
                                        'remarks': obj.remarks,
                                        'm_time': obj.m_time.strftime("%Y-%m-%d-%H:%M:%S"), 
                                         'c_time': obj.c_time.strftime("%Y-%m-%d-%H:%M:%S"),
                                        })
        return JsonResponse(data)


def addFixtureData(request):
    if request.method == "POST":
        name = request.POST.get('nameInput')
        station_id = request.POST.get('stationSelect')
        remarks = request.POST.get('remarksText')
        print(name, station_id)
        # 数据校验
        if not all([name, station_id]):
            return JsonResponse({"ret": False, "errMsg": '数据不能为空！', "rows": [], "total": 0})
        try:
            station = Station.objects.get(id=station_id)
            fixture_no = genFixtureNo()
            Fixture.objects.create(num=fixture_no, name=name,
                                    station=station, remarks=remarks)
        except Exception as e:
            return JsonResponse({"ret": False, "errMsg": str(e), "rows": [], "total": 0})
        return_dict = {"ret": True, "errMsg": "", "rows": [], "total": 0}
        return JsonResponse(return_dict)


def updateFixtureData(request):
    if request.method == 'POST':
        id = request.POST.get('u_idInput')
        name = request.POST.get('u_nameInput')
        station_id = request.POST.get('u_stationSelect')
        remarks = request.POST.get('u_remarksText')
        
        # 数据校验
        if not all([name, station_id, id]):
            return JsonResponse({"ret": False, "errMsg": '数据不能为空！', "rows": [], "total": 0})
        
        try:
            station = Station.objects.get(id=station_id)
            fixture = Fixture.objects.get(id=id)
            fixture.name = name
            fixture.station = station
            fixture.remarks = remarks
            fixture.save()
        except Exception as e:
            return_dict = {"ret": False, "errMsg": str(e), "rows": [], "total": 0}
            return JsonResponse(return_dict)
        return_dict = {"ret": True, "errMsg": "", "rows": [], "total": 0}
        return JsonResponse(return_dict)


def deleteFixtureData(request):
    return_dict = {"ret": True, "errMsg": "", "rows": [], "total": 0}
    id = request.POST.get('id')
    try:
        fixture = Fixture.objects.get(id=id)
        fixture.delete()
        return JsonResponse(return_dict)
    except Exception as e:
        return_dict = {"ret": False, "errMsg": str(e), "rows": [], "total": 0}
        return JsonResponse(return_dict)


def testStandard(request, fixture_id):
    fixture = Fixture.objects.get(id=fixture_id)
    teststandard = TestStandard.objects.filter_without_isdelete().filter(fixture=fixture).first()
    return render(request, 'station_manager/fixture_teststandard.html', locals())


def getTestStandard(request, fixture_id):
    model = TestStandard
    if request.method == "GET":
        pageSize = int(request.GET.get('pageSize'))
        pageNumber = int(request.GET.get('pageNumber'))
        sortName = request.GET.get('sortName')
        sortOrder = request.GET.get('sortOrder')
        search_kw = request.GET.get('search_kw')
        # if sortOrder == 'asc':
        #     sort_str = sortName
        # else:
        #     sort_str = '-' + sortName
        try:
            fixture = Fixture.objects.get(id=fixture_id)
        except Exception as e:
            return_dict = {"ret": False, "errMsg": str(e), "rows": [], "total": 0}
            return JsonResponse(return_dict)
        if not search_kw:
            total = model.objects.filter_without_isdelete().filter(fixture=fixture).count()
            objs = model.objects.filter_without_isdelete().filter(fixture=fixture)[(pageNumber - 1) * pageSize:(pageNumber) * pageSize]
        else:
            objs = model.objects.filter_without_isdelete().filter(fixture=fixture).filter(Q(name__contains=search_kw)) \
                [(pageNumber - 1) * pageSize: pageNumber * pageSize]
            # 获取查询结果的总条数
            total = model.objects.filter_without_isdelete().filter(fixture=fixture).filter(Q(name__contains=search_kw))\
                [(pageNumber - 1) * pageSize: pageNumber * pageSize].count()
        rows = []
        data = {"total": total, "rows": rows}
        for obj in objs:
            rows.append({'id': obj.id, 
                                        'num': obj.num, 
                                        'name': obj.name,
                                        'upper': obj.upper, 
                                        'lower': obj.lower,
                                        'm_time': obj.m_time.strftime("%Y-%m-%d-%H:%M:%S"), 
                                         'c_time': obj.c_time.strftime("%Y-%m-%d-%H:%M:%S"),
                                        })
        return JsonResponse(data)


def addTestStandard(request, fixture_id):
    if request.method == "POST":
        num = request.POST.get('numInput')
        name = request.POST.get('nameInput')
        upper = float(request.POST.get('upperInput'))
        lower = float(request.POST.get('lowerInput'))
        # 数据校验
        if not all([num, name, upper, lower]):
            return JsonResponse({"ret": False, "errMsg": '数据不能为空！', "rows": [], "total": 0})
        if upper < lower:
            return JsonResponse({"ret": False, "errMsg": "上限大于等于下限！", "rows": [], "total": 0})

        try:
            fixture = Fixture.objects.get(id=fixture_id)
            temp_obj = TestStandard.objects.filter_without_isdelete().first()
            TestStandard.objects.create(num=num, name=name, upper=upper, lower=lower, fixture=fixture, version=temp_obj.version)
        except Exception as e:
            return JsonResponse({"ret": False, "errMsg": str(e), "rows": [], "total": 0})
        return_dict = {"ret": True, "errMsg": "", "rows": [], "total": 0}
        return JsonResponse(return_dict)


def updateTestStandard(request, fixture_id):
    if request.method == 'POST':
        id = request.POST.get('u_idInput')
        num = request.POST.get('u_numInput')
        name = request.POST.get('u_nameInput')
        upper = float(request.POST.get('u_upperInput'))
        lower = float(request.POST.get('u_lowerInput'))
        
        # 数据校验
        if not all([num, name, upper, lower]):
            return JsonResponse({"ret": False, "errMsg": '数据不能为空！', "rows": [], "total": 0})
        if upper<lower:
            return JsonResponse({"ret": False, "errMsg": "上限大于等于下限！", "rows": [], "total": 0})
        
        try:
            test_standard = TestStandard.objects.get(id=id)
            test_standard.num = num
            test_standard.name = name
            test_standard.upper = upper
            test_standard.lower = lower
            test_standard.save()
        except Exception as e:
            return_dict = {"ret": False, "errMsg": str(e), "rows": [], "total": 0}
            return JsonResponse(return_dict)
        return_dict = {"ret": True, "errMsg": "", "rows": [], "total": 0}
        return JsonResponse(return_dict)


def deleteTestStandard(request, fixture_id):
    return_dict = {"ret": True, "errMsg": "", "rows": [], "total": 0}
    id = request.POST.get('id')
    try:
        obj = TestStandard.objects.get(id=id)
        obj.delete()
        return JsonResponse(return_dict)
    except Exception as e:
        return_dict = {"ret": False, "errMsg": str(e), "rows": [], "total": 0}
        return JsonResponse(return_dict)


def writeToDB(**kwargs):
    filename = kwargs.get('filename')
    fixture_id =  kwargs.get('fixture_id')
    version = kwargs.get('version')
    excel = xlrd.open_workbook(settings.UPLOAD_ROOT + "/" + filename)
    sheet = excel.sheet_by_name('测试标准')
    nrows = sheet.nrows
    ncols = sheet.ncols

    try:
        fixture = Fixture.objects.get(id=fixture_id)
    except Exception as e:
        raise e

    obj_list = []
    for i in range(1, nrows):
        row = sheet.row_values(i)
        if not all([row[0], row[1], row[2], row[3]]):
            raise Exception("excel文档的第" + str(i+1) + "存在异常！")
        num = row[0].strip()
        name = row[1].strip()
        if type(row[2]) == str:
            upper = float(row[2].strip())
        else:
            upper = row[2]
        if type(row[3]) == str:
            lower = float(row[3].strip())
        else:
            lower = row[3]
       
        obj_list.append([num, name, upper, lower])
    old_teststandards = TestStandard.objects.filter_without_isdelete().filter(fixture=fixture)
    for old in old_teststandards:
        old.delete()
    
    for obj in obj_list:
        try:
            TestStandard.objects.create(num=obj[0], name=obj[1], upper=obj[2], lower=obj[3], fixture=fixture, version=version)
        except Exception as e:
            raise e
        

def uploadTestStandard(request, fixture_id):
    file = request.FILES.get('uploadFile')
    version = request.POST.get('version')
    try:
        fixture = Fixture.objects.get(id=fixture_id)
    except Exception as e:
        return_dict = {"ret": False, "errMsg": str(e), "rows": [], "total": 0}
        return HttpResponse(json.dumps(return_dict))

    if not version:
        return_dict = {"ret": False, "errMsg": '请填写版本', "rows": [], "total": 0}
        return JsonResponse(return_dict)
    if not re.match(r'^V(\d{1,2})\.(\d{3})$', version):
            return JsonResponse({"ret": False, "errMsg": '版本格式不正确！', "rows": [], "total": 0})
            
    old_teststandard = TestStandard.objects.filter_without_isdelete().filter(fixture=fixture).first()
    if old_teststandard and (float(version[1:]) < float(old_teststandard.version[1:])):
        return JsonResponse({"ret": False, "errMsg": '版本输入有误！', "rows": [], "total": 0})

    if not os.path.exists(settings.UPLOAD_ROOT):
        os.makedirs(settings.UPLOAD_ROOT)
    try:
        if file is None:
            return_dict = {"ret": False, "errMsg": '请选择文件', "rows": [], "total": 0}
            return JsonResponse(return_dict)
        with open(settings.UPLOAD_ROOT + "/" + file.name, 'wb') as f:
            for i in file.readlines():
                f.write(i)
        writeToDB(filename=file.name, fixture_id=fixture_id, version=version)
        return_dict = {"ret": True, "errMsg": "", "rows": [], "total": 0}
        return HttpResponse(json.dumps(return_dict))
    except Exception as e:
        return_dict = {"ret": False, "errMsg": str(e), "rows": [], "total": 0}
        return HttpResponse(json.dumps(return_dict))