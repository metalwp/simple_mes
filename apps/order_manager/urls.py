from django.contrib import admin
from django.urls import path, include

from apps.order_manager import views

app_name = 'order_manager'
urlpatterns = [
    path('cm_index/', views.cm_index, name='cm_index'),
    path('cm_index/getData/', views.getCustomerData, name='getCustomerData'),
    path('cm_index/addData/', views.addCustomerData, name='addCustomerData'),
    path('cm_index/deleteData/', views.deleteCustomerData, name='deleteCustomerData'),
    path('cm_index/updateData/', views.updateCustomerData, name='updateCustomerData'),

    path('om_index/', views.om_index, name='om_index'),
    path('om_index/getData/', views.getOrderData, name='getOrderData'),
    path('om_index/deleteData/', views.deleteOrderData, name='deleteOrderData'),
    path('om_index/addData/', views.addOrderData, name='addOrderData'),
    path('om_index/getOrderNo/', views.GetOrderNum.as_view(), name='getOrderNo'),

    path('om_index/updateData/', views.updateOrderData, name='updateOrderData'),

]
