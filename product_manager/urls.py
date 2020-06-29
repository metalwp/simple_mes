from django.contrib import admin
from django.urls import path, include

from product_manager import views

app_name = 'product_manager'
urlpatterns = [
    path('pc_index/', views.pc_index, name='pc_index'),
    path('pc_index/getPcData/', views.getPcData, name='getPcData'),
    path('pc_index/addPcData/', views.addPcData, name='addPcData'),
    path('pc_index/updatePcData/', views.updatePcData, name='updatePcData'),
    path('pc_index/deleteData/', views.deleteData, name='deleteData'),
    path('pm_index/', views.pm_index, name='pm_index'),

]