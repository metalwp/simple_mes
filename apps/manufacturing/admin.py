from django.contrib import admin
from apps.manufacturing.models import Product, ProcessRecord, AssemblyRecord, TestRecord, HistoryRecord

# Register your models here.
admin.site.register(Product)
admin.site.register(ProcessRecord)
admin.site.register(AssemblyRecord)
admin.site.register(TestRecord)
admin.site.register(HistoryRecord)
