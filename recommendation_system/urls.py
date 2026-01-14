from django.urls import path
from . import views

urlpatterns = [
    path('', views.main_page, name='select_page'),
    path("city_searching/", views.city_search, name="city_autocomplete"),
    path("city_selected/", views.city_selected, name="city_selected"),
    path("save_city_selection/", views.save_city_selection, name="save_city_selection"),
    path("save_analytics_type/", views.save_analytics_type, name="save_analytics_type"),
    path('check_if_ready_to_analyze/', views.check_if_ready_to_analyze, name='check_if_ready_to_analyze'),
]