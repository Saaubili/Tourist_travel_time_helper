from django.urls import path
from . import views

urlpatterns = [
    path('', views.main_page, name='select_page'),
    path("city_searching/", views.city_search, name="city_autocomplete"),
]