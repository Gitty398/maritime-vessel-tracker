import math
from django.utils.dateparse import parse_datetime
from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
# from rest_framework import generics
from .services.myshiptracking import updated_vessel_location, MyShipTrackingError
from django.contrib import messages

from .models import SavedVessel, VesselLocation
# from .services.marinesia import vessels_in_bbox, updated_vessel_location
from .services.myshiptracking import vessels_in_bbox, updated_vessel_location


def nm_bbox(lat, lon, radius_nm):
    dlat = radius_nm / 60.0
    dlon = radius_nm / (60.0 * max(0.01, math.cos(math.radians(lat))))
    return lat - dlat, lat + dlat, lon - dlon, lon + dlon


class NearbySearchAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        lat = float(request.data["lat"])
        lon = float(request.data["lon"])
        radius_nm = float(request.data.get("radius_nm", 10))

        lat_min, lat_max, lon_min, lon_max = nm_bbox(lat, lon, radius_nm)

        payload = vessels_in_bbox(lat_min, lat_max, lon_min, lon_max)
        vessels = payload.get("data", [])

        return Response(
            {
                "error": False,
                "message": f"Found {len(vessels)} vessel(s).",
                "data": [
                    {
                        "name": v.get("vessel_name"),
                        "mmsi": v.get("mmsi"),
                        "imo": v.get("imo"),
                        "lat": v.get("lat"),
                        "lng": v.get("lng"),
                        "sog": v.get("speed"),
                        "cog": v.get("course"),
                        "status": v.get("nav_status"),
                        "ts": v.get("received"),
                        "raw": v,
                    }
                    for v in vessels
                ],
            },
            status=status.HTTP_200_OK,
        )


# @api_view(["POST"])
# @permission_classes([permissions.IsAuthenticated])
# @transaction.atomic

# def save_vessels(request):
#     vessels = request.data.get("vessels", [])
#     if not isinstance(vessels, list) or not vessels:
#         return Response({"error": True, "message": "Send {vessels: [...]}"}, status=400)

#     out = []

#     for v in vessels:
#         mmsi = v.get("mmsi")
#         if not mmsi:
#             continue

#         name = v.get("vessel_name") or v.get("name") or ""
#         imo = v.get("imo")
#         imo = "" if imo is None else str(imo)

#         saved, _ = SavedVessel.objects.get_or_create(
#             user=request.user,
#             mmsi=mmsi,
#             defaults={"name": name, "imo": imo, "raw": v},
#         )

#         saved.name = name or saved.name
#         saved.imo = imo or saved.imo
#         saved.raw = v
#         saved.save()

#         ts_str = v.get("received") or v.get("ts")
#         ts = parse_datetime(ts_str) if ts_str else None

#         if v.get("lat") is not None and v.get("lng") is not None and ts:
#             try:
#                 VesselLocation.objects.create(
#                     vessel=saved,
#                     lat=v["lat"],
#                     lng=v["lng"],
#                     sog=v.get("speed") if v.get("speed") is not None else v.get("sog"),
#                     cog=v.get("course") if v.get("course") is not None else v.get("cog"),
#                     ts=ts,
#                     raw=v,
#                 )
#             except IntegrityError:
#                 pass

#         out.append({"id": saved.id, "mmsi": saved.mmsi, "name": saved.name})

#     return Response({"error": False, "data": out}, status=201)

# class SavedVesselListCreateAPIView(APIView):
#     permission_classes = [permissions.IsAuthenticated]

#     def get(self, request):
#         qs = SavedVessel.objects.filter(user=request.user).order_by("-id")
#         return Response([{"id": v.id, "mmsi": v.mmsi, "name": v.name, "imo": v.imo} for v in qs])

#     def post(self, request):
#         v = SavedVessel.objects.create(
#             user=request.user,
#             mmsi=request.data["mmsi"],
#             name=request.data.get("name", ""),
#             imo=str(request.data.get("imo", "") or ""),
#             raw=request.data.get("raw", {}),
#         )
#         return Response({"id": v.id}, status=status.HTTP_201_CREATED)


# class SavedVesselDetailAPIView(APIView):
#     permission_classes = [permissions.IsAuthenticated]

