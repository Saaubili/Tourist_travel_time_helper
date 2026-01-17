from django.http import JsonResponse


def save_city_selection(request):
    city_id = request.POST.get("city_id")
    request.session['selected_city_id'] = city_id
    return JsonResponse({"status": "ok"})


def save_analytics_type(request):
    analytics_type = request.POST.get("analytics_type")
    request.session['analytics_type'] = analytics_type
    return JsonResponse({"status": "ok"})


def save_chosen_periods(request):
    chosen_periods = request.POST.get("chosen_periods")
    request.session['chosen_weeks'] = chosen_periods
    return JsonResponse({"status": "ok"})
