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
    path('detail/upload/<int:bom_id>/', views.upload, name='upload'),
    path('detail/get/<int:bom_id>/', views.get, name='get'),
    path('detail/delete/<int:bom_id>/', views.delete, name='delete'),
    path('detail/add/<int:bom_id>/', views.add, name='add'),
    path('detail/update/<int:bom_id>/', views.update, name='update'),
]
