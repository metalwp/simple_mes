from django.contrib import admin
from apps.manufacturing.models import Product, ProcessRecord, AssemblyRecord, TestRecord

# Register your models here.
admin.site.register(Product)
admin.site.register(ProcessRecord)
admin.site.register(AssemblyRecord)
admin.site.register(TestRecord)
