from django.contrib import admin
from apps.station_manager.models import Station, Fixture, TestStandard

# Register your models here.


admin.site.register(Station)
admin.site.register(Fixture)
admin.site.register(TestStandard)