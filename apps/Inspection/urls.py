from django.contrib import admin
from django.urls import path, include
from apps.Inspection import views


app_name = 'Inspection'
urlpatterns = [
    path('material/index/', views.material_index, name='material_index'),
    path('material/getMaterialData/', views.getMaterialData, name='getMaterialData'),

    path('material/detail/<int:material_id>/', views.material_detail, name='material_detail'),
    path('material/detail/getData/<int:material_id>/', views.getInspectionData, name='getInspectionData'),
    path('material/detail/addData/<int:material_id>/', views.addInspectionData, name='addInspectionData'),
    path('material/detail/updateData/<int:material_id>/', views.updateInspectionData, name='updateInspectionData'),
    path('material/detail/deleteData/<int:material_id>/', views.deleteInspectionData, name='deleteInspectionData'),
    path('material/detail/<int:material_id>/uploadData/', views.uploadInspection, name='uploadInspection'),

    path('gminspection/index/', views.gminspection_index, name='gminspection_index'),
    path('gminspection/getMaterialInfo/', views.getMaterialInfo, name='getMaterialInfo'),
    path('gminspection/getGMInspectionData/', views.getGMInspectionData, name='getGMInspectionData'),

    path('tminspection/index/', views.tminspection_index, name='tminspection_index'),

]
