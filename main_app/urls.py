from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('accounts/signup/', views.signup, name='signup'),

    path('myvessels/', views.my_vessels, name='myvessels'),
    path("myvessels/<int:pk>/delete/", views.my_vessels_delete, name="myvessels_delete"),
    path("myvessels/<int:pk>/", views.my_vessels_detail, name="myvessels_detail"),
]
