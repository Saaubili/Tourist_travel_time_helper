import pandas as pd
import datetime
from data_receiver.models import City, WeatherData, TourismStat
from . import get_weather_data, TCI_calculation


def rate_every_week(city_id):
    city = City.objects.get(id=city_id)
    tourism_stat = TourismStat.objects.filter(country=city.country)

    climate_type = get_climate_type_by_lat(city.latitude)

    succeeded, weather_result = get_weather_data.get_weather_data_for_city(city)
    if not succeeded:
        return {"error": weather_result}
    weather_result = weather_result.order_by("period")
    weekly_scores = []

    last_month = 0
    tourism_coef = 0
    for week in weather_result:
        TCI = TCI_calculation.calculate_TCI(week, climate_type)
        if tourism_stat.exists():
            month = get_month_from_week(week.period)
            if month != last_month:
                tourism_coef = calculate_tourism_coef(tourism_stat, month)
                last_month = month
        else:
            tourism_coef = get_tourism_coef_by_city_size(city.city_size, climate_type)
        week_score = round(TCI * 0.78 + tourism_coef * 0.22, 2)
        if week_score > 5:
            week_score = 5
        weekly_scores.append({"period": week.period, "score": week_score})
    return weekly_scores


def prepare_best_periods(city_id):
    weekly_scores = rate_every_week(city_id)
    all_weeks_rated = pd.DataFrame(weekly_scores)
    best_weeks = all_weeks_rated.sort_values("score", ascending=False).head(5)

    return {"all_weeks": all_weeks_rated, "best_weeks": best_weeks}


def get_tourism_coef_by_city_size(city_size, climate_type):
    if city_size == "very big":
        if climate_type in ["temperate", "cool"]:
            return 1
        return 0.8
    elif city_size == "big":
        if climate_type in ["temperate", "cool"]:
            return 1.5
        return 1
    elif city_size == "large":
        if climate_type in ["temperate", "cool"]:
            return 2
        return 1.2
    elif city_size == "average":
        if climate_type in ["temperate", "cool"]:
            return 3
        return 2
    return 3


def get_climate_type_by_lat(lat):
    lat = abs(lat)
    if lat <= 30:
        return "warm"
    elif lat <= 47:
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
