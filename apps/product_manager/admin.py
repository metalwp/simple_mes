from django.contrib import admin
from apps.product_manager.models import ProductCategory, ProductModel
# Register your models here.


admin.site.register(ProductCategory)
admin.site.register(ProductModel)