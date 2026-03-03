from django.urls import path
from .api_views import NearbyVesselsSearchAPIView

urlpatterns = [
    path("search/nearby/", NearbyVesselsSearchAPIView.as_view(), name="api-search-nearby"),
]