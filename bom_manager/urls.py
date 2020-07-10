from django.contrib import admin
from django.urls import path, include
from bom_manager import views


app_name = 'bom_manager'
urlpatterns = [
    path('index/', views.index, name='index'),
    path('detail/<int:product_id>/', views.detail, name='detail'),
    path('detail/<int:product_id>/upload/', views.upload, name='upload'),
    path('detail/getMaterials/<int:product_id>/', views.getMaterials, name='getMaterials'),
    path('detail/<int:product_id>/delete/', views.delete, name='delete'),

]