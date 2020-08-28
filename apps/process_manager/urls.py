from django.contrib import admin
from django.urls import path, include
from apps.process_manager import views


app_name = 'process_manager'
urlpatterns = [
    path('process_step/index/', views.ps_index, name='ps_index'),
    path('process_step/index/getPSData', views.getPSData, name='getPSData'),
    path('process_step/index/deletePSData', views.deletePSData, name='deletePSData'),
    path('process_step/index/addPSData', views.addPSData, name='addPSData'),
    path('process_step/index/updatePSData', views.updatePSData, name='updatePSData'),
    path('process_route/index/', views.pr_index, name='pr_index'),
    path('process_route/detail/<int:product_id>/', views.pr_detail, name='pr_detail'),
    path('process_route/detail/<int:product_id>/edit', views.pr_edit, name='pr_edit'),

]