from django.contrib import admin
from apps.bom_manager.models import BOM, MaterialModel, Inspection

# Register your models here.


admin.site.register(BOM)
admin.site.register(MaterialModel)
admin.site.register(Inspection)
