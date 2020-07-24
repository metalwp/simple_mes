from django.contrib import admin
from django.urls import path, include

from station_manager import views

app_name = 'station_manager'
urlpatterns = [
    path('index/', views.IndexView.as_view(), name='index'),
    path('getdata/', views.IndexView.as_view(), name='getdata'),
    # path('pc_index/getPcData/', views.getPcData, name='getPcData'),
    # path('pc_index/addPcData/', views.addPcData, name='addPcData'),
    # path('pc_index/updatePcData/', views.updatePcData, name='updatePcData'),
    # path('pc_index/deletePcData/', views.deletePcData, name='deletePcData'),
]
