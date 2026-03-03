from django.urls import path
from .api_views import (
    NearbyVesselsSearchAPIView,
    SaveVesselsAPIView,
    MyVesselsListAPIView,
    RefreshMyVesselsLocationsAPIView,
)

urlpatterns = [
    path("search/nearby/", NearbyVesselsSearchAPIView.as_view(), name="api-search-nearby"),
    path("my-vessels/", MyVesselsListAPIView.as_view(), name="api-my-vessels"),
    path("my-vessels/save/", SaveVesselsAPIView.as_view(), name="api-my-vessels-save"),
    path("my-vessels/refresh/", RefreshMyVesselsLocationsAPIView.as_view(), name="api-my-vessels-refresh"),
]