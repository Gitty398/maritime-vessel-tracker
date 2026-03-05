from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('accounts/signup/', views.signup, name='signup'),
    # path("save-vessel/", views.save_vessel, name="save_vessel"),
    path('myvessels/', views.my_vessels, name='myvessels'),
    path("myvessels/<int:pk>/delete/", views.my_vessels_delete, name="myvessels_delete"),
    path("myvessels/<int:pk>/", views.my_vessels_detail, name="myvessels_detail"),
    path('myvessels/add/', views.my_vessels_add, name='myvessels_add'),
    path('myvessels/<int:pk>/edit/', views.my_vessels_edit, name='myvessels_edit'),
]
