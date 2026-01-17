import pandas as pd
import requests
from data_receiver.models import WeatherData


def get_weather_data_for_city(city, period=None):
    city_weather = WeatherData.objects.filter(city=city)
    if not city_weather.exists():
        historical_data_url = "https://archive-api.open-meteo.com/v1/archive"
        params = {
            "latitude": city.latitude,
            "longitude": city.longitude,
            "start_date": "2023-01-01",
            "end_date": "2025-12-31",
            "daily": ["temperature_2m_max",
                      "temperature_2m_mean",
                      "precipitation_sum",
                      "relative_humidity_2m_mean",
                      "relative_humidity_2m_min",
                      "wind_speed_10m_mean",
                      "daylight_duration"],
            "timezone": "auto",
        }

        city_weather_data = requests.get(historical_data_url, params=params).json()

        if "daily" not in city_weather_data:
            if "API request limit exceeded" in city_weather_data['reason']:
                return (False,
                        f"API request limit exceeded, please try again later, time: {city_weather_data["reason"].split(" ")[-1]}")
            return (False, f"daily not found in {city.name}")

        daily_data = city_weather_data["daily"]
        fill_weather_model_data(daily_data, city)
        return (True, WeatherData.objects.filter(city=city))
    return (True, city_weather)


def fill_weather_model_data(daily_data, city):
    weather_df = pd.DataFrame({
        "date": pd.to_datetime(daily_data["time"]),
        "mean_temperature": daily_data["temperature_2m_mean"],
        "max_temperature": daily_data["temperature_2m_max"],
        "precipitation": daily_data["precipitation_sum"],
        "wind_speed": daily_data["wind_speed_10m_mean"],
        "min_relative_humidity": daily_data["relative_humidity_2m_min"],
        "mean_relative_humidity": daily_data["relative_humidity_2m_mean"],
        "daylight_duration": daily_data["daylight_duration"]
    })

    weather_df["year"] = weather_df["date"].dt.year
    weather_df["day_index"] = weather_df.groupby("year").cumcount()
    weather_df["period"] = weather_df["day_index"] // 7 + 1

    weekly_by_year = weather_df.groupby(["year", "period"]).agg(
        mean_temperature=("mean_temperature", "mean"),
        max_temperature=("max_temperature", "mean"),
        precipitation=("precipitation", "sum"),
        wind_speed=("wind_speed", "mean"),
        min_relative_humidity=("min_relative_humidity", "mean"),
        mean_relative_humidity=("mean_relative_humidity", "mean"),
        daylight_duration=("daylight_duration", "mean"),
    )

    weekly_avg = weekly_by_year.groupby("period").agg(
        mean_temperature=("mean_temperature", "mean"),
        max_temperature=("max_temperature", "mean"),
        precipitation=("precipitation", "mean"),
        wind_speed=("wind_speed", "mean"),
        min_relative_humidity=("min_relative_humidity", "mean"),
        mean_relative_humidity=("mean_relative_humidity", "mean"),
        daylight_duration=("daylight_duration", "mean"),
    ).reset_index()

    for _, row in weekly_avg.iterrows():
        WeatherData.objects.update_or_create(
            city=city,
            period=int(row["period"]),
            defaults={
                "mean_temperature": row["mean_temperature"],
                "max_temperature": row["max_temperature"],
                "precipitation": row["precipitation"],
                "wind_speed": row["wind_speed"],
                "min_relative_humidity": int(round(row["min_relative_humidity"])),
                "mean_relative_humidity": int(round(row["mean_relative_humidity"])),
                "daylight_duration": row["daylight_duration"]
            }
        )
