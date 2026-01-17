from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from data_receiver.models import City


def city_selected(request):
    city_id = request.GET.get("city_id")
    city = get_object_or_404(City, id=city_id)
    return JsonResponse({
        "name": city.name_ru,
    })


def city_search(request):
    city_name = request.GET.get("city_name", "")

    cities = City.objects.filter(name_ru__istartswith=city_name).order_by("-population")[:10]

    data = [
        {
            "id": city.id,
            "name": city.name_ru,
            "lat": city.latitude,
            "lon": city.longitude
        }
        for city in cities
    ]

    return JsonResponse(data, safe=False)
