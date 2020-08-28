from django.contrib import admin
from apps.process_manager.models import ProcessRoute, ProcessStep
# Register your models here.

admin.site.register(ProcessRoute)
admin.site.register(ProcessStep)
