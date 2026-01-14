import pandas as pd
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
import requests
from data_receiver.models import City, WeatherData, TourismStat
import numpy as np
from .form import CitySelectForm


def main_page(request):
    city_id = request.session.get('selected_city_id')
    selected_city_id = None
    chosen_analytics_type = None
    if city_id:
        selected_city_id = get_object_or_404(City, id=city_id)
    context = {
        "selected_city": selected_city_id,
        "analytics_type": chosen_analytics_type,
    }
    return render(request, "recommendation_system/select_page.html", context)


def save_city_selection(request):
    city_id = request.POST.get("city_id")
    request.session['selected_city_id'] = city_id


def save_analytics_type(request):
    analytics_type = request.POST.get("analytics_type")
    request.session['analytics_type'] = analytics_type


def check_if_ready_to_analyze(request):
    city_selected = request.session.get('city_selected_id')
    analytics_selected = request.session.get('analytics_selected')

    if not city_selected or not analytics_selected:
        return
    else:
        if analytics_selected == "best_periods":
            prepare_best_periods(request, city_selected)


def prepare_best_periods(request, city_selected):
    city = City.objects.get(id=city_selected)
    succeeded, result = get_weather_data_for_city(request, city)
    if not succeeded:
        return result



def get_weather_data_for_city(request, city, period=None):
    city_weather = WeatherData.objects.filter(city=city)
    if not city_weather.exists():
        historical_data_url = "https://archive-api.open-meteo.com/v1/archive"
        params = {
            "latitude": city.latitude,
            "longitude": city.longitude,
            "start_date": "2023-01-01",
            "end_date": "2025-12-31",
            "daily": ["temperature_2m_max", "temperature_2m_min", "precipitation_sum", "wind_speed_10m_mean"],
            "timezone": "auto",
        }

        city_weather_data = requests.get(historical_data_url, params=params).json()

        if "daily" not in city_weather_data:
            if "API request limit exceeded" in city_weather_data['reason']:
                return  (False, f"API request limit exceeded, please try again later, time: {city_weather_data["reason"].split(" ")[-1]}")
            return (False, f"daily not found in {city.name}")

        daily_data = city_weather_data["daily"]
        fill_weather_model_data(daily_data, city)
        return (True, WeatherData.objects.filter(city=city))
    return (True, city_weather)


def fill_weather_model_data(daily_data, city):
    weather_df = pd.DataFrame({
        "date": pd.to_datetime(daily_data["time"]),
        "min_temp": daily_data["temperature_2m_min"],
        "max_temp": daily_data["temperature_2m_max"],
        "precipitation": daily_data["precipitation_sum"],
        "wind_speed": daily_data["wind_speed_10m_mean"]
    })
    weather_df["year"] = weather_df["date"].dt.year

    weather_df["day_index"] = weather_df.groupby("year").cumcount()

    weather_df["period"] = weather_df["day_index"] // 7 + 1

    grouped = weather_df.groupby(["year", "period"]).agg(
        min_temperature=("min_temp", "mean"),
        max_temperature=("max_temp", "mean"),
        precipitation=("precipitation", "sum"),
        wind_speed=("wind_speed", "mean"),
    ).reset_index()

    for _, row in grouped.iterrows():
        WeatherData.objects.update_or_create(
            city=city.name,
            year=int(row["year"]),
            period=int(row["period"]),
            defaults={
                "min_temperature": row["min_temperature"],
                "max_temperature": row["max_temperature"],
                "precipitation": row["precipitation"],
                "wind_speed": row["wind_speed"],
            }
        )


def city_selected(request):
    city_id = request.GET.get("city_id")
    city = get_object_or_404(City, id=city_id)
    return JsonResponse({
        "name": city.name_ru,
        "population": city.population,
        "lat": city.latitude,
        "lon": city.longitude,
    })


def city_search(request):
    city_name = request.GET.get("city_name", "")

    cities = (
        City.objects
        .filter(name_ru__icontains=city_name)
        .order_by("-population")[:10]
    )

    data = [
        {
            "id": city.id,
            "name": city.name_ru,
            "lat": city.latitude,
            "lon": city.longitude,
        }
        for city in cities
    ]

    return JsonResponse(data, safe=False)
