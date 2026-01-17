from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from data_receiver.models import City, WeatherData, TourismStat
from .views_files import prepare_best_weeks, score_chosen_weeks


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


def check_if_ready_to_analyze(request):
    city_selected = request.session.get('selected_city_id')
    analytics_selected = request.session.get('analytics_type')

    if not city_selected or not analytics_selected:
        return JsonResponse({"best_weeks": [], "graph_data": []})
    else:
        if analytics_selected == "best_periods":
            result = prepare_best_weeks.prepare_best_periods(city_selected)
            if "error" in result:
                return JsonResponse({"status": "error", "message": result["error"]})
            rated_weeks = result["all_weeks"]
            best_weeks = result["best_weeks"]

            return JsonResponse({
                "status": "ok",
                "best_weeks": best_weeks.to_dict(orient="records"),
                "graph_data": rated_weeks.to_dict(orient="records")
            })
        else:
            weeks_numbers = map(int, request.session.get('chosen_weeks').split(','))
            period_score, graph_data = score_chosen_weeks.score_chosen_weeks(city_selected, weeks_numbers)
            return JsonResponse({"status": "ok",
                                 "period_score": round(period_score, 2),
                                 "graph_data": graph_data.to_dict(orient="records")})
