from django.contrib import admin
from django.urls import path, include

from apps.station_manager import views

app_name = 'station_manager'
urlpatterns = [
    path('station_index/', views.station_index, name='station_index'),
    path('station_index/getData/', views.getStationData, name='getStationData'),
    path('station_index/addData/', views.addStationData, name='addStationData'),
    path('station_index/updateData/', views.updateStationData, name='updateStationData'),
    path('station_index/deleteData/', views.deleteStationData, name='deleteStationData'),

    path('fixture_index/', views.fixture_index, name='fixture_index'),
    path('fixture_index/getData/', views.getFixtureData, name='getFixtureData'),
    path('fixture_index/addData/', views.addFixtureData, name='addFixtureData'),
    path('fixture_index/updateData/', views.updateFixtureData, name='updateFixtureData'),
    path('fixture_index/deleteData/', views.deleteFixtureData, name='deleteFixtureData'),

    path('fixture_teststandard/<int:fixture_id>', views.testStandard, name='teststandard'),
    path('fixture_teststandard/uploadData/<int:fixture_id>/', views.uploadTestStandard, name='uploadTestStandard'),
    path('fixture_teststandard/getData/<int:fixture_id>/', views.getTestStandard, name='getTestStandard'),
    path('fixture_teststandard/deleteData/<int:fixture_id>/', views.deleteTestStandard, name='deleteTestStandard'),
    path('fixture_teststandard/addData/<int:fixture_id>/', views.addTestStandard, name='addTestStandard'),
    path('fixture_teststandard/updateData/<int:fixture_id>/', views.updateTestStandard, name='updateTestStandard'),

]
