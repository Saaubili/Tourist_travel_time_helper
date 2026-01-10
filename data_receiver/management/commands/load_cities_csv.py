from django.core.management.base import BaseCommand
from data_receiver.models import City
import csv
import requests


class Command(BaseCommand):
    help = "fill_City_model_with_data"

    def add_arguments(self, parser):
        parser.add_argument("csv_file", type=str)

    def handle(self, *args, **options):
        viable_countries_iso3 = [
            "ALB", "AND", "AUT", "BLR", "BEL", "BIH", "BGR", "HRV", "CYP",
            "CZE", "DNK", "EST", "FIN", "FRA", "DEU", "GRC", "HUN", "ISL",
            "IRL", "ITA", "LVA", "LIE", "LTU", "LUX", "MLT", "MDA", "MCO",
            "MNE", "NLD", "MKD", "NOR", "POL", "PRT", "ROU", "RUS", "SMR",
            "SRB", "SVK", "SVN", "ESP", "SWE", "CHE", "UKR", "GBR", "VAT",]
        with open(options['csv_file'], encoding='utf-8') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                if row["iso3"] in viable_countries_iso3:
                    city_name = row['city']
                    population = int(row["population"])
                    csv_city_type = row['capital']
                    is_capital = csv_city_type.strip() == "primary"

                    tourism_info = self.check_if_city_tourist(city_name)

                    city_size = self.determine_city_size(population)

                    city_type = self.determine_city_type(is_capital, tourism_info)

                    City.objects.update_or_create(name=row['city'],
                                                  country=row['country'],
                                                  defaults={
                                                      "latitude": float(row["lat"]),
                                                      "longitude": float(row["lng"]),
                                                      "population": population,
                                                      "city_size": city_size,
                                                      "city_type": city_type
                                                  })
        self.stdout.write(self.style.SUCCESS("Successfully loaded cities data"))

    def check_if_city_tourist(self, city_name):
        params = {"q": city_name, "language": "en", "limit": 1}

        headers = {
            "User-Agent": "Test-script",
        }
        tourism_dict = {
            "Q1200957": "Generally popular location",
            "Q130003": "Ski resort",
            "Q317548": "Resort town",
            "Q1021711": "Seaside resort"
        }
        try:
            item_search_url = "https://www.wikidata.org/w/rest.php/wikibase/v0/search/items"
            item_search_result = requests.get(item_search_url, params=params, headers=headers)
            if not item_search_result.json()["results"]:
                self.stdout.write(self.style.WARNING(f"No Wikidata entry found for city '{city_name}'"))
                return []
            id = item_search_result.json()["results"][0]["id"]

            statements_search_url = f"https://www.wikidata.org/w/rest.php/wikibase/v1/entities/items/{id}/statements"
            statements_search_result = requests.get(statements_search_url, headers=headers)
            statements_by_parameter = statements_search_result.json().get("P31", [])
            if statements_by_parameter:
                statements_list = []

                for statement in statements_by_parameter:
                    statement_id = statement["value"]["content"]
                    if statement_id in tourism_dict:
                        statements_list.append(tourism_dict.get(statement["value"]["content"]))
                return statements_list
            else:
                self.stdout.write(self.style.WARNING(f"No 'Instance of' data for city '{city_name}'"))
                return []
        except requests.exceptions.RequestException:
            self.stdout.write(self.style.ERROR("Failed to connect to Wikidata API"))
            return []

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

    @staticmethod
    def determine_city_type(is_capital, tourism_info):
        if is_capital:
            return "capital"
        if tourism_info:
            if "Generally popular location" in tourism_info:
                city_type = "tourist attraction"
            else:
                city_type = tourism_info[0]
            return city_type
        return ""