from django.core.management.base import BaseCommand
from data_receiver.models import City, WeatherData
import pandas as pd
import datetime
import requests
import datetime
import time


class Command(BaseCommand):
    help = "fill weather data"

    def handle(self, *args, **options):
        path = "https://archive-api.open-meteo.com/v1/archive"
        for city in City.objects.filter(population__gte = 100000):
            if WeatherData.objects.filter(city=city).exists():
                self.stdout.write(f"{city.name} already exists")
                continue
            params = {
                "latitude": city.latitude,
                "longitude": city.longitude,
                "start_date": "2023-01-01",
                "end_date": "2025-12-31",
                "daily": ["temperature_2m_max", "temperature_2m_min", "precipitation_sum", "wind_speed_10m_mean"],
                "timezone": "auto",
            }
            time.sleep(2)
            response = requests.get(path, params=params).json()
            if "daily" not in response:
                self.stdout.write(f"No daily data for {city.name}")
                if "API request limit exceeded" in response['reason']:
                    self.stdout.write(f"API request limit exceeded, please try again later, time: {response["reason"].split(" ")[-1]}")
                    break
                else:
                    continue
            daily = response["daily"]
            df = pd.DataFrame({
                "date": pd.to_datetime(daily["time"]),
                "min_temp": daily["temperature_2m_min"],
                "max_temp": daily["temperature_2m_max"],
                "precipitation": daily["precipitation_sum"],
                "wind_speed": daily["wind_speed_10m_mean"]
            })

            df["year"] = df["date"].dt.year

            df["day_index"] = df.groupby("year").cumcount()

            df["period"] = df["day_index"] // 14 + 1

            grouped = df.groupby(["year", "period"]).agg(
                min_temperature=("min_temp", "mean"),
                max_temperature=("max_temp", "mean"),
                precipitation=("precipitation", "sum"),
                wind_speed=("wind_speed", "mean"),
            ).reset_index()

            grouped["year"] = grouped["year"].astype(int)
            grouped["period"] = grouped["period"].astype(int)

            for _, row in grouped.iterrows():
                WeatherData.objects.update_or_create(
                    city=city,
                    year=int(row["year"]),
                    period=int(row["period"]),
                    defaults={
                        "min_temperature": row["min_temperature"],
                        "max_temperature": row["max_temperature"],
                        "precipitation": row["precipitation"],
                        "wind_speed": row["wind_speed"],
                    }
                )

            self.stdout.write(self.style.SUCCESS(f"finished {city.name}"))

        self.stdout.write(self.style.SUCCESS("Successfully loaded weather data"))
