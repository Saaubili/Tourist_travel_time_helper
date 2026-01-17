def calculate_TCI(weekly_data, climate_type):
    CID = get_CID_CIA_score(weekly_data.max_temperature, weekly_data.min_relative_humidity, climate_type)
    CIA = get_CID_CIA_score(weekly_data.mean_temperature, weekly_data.mean_relative_humidity, climate_type)

    rainfall = calculate_rainfall_score(weekly_data.precipitation)
    wind_speed = calculate_wind_score(weekly_data.wind_speed, climate_type)
    daytime = calculate_daytime(weekly_data.daylight_duration)

    TCI_coef = get_TCI_coef(climate_type)

    base_TCI = (2 * (4 * CID + CIA + 2 * rainfall + 2 * daytime + wind_speed)) / 20

    return base_TCI * TCI_coef


def get_TCI_coef(climate_type):
    if climate_type == "warm":
        return 1
    elif climate_type == "temperate":
        return 1.05
    return 1.1


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
        score -= (rh - 10) / 10
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
