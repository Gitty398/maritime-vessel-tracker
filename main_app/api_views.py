import math
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

from .services.marinesia import vessels_nearby_bbox, MarinesiaError


def radius_nm_to_bbox(lat: float, lon: float, radius_nm: float):
    
    dlat = radius_nm / 60.0

    cos_lat = max(0.01, math.cos(math.radians(lat)))
    dlon = radius_nm / (60.0 * cos_lat)

    return lat - dlat, lat + dlat, lon - dlon, lon + dlon


class NearbyVesselsSearchAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        try:
            lat = float(request.data.get("lat"))
            lon = float(request.data.get("lon"))
            radius_nm = float(request.data.get("radius_nm", 10))
        except (TypeError, ValueError):
            return Response(
                {
                    "error": True,
                    "message": "Provide lat, lon, and optional radius_nm as numbers.",
                    "data": []
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if radius_nm <= 0 or radius_nm > 100:
            return Response(
                {
                    "error": True,
                    "message": "radius_nm must be between 0 and 100.",
                    "data": []
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        lat_min, lat_max, lon_min, lon_max = radius_nm_to_bbox(lat, lon, radius_nm)

        try:
            data = vessels_nearby_bbox(lat_min, lat_max, lon_min, lon_max)
        except MarinesiaError as e:
            return Response(
                {"error": True, "message": e.message, "data": []},
                status=e.status_code,
            )

        return Response(data, status=status.HTTP_200_OK)