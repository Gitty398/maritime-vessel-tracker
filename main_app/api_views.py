import math
from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_datetime

from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics

from .models import SavedVessel, VesselLocation
from .services.marinesia import vessels_in_bbox


def nm_bbox(lat, lon, radius_nm):
    dlat = radius_nm / 60.0
    dlon = radius_nm / (60.0 * max(0.01, math.cos(math.radians(lat))))
    return lat - dlat, lat + dlat, lon - dlon, lon + dlon


class TargetSearchAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        lat = float(request.data["lat"])
        lon = float(request.data["lon"])
        radius_nm = float(request.data.get("radius_nm", 10))

        lat_min, lat_max, lon_min, lon_max = nm_bbox(lat, lon, radius_nm)
        data = vessels_in_bbox(lat_min, lat_max, lon_min, lon_max)
        return Response(data)


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
@transaction.atomic

def save_vessels(request):
    vessels = request.data.get("vessels", [])
    if not isinstance(vessels, list) or not vessels:
        return Response(
            {"error": True, "message": "Send {vessels: [...]}"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    out = []

    for v in vessels:
        mmsi = v.get("mmsi")
        if not mmsi:
            continue

        saved, _ = SavedVessel.objects.get_or_create(
            user=request.user,
            mmsi=mmsi,
            defaults={
                "name": (v.get("name") or ""),
                "imo": str(v.get("imo") or ""),
                "raw": v,
            },
        )

        saved.raw = v
        if v.get("name"):
            saved.name = v["name"]
        if v.get("imo") is not None:
            saved.imo = str(v["imo"])
        saved.save()

        if v.get("lat") is not None and v.get("lng") is not None and v.get("ts") is not None:
            try:
                VesselLocation.objects.create(
                    vessel=saved,
                    lat=v["lat"],
                    lng=v["lng"],
                    sog=v.get("sog"),
                    cog=v.get("cog"),
                    ts=v["ts"],
                    raw=v,
                )
            except IntegrityError:
                pass

        out.append({"id": saved.id, "mmsi": saved.mmsi, "name": saved.name})

    return Response({"error": False, "data": out}, status=status.HTTP_201_CREATED)

class SavedVesselListCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        qs = SavedVessel.objects.filter(user=request.user).order_by("-id")
        return Response([{"id": v.id, "mmsi": v.mmsi, "name": v.name, "imo": v.imo} for v in qs])

    def post(self, request):
        v = SavedVessel.objects.create(
            user=request.user,
            mmsi=request.data["mmsi"],
            name=request.data.get("name", ""),
            imo=str(request.data.get("imo", "") or ""),
            raw=request.data.get("raw", {}),
        )
        return Response({"id": v.id}, status=status.HTTP_201_CREATED)


class SavedVesselDetailAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, request, pk):
        return get_object_or_404(SavedVessel, pk=pk, user=request.user)

    def get(self, request, pk):
        v = self.get_object(request, pk)
        return Response({"id": v.id, "mmsi": v.mmsi, "name": v.name, "imo": v.imo, "raw": v.raw})

    def put(self, request, pk):
        v = self.get_object(request, pk)
        v.name = request.data.get("name", v.name)
        v.imo = str(request.data.get("imo", v.imo) or "")
        v.save()
        return Response({"ok": True})

    def delete(self, request, pk):
        v = self.get_object(request, pk)
        v.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class VesselLocationCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, vessel_id):
        vessel = get_object_or_404(SavedVessel, pk=vessel_id, user=request.user)

        try:
            loc = VesselLocation.objects.create(
                vessel=vessel,
                lat=request.data["lat"],
                lng=request.data["lng"],
                sog=request.data.get("sog"),
                cog=request.data.get("cog"),
                ts=request.data["ts"],
                raw=request.data,
            )
        except IntegrityError:
            return Response({"error": True, "message": "Location at this ts already exists."},
                            status=status.HTTP_409_CONFLICT)

        return Response({"id": loc.id}, status=status.HTTP_201_CREATED)


class VesselLocationListAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, vessel_id):
        vessel = get_object_or_404(SavedVessel, pk=vessel_id, user=request.user)
        locations = vessel.locations.all()
        return Response([{"id": l.id, "lat": l.lat, "lng": l.lng, "ts": l.ts} for l in locations])