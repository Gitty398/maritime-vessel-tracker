from django.urls import path
from . import api_views

urlpatterns = [
    path("search/nearby/", api_views.NearbySearchAPIView.as_view()),
    # path("my-vessels/save/", api_views.save_vessels),
    
    # path("my-vessels/", api_views.SavedVesselListCreateAPIView.as_view()),
    # path("my-vessels/<int:pk>/", api_views.SavedVesselDetailAPIView.as_view()),
    # path("my-vessels/<int:vessel_id>/locations/", api_views.VesselLocationListAPIView.as_view()),
    # path("my-vessels/<int:vessel_id>/locations/create/", api_views.VesselLocationCreateAPIView.as_view()),

    path("my-vessels/<int:mmsi>/update-location/", api_views.update_location_by_mmsi, name="api_update_location"),
    path("my-vessels/update-locations/", api_views.update_all_locations, name="api_update_all_locations"),
]