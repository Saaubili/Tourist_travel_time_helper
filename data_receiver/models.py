from django.db import models


# Create your models here.
class City(models.Model):
    name = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()
    population = models.IntegerField()
    city_size = models.CharField(max_length=15, )
    city_type = models.CharField(max_length=25, blank=True)

    class Meta:
        db_table = 'city'


class WeatherData(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE, )
    date = models.DateField()
    min_temperature = models.FloatField()
    max_temperature = models.FloatField()
    precipitation = models.FloatField()
    wind_speed = models.FloatField()

    class Meta:
        unique_together = ("city", "date")
        db_table = 'weather_data'

    def get_avg_temperature(self):
        return (self.min_temperature + self.max_temperature) / 2


class TourismStat(models.Model):
    country = models.CharField(max_length=100)
    date = models.DateField()
    nights_spent = models.IntegerField(null=True)
    occupancy_rate = models.FloatField(null=True)

    class Meta:
        unique_together = ("country", "date")
        db_table = 'tourism_stat'
