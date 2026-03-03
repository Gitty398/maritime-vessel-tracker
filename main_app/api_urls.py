from django.urls import path
from .api_views import NearbyVesselsSearchAPIView, SaveVesselsAPIView

urlpatterns = [
    path("search/nearby/", NearbyVesselsSearchAPIView.as_view(), name="api-search-nearby"),
    path("my-vessels/save/", SaveVesselsAPIView.as_view(), name="api-my-vessels-save"),
]