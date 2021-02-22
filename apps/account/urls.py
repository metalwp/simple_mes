from django.contrib import admin
from django.urls import path, include
from apps.account.views import LoginView, LogoutView, RegisterView, UserView, PermissionView, RoleView, MenuView, RolePermissionView


app_name = 'account'
urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),

    path('user/', UserView.as_view(), name='user'),
    path('user/get/', UserView.as_view(), name='getUser'),
    path('user/add/', UserView.as_view(), name='addUser'),
    path('user/delete/', UserView.as_view(), name='deleteUser'),
    path('user/update/', UserView.as_view(), name='updateUser'),
    path('user/reset/', UserView.as_view(), name='resetPassword'),
    path('user/profile/', UserView.as_view(), name='editProfile'),
    path('user/password/', UserView.as_view(), name='editPassword'),

    path('permission/', PermissionView.as_view(), name='permission'),
    path('permission/get/', PermissionView.as_view(), name='getPermission'),
    path('permission/add/', PermissionView.as_view(), name='addPermission'),
    path('permission/update/', PermissionView.as_view(), name='updatePermission'),
    path('permission/delete/', PermissionView.as_view(), name='deletePermission'),
    path('permission/export/', PermissionView.as_view(), name='exportPermission'),
    path('permission/upload/', PermissionView.as_view(), name='uploadPermission'),

    path('role/', RoleView.as_view(), name='role'),
    path('role/get/', RoleView.as_view(), name='getRole'),
    path('role/add/', RoleView.as_view(), name='addRole'),
    path('role/update/', RoleView.as_view(), name='updateRole'),
    path('role/delete/', RoleView.as_view(), name='deleteRole'),

    path('menu/', MenuView.as_view(), name='menu'),
    path('menu/get/', MenuView.as_view(), name='getMenu'),
    path('menu/add/', MenuView.as_view(), name='addMenu'),
    path('menu/update/', MenuView.as_view(), name='updateMenu'),
    path('menu/delete/', MenuView.as_view(), name='deleteMenu'),
    path('menu/export/', MenuView.as_view(), name='exportMenu'),
    path('menu/upload/', MenuView.as_view(), name='uploadMenu'),

    path('role_permission/', RolePermissionView.as_view(), name='role_permission'),
    path('role_permission/getRole/', RolePermissionView.as_view(), name='getRole2'),
    path('role_permission/getPermission/', RolePermissionView.as_view(), name='getPermission2'),
    path('role_permission/getChecked/', RolePermissionView.as_view(), name='getChecked'),
    path('role_permission/updatePermission/', RolePermissionView.as_view(), name='updatePermission2'),

]