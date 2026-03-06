# import math
# from django.conf import settings
# from django.utils.dateparse import parse_datetime
# from django.shortcuts import get_object_or_404, redirect
# from django.contrib import messages
# from django.contrib.auth.decorators import login_required
# from django.views.decorators.http import require_POST
# from rest_framework import status, permissions
# from rest_framework.response import Response
# from rest_framework.views import APIView

# from .models import SavedVessel, VesselLocation
# from .services.marinesia import vessels_in_bbox, latest_location_by_mmsi, MarinesiaError


# def nm_bbox(lat, lon, radius_nm):
#     dlat = radius_nm / 60.0
#     dlon = radius_nm / (60.0 * max(0.01, math.cos(math.radians(lat))))
#     return lat - dlat, lat + dlat, lon - dlon, lon + dlon


# def parse_marinesia_ts(value):
    
#     if not isinstance(value, str):
#         return None
    
#     return parse_datetime(value.replace("Z", "+00:00"))


# class NearbySearchAPIView(APIView):
#     permission_classes = [permissions.IsAuthenticated]

#     def post(self, request):
#         lat = float(request.data["lat"])
#         lon = float(request.data["lon"])
#         radius_nm = float(request.data.get("radius_nm", 10))

#         lat_min, lat_max, lon_min, lon_max = nm_bbox(lat, lon, radius_nm)

#         try:
#             payload = marinesia_client().vessels_in_bbox(lat_min, lat_max, lon_min, lon_max)
#         except MarinesiaError as e:
#             return Response(
#                 {"error": True, "message": str(e), "data": []},
#                 status=status.HTTP_502_BAD_GATEWAY,
#             )

#         vessels = payload.get("data", []) or []

#         return Response(
#             {
#                 "error": False,
#                 "message": f"Found {len(vessels)} vessel(s).",
#                 "data": [
#                     {
#                         "name": v.get("name"),
#                         "mmsi": v.get("mmsi"),
#                         "imo": v.get("imo"),
#                         "lat": v.get("lat"),
#                         "lng": v.get("lng"),
#                         "sog": v.get("sog"),
#                         "cog": v.get("cog"),
#                         "status": v.get("status"),
#                         "ts": v.get("ts"),
#                         "raw": v,
#                     }
#                     for v in vessels
#                 ],
#             },
#             status=status.HTTP_200_OK,
#         )


# @login_required
# @require_POST
# def update_location_by_mmsi(request, mmsi):
#     vessel = get_object_or_404(SavedVessel, user=request.user, mmsi=mmsi)

#     try:
#         payload = latest_location_by_mmsi(int(mmsi))
#     except MarinesiaError as e:
#         messages.error(request, str(e))
#         return redirect("myvessels")
#     except Exception as e:
#         messages.error(request, f"Unexpected error calling Marinesia: {e}")
#         return redirect("myvessels")

#     data = payload.get("data") or {}

#     ts = parse_marinesia_ts(data.get("ts"))
#     if not ts:
#         messages.error(request, "Marinesia did not return a valid timestamp (ts).")
#         return redirect("myvessels")

#     lat = data.get("lat")
#     lng = data.get("lng")
#     if lat is None or lng is None:
#         messages.error(request, "Marinesia did not return lat/lng.")
#         return redirect("myvessels")

#     VesselLocation.objects.get_or_create(
#         vessel=vessel,
#         ts=ts,
#         defaults={
#             "lat": float(lat),
#             "lng": float(lng),
            
#             "sog": data.get("sog"),
#             "cog": data.get("cog"),
#             "raw": data,
#         },
#     )

    
#     vessel.raw = data
#     vessel.save(update_fields=["raw"])

#     messages.success(request, f"Updated location for MMSI {mmsi}.")
#     return redirect("myvessels")


# @login_required
# @require_POST
# def update_all_locations(request):
#     ok = 0
#     failed = 0

#     for v in SavedVessel.objects.filter(user=request.user):
#         try:
#             payload = latest_location_by_mmsi(int(v.mmsi))
#             data = payload.get("data") or {}

#             ts = parse_marinesia_ts(data.get("ts"))
#             lat = data.get("lat")
#             lng = data.get("lng")
#             if not ts or lat is None or lng is None:
#                 failed += 1
#                 continue

#             VesselLocation.objects.get_or_create(
#                 vessel=v,
#                 ts=ts,
#                 defaults={
#                     "lat": float(lat),
#                     "lng": float(lng),
#                     "sog": data.get("sog"),
#                     "cog": data.get("cog"),
#                     "raw": data,
#                 },
#             )

#             v.raw = data
#             v.save(update_fields=["raw"])
#             ok += 1
#         except Exception:
#             failed += 1
#             continue

#     if failed:
#         messages.warning(request, f"Updated {ok} vessel(s); {failed} failed.")
#     else:
#         messages.success(request, f"Updated {ok} vessel(s).")

#     return redirect("myvessels")

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