from django.contrib import admin
from .models import City, TourismStat, WeatherData
import _sqlite3

# Register your models here.
class CityAdmin(admin.ModelAdmin):
    list_display = ("name", "name_ru", "country", "city_size", "population")
    search_fields = ("name", "country", "name_ru",)


class WeatherDataAdmin(admin.ModelAdmin):
    list_display = ("city", "year", "period", "min_temperature", "max_temperature")
    search_fields = ("city", "year", "period")


class TourismStatAdmin(admin.ModelAdmin):
    list_display = ("country", "date", "nights_spent", "occupancy_rate")
    search_fields = ("country",)


admin.site.register(City,CityAdmin)
admin.site.register(TourismStat, TourismStatAdmin)
admin.site.register(WeatherData, WeatherDataAdmin)
