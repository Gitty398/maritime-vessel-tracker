import math
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.db import transaction

from .services.marinesia import vessels_nearby_bbox, MarinesiaError
from .models import SavedVessel, VesselPosition
from .serializers import SaveVesselsRequestSerializer


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
    

class SaveVesselsAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    @transaction.atomic
    def post(self, request):
        ser = SaveVesselsRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        vessels = ser.validated_data["vessels"]

        created_count = 0
        position_count = 0
        out = []

        for v in vessels:
            mmsi = v["mmsi"]
            name = (v.get("name") or "").strip()
            imo = (v.get("imo") or "").strip()

            saved, created = SavedVessel.objects.get_or_create(
                user=request.user,
                mmsi=mmsi,
                defaults={"name": name, "imo": imo},
            )

            # Keep metadata updated
            changed = False
            if name and saved.name != name:
                saved.name = name
                changed = True
            if imo and saved.imo != imo:
                saved.imo = imo
                changed = True
            if changed:
                saved.save(update_fields=["name", "imo"])

            if created:
                created_count += 1

            # Automatic location ingestion (only if ts newer than latest)
            lat = v.get("lat")
            lng = v.get("lng")
            ts = v.get("ts")  # already parsed datetime or None

            if lat is not None and lng is not None and ts is not None:
                latest = saved.latest_position
                latest_ts = latest.ts if latest else None

                if latest_ts is None or ts > latest_ts:
                    VesselPosition.objects.create(
                        vessel=saved,
                        lat=lat,
                        lng=lng,
                        sog=v.get("sog"),
                        cog=v.get("cog"),
                        status=v.get("status"),
                        dest=v.get("dest"),
                        eta=v.get("eta"),
                        draught=v.get("draught"),
                        ts=ts,
                        raw=v,
                    )
                    position_count += 1

            out.append(
                {
                    "id": saved.id,
                    "mmsi": saved.mmsi,
                    "name": saved.name,
                    "imo": saved.imo or None,
                    "created_at": saved.created_at,
                }
            )

        return Response(
            {
                "error": False,
                "message": f"Saved {created_count} new vessel(s). Added {position_count} position point(s).",
                "data": out,
            },
            status=status.HTTP_201_CREATED,
        )