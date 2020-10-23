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

    path('process_step/detail/<int:step_id>/', views.ps_detail, name='ps_detail'),
    path('process_step/detail/<int:step_id>/getMaterialDate', views.getMaterialDate, name='getMaterialDate'),
    path('process_step/detail/<int:step_id>/addMaterialDate', views.addMaterialDate, name='addMaterialDate'),
    path('process_step/detail/<int:step_id>/deleteMaterialDate', views.deleteMaterialDate, name='deleteMaterialDate'),
    path('process_step/detail/<int:step_id>/refresh_options', views.refresh_options, name='refresh_options'),

    path('process_step/detail/getInspectionData/<int:step_id>/', views.getInspectionData, name='getInspectionData'),
    path('process_step/detail/addInspectionData/<int:step_id>/', views.addInspectionData, name='addInspectionData'),
    path('process_step/detail/updateInspectionData/<int:step_id>/', views.updateInspectionData, name='updateInspectionData'),
    path('process_step/detail/deleteInspectionData/<int:step_id>/', views.deleteInspectionData, name='deleteInspectionData'),
    path('process_step/detail/<int:step_id>/uploadInspection/', views.uploadInspection, name='uploadInspection'),

    path('process_route/index/', views.pr_index, name='pr_index'),
    path('process_route/index/getPRData', views.getPRData, name='getPRData'),
    path('process_route/index/addPRData', views.addPRData, name='addPRData'),
    path('process_route/index/deletePRData', views.deletePRData, name='deletePRData'),
    path('process_route/index/updatePRData', views.updatePRData, name='updatePRData'),

    path('process_route/detail/<int:route_id>/', views.pr_detail, name='pr_detail'),
    path('process_route/detail/<int:route_id>/edit', views.pr_edit, name='pr_edit'),

]