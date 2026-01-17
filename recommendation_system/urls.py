from django.urls import path
from . import views
from .views_files import saving_inputs, city_searching

urlpatterns = [
    path("", views.main_page, name='select_page'),

    path("city_searching/", city_searching.city_search, name="city_autocomplete"),
    path("city_selected/", city_searching.city_selected, name="city_selected"),

    path("save_city_selection/", saving_inputs.save_city_selection, name="save_city_selection"),
    path("save_analytics_type/", saving_inputs.save_analytics_type, name="save_analytics_type"),
    path("save_chosen_periods/", saving_inputs.save_chosen_periods, name="save_chosen_periods"),

    path("check_if_ready_to_analyze/", views.check_if_ready_to_analyze, name='check_if_ready_to_analyze'),
]
