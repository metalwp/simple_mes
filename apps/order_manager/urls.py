from django.contrib import admin
from django.urls import path, include

from apps.order_manager import views

app_name = 'order_manager'
urlpatterns = [
    path('cm_index/', views.cm_index, name='cm_index'),

    path('om_index/', views.om_index, name='om_index'),
    path('om_index/getOrderData/', views.getOrderData, name='getOrderData'),
    path('om_index/deleteOrderData/', views.deleteOrderData, name='deleteOrderData'),
    path('om_index/addOrderData/', views.addOrderData, name='addOrderData'),
    # path('index/getOrderNo/', views.getOrderNo, name='getOrderNo'),
    path('om_index/getOrderNo/', views.GetOrderNum.as_view(), name='getOrderNo'),

    path('om_index/updateOrderData/', views.updateOrderData, name='updateOrderData'),

]
