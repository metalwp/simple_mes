from django.contrib import admin
from apps.Inspection.models import GeneralMaterial, GMInspectRecord, TraceMaterial, TMInspectRecord, Inspection
# Register your models here.

admin.site.register(Inspection)
admin.site.register(GeneralMaterial)
admin.site.register(GMInspectRecord)
admin.site.register(TraceMaterial)
admin.site.register(TMInspectRecord)
