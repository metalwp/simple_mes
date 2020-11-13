from django.contrib import admin
from apps.account.models import User, Menu, Permission, Role

# Register your models here.

admin.site.register(User)
admin.site.register(Menu)
admin.site.register(Permission)
admin.site.register(Role)

