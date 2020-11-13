from django.contrib import admin
from django.urls import path, include
from apps.account.views import LoginView, LogoutView, RegisterView, UserView, PermissionView, RoleView, MenuView


app_name = 'account'
urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),

    path('user/', UserView.as_view(), name='user'),
    path('user/get/', UserView.as_view(), name='getUser'),
    path('user/add/', UserView.as_view(), name='addUser'),

    path('permission/', PermissionView.as_view(), name='permission'),
    path('role/', RoleView.as_view(), name='role'),
    path('menu/', MenuView.as_view(), name='menu'),
]