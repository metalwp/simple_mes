from django.contrib import admin
from . import models

# Register your models here.

admin.site.register(models.ProcessRoute)
admin.site.register(models.ProcessStep)
