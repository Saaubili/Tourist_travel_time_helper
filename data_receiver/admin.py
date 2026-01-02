from django.contrib import admin
from .models import City, WeatherData, TourismStat
import _sqlite3

# Register your models here.
class CityAdmin(admin.ModelAdmin):
    list_display = ("name", "country", "city_type", "population")
    search_fields = ("name", "country")


class WeatherDataAdmin(admin.ModelAdmin):
    list_display = ("city", "date", "min_temperature", "max_temperature")
    search_fields = ("city__name", "city__country")
    list_filter = ("city",)


class TourismStatAdmin(admin.ModelAdmin):
    list_display = ("country", "date", "nights_spent", "occupancy_rate")
    search_fields = ("country",)


admin.site.register(City,CityAdmin)
admin.site.register(TourismStat, TourismStatAdmin)
admin.site.register(WeatherData, WeatherDataAdmin)
