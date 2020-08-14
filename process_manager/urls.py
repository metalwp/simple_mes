from django.contrib import admin
from django.urls import path, include
from process_manager import views


app_name = 'process_manager'
urlpatterns = [
    path('process_step/index/', views.ps_index, name='ps_index'),
    path('process_step/index/getPSData', views.getPSData, name='getPSData'),
    path('process_step/index/deletePSData', views.deletePSData, name='deletePSData'),
    path('process_step/index/addPSData', views.addPSData, name='addPSData'),

    path('process_route/index/', views.pr_index, name='pr_index'),
    path('process_route/detail/<int:product_id>/', views.pr_detail, name='pr_detail'),
    # path('detail/<int:product_id>/upload/', views.upload, name='upload'),
    # path('detail/getMaterials/<int:product_id>/', views.getMaterials, name='getMaterials'),
    # path('detail/<int:product_id>/delete/', views.delete, name='delete'),
    # path('detail/<int:product_id>/add/', views.add, name='add'),
    # path('detail/<int:product_id>/update/', views.update, name='update'),
]