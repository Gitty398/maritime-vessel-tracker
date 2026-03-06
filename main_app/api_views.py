from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .services.geo import radius_nm_to_bbox
from .services.marinesia import MarinesiaError, vessels_nearby_bbox


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
                    "data": [],
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        lat_min, lat_max, lon_min, lon_max = radius_nm_to_bbox(lat, lon, radius_nm)

        try:
            payload = vessels_nearby_bbox(lat_min, lat_max, lon_min, lon_max)
        except MarinesiaError as e:
            return Response(
                {"error": True, "message": str(e), "data": []},
                status=e.status_code,
            )

        return Response(payload, status=status.HTTP_200_OK)