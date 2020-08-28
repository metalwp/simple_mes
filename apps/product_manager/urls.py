from django.contrib import admin
from django.urls import path, include

from apps.product_manager import views

app_name = 'product_manager'
urlpatterns = [
    path('pc_index/', views.pc_index, name='pc_index'),
    path('pc_index/getPcData/', views.getPcData, name='getPcData'),
    path('pc_index/addPcData/', views.addPcData, name='addPcData'),
    path('pc_index/updatePcData/', views.updatePcData, name='updatePcData'),
    path('pc_index/deletePcData/', views.deletePcData, name='deletePcData'),
    path('pm_index/', views.pm_index, name='pm_index'),
    path('pm_index/getPmData/', views.getPmData, name='getPmData'),
    path('pm_index/addPmData/', views.addPmData, name='addPmData'),
    path('pm_index/updatePmData/', views.updatePmData, name='updatePmData'),
    path('pm_index/deletePmData/', views.deletePmData, name='deletePmData'),
]
