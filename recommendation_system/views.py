from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from data_receiver.models import City, WeatherData
from .form import CitySelectForm


def main_page(request):
    city_id = request.session.get('selected_city_id')
    selected_city = None
    if city_id:
        selected_city = get_object_or_404(City, id=city_id)
    context = {
        "selected_city": selected_city,
    }
    return render(request, "recommendation_system/select_page.html", context)



def save_city_selection(request):
    city_id = request.POST.get("city_id")
    city = get_object_or_404(City, id=city_id)

    request.session['selected_city_id'] = city.id

    return JsonResponse({
        "success": True,
        "city": {
            "name": city.name_ru,
            "lat": city.latitude,
            "lon": city.longitude,
            "population": city.population,
        }
    })


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
