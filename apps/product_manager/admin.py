from django.contrib import admin
from apps.product_manager.models import ProductCategory, ProductModel, VinRule, VinRuleItem
# Register your models here.

@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    pass

# admin.site.register(ProductCategory)
admin.site.register(ProductModel)
admin.site.register(VinRule)
admin.site.register(VinRuleItem)

