from django.urls import path

from apps.manufacturing import views


app_name = 'manufacturing'
urlpatterns = [
    path('assemble/<int:sequence_no>/', views.index, name='index'),

    path('assemble/getOrderInfo/<int:sequence_no>/', views.getOrderInfo, name='getOrderInfo'),
    path('assemble/getProductInfo/<int:sequence_no>/', views.getProductInfo, name='getProductInfo'),
    path('assemble/generateVIN/<int:sequence_no>/', views.generateVIN, name='generateVIN'),

    path('assemble/getAssembleRecord/<int:sequence_no>/', views.getAssembleRecord, name='getAssembleRecord'),

]