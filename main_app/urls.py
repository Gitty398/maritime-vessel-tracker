from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("accounts/signup/", views.signup, name="signup"),

    path("myvessels/", views.my_vessels, name="myvessels"),
    path("search/add-vessels/", views.add_vessels_from_search, name="add_vessels_from_search"),
    
    path("myvessels/add/", views.my_vessels_add, name="myvessels_add"),
    path("myvessels/<int:pk>/edit/", views.my_vessels_edit, name="myvessels_edit"),
    path("myvessels/<int:pk>/delete/", views.my_vessels_delete, name="myvessels_delete"),
    
    path("myvessels/<int:pk>/", views.my_vessels_detail, name="myvessels_detail"),

    path("api/my-vessels/<int:mmsi>/update-location/", views.update_location_by_mmsi, name="update_location_by_mmsi"),
    
]