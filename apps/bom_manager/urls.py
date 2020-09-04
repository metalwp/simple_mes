from django.contrib import admin
from django.urls import path, include
from apps.bom_manager import views


app_name = 'bom_manager'
urlpatterns = [
    path('index/', views.index, name='index'),
    path('index/getData/', views.getBomData, name='getBomData'),
    path('index/addData/', views.addBomData, name='addBomData'),
    path('index/deleteData/', views.deleteBomData, name='deleteBomData'),
    path('index/updateData/', views.updateBomData, name='updateBomData'),   

    path('detail/<int:bom_id>/', views.detail, name='detail'),
    path('detail/<int:bom_id>/upload/', views.upload, name='upload'),
    path('detail/<int:bom_id>/get/', views.get, name='get'),
    path('detail/<int:bom_id>/delete/', views.delete, name='delete'),
    path('detail/<int:bom_id>/add/', views.add, name='add'),
    path('detail/<int:bom_id>/update/', views.update, name='update'),
]
