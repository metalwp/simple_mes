from django.urls import path

from apps.manufacturing import views


app_name = 'manufacturing'
urlpatterns = [
    path('assemble/<int:step_id>/', views.index, name='index'),

    path('assemble/getOrderInfo/<int:step_id>/', views.getOrderInfo, name='getOrderInfo'),
    path('assemble/getProductInfo/<int:step_id>/', views.getProductInfo, name='getProductInfo'),
    path('assemble/generateVIN/<int:step_id>/', views.generateVIN, name='generateVIN'),
    path('assemble/getInspectionData/<int:step_id>/', views.getInspectionData, name='getInspectionData'),
    path('assemble/saveInspectionData/<int:step_id>/', views.saveInspectionData, name='saveInspectionData'),
    path('assemble/unbundle/<int:step_id>/', views.unbundle, name='unbundle'),

    path('assemble/getAssembleRecord/<int:step_id>/', views.getAssembleRecord, name='getAssembleRecord'),

    path('repair/', views.repair_index, name='repair_index'),
    path('repair/getRepairInfo/', views.getRepairInfo, name='getRepairInfo'),
    path('repair/get/', views.getRepairRecord, name='getRepairRecord'),
    path('repair/add/', views.addRepairRecord, name='addRepairRecord'),
    #path('repair/delete/', views.deleteRepairRecord, name='deleteRepairRecord'),  # 不增加删除返修记录功能，会造成数据的丢失和混乱

]