#     def get_object(self, request, pk):
#         return get_object_or_404(SavedVessel, pk=pk, user=request.user)

#     def get(self, request, pk):
#         v = self.get_object(request, pk)
#         return Response({"id": v.id, "mmsi": v.mmsi, "name": v.name, "imo": v.imo, "raw": v.raw})

#     def put(self, request, pk):
#         v = self.get_object(request, pk)
#         v.name = request.data.get("name", v.name)
#         v.imo = str(request.data.get("imo", v.imo) or "")
#         v.save()
#         return Response({"ok": True})

#     def delete(self, request, pk):
#         v = self.get_object(request, pk)
#         v.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)


# class VesselLocationCreateAPIView(APIView):
#     permission_classes = [permissions.IsAuthenticated]

#     def post(self, request, vessel_id):
#         vessel = get_object_or_404(SavedVessel, pk=vessel_id, user=request.user)

#         try:
#             loc = VesselLocation.objects.create(
#                 vessel=vessel,
#                 lat=request.data["lat"],
#                 lng=request.data["lng"],
#                 sog=request.data.get("sog"),
#                 cog=request.data.get("cog"),
#                 ts=request.data["ts"],
#                 raw=request.data,
#             )
#         except IntegrityError:
#             return Response({"error": True, "message": "Location at this ts already exists."},
#                             status=status.HTTP_409_CONFLICT)

#         return Response({"id": loc.id}, status=status.HTTP_201_CREATED)


# class VesselLocationListAPIView(APIView):
#     permission_classes = [permissions.IsAuthenticated]

#     def get(self, request, vessel_id):
#         vessel = get_object_or_404(SavedVessel, pk=vessel_id, user=request.user)
#         locations = vessel.locations.all()
#         return Response([{"id": l.id, "lat": l.lat, "lng": l.lng, "ts": l.ts} for l in locations])
    


@login_required
@require_POST
def update_location_by_mmsi(request, mmsi):
    vessel = get_object_or_404(SavedVessel, user=request.user, mmsi=mmsi)

    try:
        payload = updated_vessel_location(mmsi)
    except MyShipTrackingError as e:
        messages.error(request, str(e))
        return redirect("myvessels")
    except Exception as e:
        messages.error(request, f"Unexpected error calling provider: {e}")
        return redirect("myvessels")

    data = payload.get("data") or {}

    received_raw = data.get("received") or ""
    ts = parse_datetime(received_raw.replace("Z", "+00:00")) if isinstance(received_raw, str) else None
    if not ts:
        messages.error(request, "API did not return a valid timestamp.")
        return redirect("myvessels")

    lat = data.get("lat")
    lng = data.get("lng")
    if lat is None or lng is None:
        messages.error(request, "API did not return lat/lng.")
        return redirect("myvessels")

    VesselLocation.objects.get_or_create(
        vessel=vessel,
        ts=ts,
        defaults={
            "lat": float(lat),
            "lng": float(lng),
            "sog": data.get("speed"),
            "cog": data.get("course"),
            "raw": data,
        },
    )

    vessel.name = data.get("vessel_name") or vessel.name
    vessel.imo = str(data.get("imo") or vessel.imo or "")
    vessel.raw = data
    vessel.save(update_fields=["name", "imo", "raw"])

    messages.success(request, f"Updated location for MMSI {mmsi}.")
    return redirect("myvessels")


@login_required
@require_POST

def update_all_locations(request):
    for v in SavedVessel.objects.filter(user=request.user):
        try:
            payload = updated_vessel_location(v.mmsi)
            data = payload["data"]
            ts = parse_datetime(data["received"])
            VesselLocation.objects.get_or_create(
                vessel=v,
                ts=ts,
                defaults={
                    "lat": data["lat"],
                    "lng": data["lng"],
                    "sog": data.get("speed"),
                    "cog": data.get("course"),
                    "raw": data,
                },
            )
            v.name = data.get("vessel_name") or v.name
            v.imo = str(data.get("imo") or v.imo or "")
            v.raw = data
            v.save()
        except Exception:
            continue
    return redirect("myvessels")