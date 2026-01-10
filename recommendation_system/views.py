from django.shortcuts import render
from django.http import JsonResponse
from data_receiver.models import City, WeatherData

def main_page(request):
    return render(request, 'recommendation_system/select_page.html')

def city_search(request):
    city_name = request.GET["city_name"]
    if len(city_name) < 2:
        return JsonResponse([], safe=False)

    cities = (
        City.objects
        .filter(name_ru__icontains=city_name)
        .order_by("-population")[:10]
    )

    data = [
        {
            "id": city.id,
            "name": city.name_ru,
            "country": city.country_ru,
        }
        for city in cities
    ]

    return JsonResponse(data, safe=False)