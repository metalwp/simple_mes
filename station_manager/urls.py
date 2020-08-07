from django.contrib import admin
from django.urls import path, include

from station_manager import views

app_name = 'station_manager'
urlpatterns = [
    path('index/', views.IndexView.as_view(), name='index'),
    path('getData/', views.getData, name='getData'),
    path('addData/', views.addData, name='addData'),
    path('updateData/', views.updateData, name='updateData'),
    path('deleteData/', views.deleteData, name='deleteData'),
]
