from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('accounts/signup/', views.signup, name='signup'),
    # path("save-vessel/", views.save_vessel, name="save_vessel"),
    path("vessels/add/", views.add_vessel_from_search, name="add_vessel"),

    path('myvessels/', views.my_vessels, name='myvessels'),
    path("myvessels/<int:pk>/delete/", views.my_vessels_delete, name="myvessels_delete"),
    path("myvessels/<int:pk>/", views.my_vessels_detail, name="myvessels_detail"),
]
