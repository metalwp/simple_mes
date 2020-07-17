from django.contrib import admin
from django.urls import path, include

from order_manager import views

app_name = 'order_manager'
urlpatterns = [
    path('index/', views.index, name='index'),
    path('index/getOrderData/', views.getOrderData, name='getOrderData'),
    path('index/deleteOrderData/', views.deleteOrderData, name='deleteOrderData'),
    path('index/addOrderData/', views.addOrderData, name='addOrderData'),
    path('index/updateOrderData/', views.updateOrderData, name='updateOrderData'),

]
