from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('myvessels/', views.my_vessels, name='myvessels'),
    path('accounts/signup/', views.signup, name='signup'),
    path("myvessels/<int:pk>/delete/", views.my_vessels_delete, name="myvessels_delete"),
]
