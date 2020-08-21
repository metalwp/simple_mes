from django.contrib import admin
from . import models
# Register your models here.

admin.site.register(models.Customer)
admin.site.register(models.Order)
admin.site.register(models.Product)
admin.site.register(models.ProductRecord)
admin.site.register(models.Material)
admin.site.register(models.TestRecord)
admin.site.register(models.IqcRecord)
