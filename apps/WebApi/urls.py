from django.urls import path

from apps.WebApi import views


app_name = 'WebApi'
urlpatterns = [
    path('getMatInsDataXG/', views.getMatInsDataXG, name='getMatInsDataXG'),
    path('getMaterialStandard/', views.getMaterialStandard, name='getMaterialStandard'),
    path('getMaterialResult/', views.getMaterialResult, name='getMaterialResult'),
    path('updateMaterialResult/', views.updateMaterialResult, name='updateMaterialResult'),
    path('getCarBindMat/', views.getCarBindMat, name='getCarBindMat'),
    path('getPreProcessResult/', views.getPreProcessResult, name='getPreProcessResult'),
    path('getFixtureStandard/', views.getFixtureStandard, name='getFixtureStandard'),
    path('updateCarResult/', views.updateCarResult, name='updateCarResult'),

]