import pandas as pd
from django.db.models.expressions import result
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
import requests
import datetime
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
    return JsonResponse({"status": "ok"})


def save_analytics_type(request):
    analytics_type = request.POST.get("analytics_type")
    request.session['analytics_type'] = analytics_type
    return JsonResponse({"status": "ok"})


def check_if_ready_to_analyze(request):
    city_selected = request.session.get('selected_city_id')
    analytics_selected = request.session.get('analytics_type')

    if not city_selected or not analytics_selected:
        return JsonResponse({"best_weeks": [], "graph_data": []})
    else:
        if analytics_selected == "best_periods":
            result = prepare_best_periods(request, city_selected)
            if "error" in result:
                return JsonResponse({"status": "error", "message": result["error"]})
            df = result["df"]
            best_weeks = result["best_weeks"]

            return JsonResponse({
                "status": "ok",
                "best_weeks": best_weeks.to_dict(orient="records"),
                "graph_data": df.to_dict(orient="records")
            })


def prepare_best_periods(request, city_selected):
    city = City.objects.get(id=city_selected)
    tourism_stat = TourismStat.objects.filter(country=city.country)
    climate_type = get_climate_type_by_lat(city.latitude)
    succeeded, weather_result = get_weather_data_for_city(city)
    if not succeeded:
        return {"error": weather_result}
    weather_result = weather_result.order_by("period")
    weekly_scores = []

    last_month = 0
    tourism_coef = 0
    for week in weather_result:
        TCI = calculate_TCI(week, climate_type)
        if tourism_stat.exists():
            month = get_month_from_week(week.period)
            if month != last_month:
                tourism_coef = calculate_tourism_coef(tourism_stat, month)
                last_month = month
        else:
            tourism_coef = get_tourism_coef_by_city_size(city.city_size, climate_type)
        week_score = round(TCI * 0.78 + tourism_coef * 0.22,2)
        if week_score > 5:
            week_score = 5
        weekly_scores.append({"period": week.period, "score": week_score})

    df = pd.DataFrame(weekly_scores)
    best_weeks = df.sort_values("score", ascending=False).head(5)

    return {"df": df, "best_weeks": best_weeks}


def get_tourism_coef_by_city_size(city_size, climate_type):
    if city_size == "very big":
        if climate_type in ["temperate", "cool"]:
            return 1
        return 0.2
    elif city_size == "big":
        if climate_type in ["temperate", "cool"]:
            return 1.5
        return 0.5
    elif city_size == "large":
        if climate_type in ["temperate", "cool"]:
            return 2
        return 0.7
    elif city_size == "average":
        if climate_type in ["temperate", "cool"]:
            return 3
        return 1
    if climate_type in ["temperate", "cool"]:
        return 3
    return 1.2

def get_climate_type_by_lat(lat):
    lat = abs(lat)
    if lat <= 35:
        return "warm"
    elif lat <= 57:
        return "temperate"
    return "cool"


def calculate_tourism_coef(tourism_stat, month):
    occupancy_rate = tourism_stat.get(month=month).occupancy_rate
    if occupancy_rate:
        return get_occup_rate_score(occupancy_rate)
    return 0


def get_month_from_week(period):
    start = datetime.date(1, 1, 1)
    middle_of_week = start + datetime.timedelta(days=(period - 1) * 7 + 3)
    return middle_of_week.month


def get_occup_rate_score(occupancy_rate):
    if occupancy_rate <= 30:
        return 5
    elif occupancy_rate <= 50:
        return 4
    elif occupancy_rate <= 70:
        return 3
    elif occupancy_rate <= 85:
        return 2
    return 1


def calculate_TCI(weekly_data, climate_type):
    CID = get_CID_CIA_score(weekly_data.max_temperature, weekly_data.min_relative_humidity, climate_type)
    CIA = get_CID_CIA_score(weekly_data.mean_temperature, weekly_data.mean_relative_humidity, climate_type)

    rainfall = calculate_rainfall_score(weekly_data.precipitation)
    wind_speed = calculate_wind_score(weekly_data.wind_speed, climate_type)
    daytime = calculate_daytime(weekly_data.daylight_duration)

    TCI_coef = get_TCI_coef(climate_type)

    base_TCI = (2 * (4 * CID + CIA + 2 * rainfall + 2 * daytime + wind_speed)) / 20

    return  base_TCI * TCI_coef


def get_TCI_coef(climate_type):
    if climate_type == "warm":
        return 1
    elif climate_type == "temperate":
        return 1.1
    return 1.2


def calculate_rainfall_score(precipitation):
    if precipitation <= 14.9:
        return 5
    elif precipitation <= 29.9:
        return 4.5
    elif precipitation <= 49.9:
        return 4
    elif precipitation <= 59.9:
        return 3.5
    elif precipitation <= 74.9:
        return 3
    elif precipitation <= 89.9:
        return 2.5
    elif precipitation <= 104.9:
        return 2
    elif precipitation <= 111.9:
        return 1.5
    return 1


def get_CID_CIA_score(temp, rh, climate_type):
    if climate_type == "cool":
        temp += 2

    if temp <= -20:
        score = -3
    elif temp <= -15:
        score = -3 + (temp + 10) / 5
    elif 0 <= temp < 10:
        score = -1 + temp / 5
    elif 10 <= temp < 20:
        score = 1 + (temp - 10) / 2
    elif 20 <= temp <= 27:
        score = 5
    elif 27 < temp <= 35:
        score = 5 - (temp - 27) / 2
    else:
        score = -3

    if rh <= 10:
        score -= 2
    elif 10 < rh < 30:
        score -= (30 - rh) / 10
    elif 30 <= rh <= 60:
        score += 0
    elif 60 < rh <= 80:
        score -= (rh - 60) / 10
    else:
        score -= 2

    if score > 5:
        return 5
    if score < -3:
        return -3
    return score


def calculate_wind_score(wind_speed, climate_type):
    wind_speed = wind_speed / 3.6
    if wind_speed < 0.79:
        return 2
    elif wind_speed <= 1.59:
        return 2.5 if climate_type == "temperate" else 1.5
    elif wind_speed <= 2.5:
        return 3 if climate_type == "temperate" else 1
    elif wind_speed <= 3.39:
        return 4 if climate_type == "temperate" else 0.5
    elif wind_speed <= 5.49:
        return 5 if climate_type == "temperate" else 0
    elif wind_speed <= 6.74:
        return 4 if climate_type == "temperate" else 0
    elif wind_speed <= 7.99:
        return 3 if climate_type == "temperate" else 0
    elif wind_speed <= 10.7:
        return 2 if climate_type == "temperate" else 0
    return 0


def calculate_daytime(daytime):
    daytime_minutes = daytime / 60
    if daytime_minutes >= 540:
        return 5
    elif daytime_minutes >= 480:
        return 4.5
    elif daytime_minutes >= 420:
        return 4
    elif daytime_minutes >= 360:
        return 3.5
    elif daytime_minutes >= 300:
        return 3
    elif daytime_minutes >= 240:
        return 2.5
    elif daytime_minutes >= 180:
        return 2
    elif daytime_minutes >= 120:
        return 1.5
    elif daytime_minutes >= 60:
        return 1
    return 0


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


def city_selected(request):
    city_id = request.GET.get("city_id")
    city = get_object_or_404(City, id=city_id)
    return JsonResponse({
        "name": city.name_ru,
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
        }
        for city in cities
    ]

    return JsonResponse(data, safe=False)
