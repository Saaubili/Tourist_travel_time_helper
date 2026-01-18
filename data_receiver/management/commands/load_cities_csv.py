import time

from django.core.management.base import BaseCommand
from data_receiver.models import City
import csv
import requests
import re
from django.conf import settings


class Command(BaseCommand):
    help = "fill_City_model_with_data"

    def add_arguments(self, parser):
        parser.add_argument("csv_file", type=str)

    def handle(self, *args, **options):
        with open(options['csv_file'], encoding='utf-8') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                lag = float(row['lat'])
                lng = float(row['lng'])
                if City.objects.filter(latitude=lag, longitude=lng).exists():
                    self.stdout.write(f"City {row['city']} already exists")
                    continue
                if int(row["population"]) > 30000 and row["country"] not in ["US", "China"]:
                    population = int(row["population"])

                    rus_name = self.get_russian_name(lag, lng)
                    if rus_name == "Не смог найти русское название":
                        rus_name = ""

                    city_size = self.determine_city_size(population)

                    City.objects.update_or_create(name=row['city'],
                                                  country=row['country'],
                                                  defaults={
                                                      "latitude": lag,
                                                      "longitude": lng,
                                                      "population": population,
                                                      "city_size": city_size,
                                                      "name_ru": rus_name,
                                                  })
                    if rus_name != "":
                        self.stdout.write(f"Successfully loaded city {rus_name}")
                    else:
                        self.stdout.write(f"Failed to load city {row['city']}")
        self.stdout.write("Successfully loaded cities data")

    @staticmethod
    def get_russian_name(lat, lng):
        if not settings.GEONAMES_USERNAME:
            raise RuntimeError("GEONAMES_USERNAME not set")
        contains_russian = lambda text: bool(re.search(r'[а-яА-ЯёЁ]', text))
        historical_data_url = "http://api.geonames.org/findNearbyPlaceNameJSON"
        params = {
            "lat": lat,
            "lng": lng,
            "username": settings.GEONAMES_USERNAME,
            "cities": "cities15000",
            "radius": 300,
            "featureClass": "P",
            "lang": "ru",
        }
        response = requests.get(historical_data_url, params=params).json()
        time.sleep(0.5)
        if response:
            candidates = []
            for place in response['geonames']:
                name = place['name']
                if contains_russian(name):
                    candidates.append({"name": name, "population": int(place['population'])})
            candidates.sort(key=lambda x: x["population"], reverse=True)
            if candidates:
                best = candidates[0]
                if contains_russian(best["name"]):
                    return best["name"]
        return "Не смог найти русское название"


    @staticmethod
    def determine_city_size(population):
        if population >= 5000000:
            city_size = "very big"
        elif population >= 1000000:
            city_size = "big"
        elif population >= 500000:
            city_size = "large"
        elif population >= 100000:
            city_size = "average"
        else:
            city_size = "small"
        return city_size
