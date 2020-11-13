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

    path('assemble/getAssembleRecord/<int:step_id>/', views.getAssembleRecord, name='getAssembleRecord'),

]
