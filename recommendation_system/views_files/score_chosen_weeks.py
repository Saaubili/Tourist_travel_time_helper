import pandas as pd
import datetime
from data_receiver.models import City, WeatherData, TourismStat
from .prepare_best_weeks import rate_every_week


def score_chosen_weeks(city_id, weeks):
    weeks_scores = rate_every_week(city_id)
    all_weeks_rated = pd.DataFrame(weeks_scores)
    needed_weeks = all_weeks_rated[all_weeks_rated['period'].isin(weeks)]
    score = needed_weeks.mean(axis=0)['score']
    return score, all_weeks_rated
