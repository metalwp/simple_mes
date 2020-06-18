from django.contrib import admin
from django.urls import path, include

from product_manager import views

app_name = 'product_manager'
urlpatterns = [
    path('pc_index/', views.pc_index, name='pc_index'),
    path('pm_index/', views.pm_index, name='pm_index'),
    path('pc_create/', views.pc_create, name='pc_create')

]