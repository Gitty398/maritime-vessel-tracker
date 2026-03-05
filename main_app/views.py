from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.views.decorators.http import require_POST
from .models import SavedVessel
from django.views.decorators.http import require_http_methods
from django.contrib.auth import login

from .models import SavedVessel, VesselLocation
from .services.myshiptracking import vessels_in_bbox, MyShipTrackingError
from django.utils.dateparse import parse_datetime

import math


def nm_bbox(lat, lon, radius_nm):
    dlat = radius_nm / 60.0
    dlon = radius_nm / (60.0 * max(0.01, math.cos(math.radians(lat))))
    return lat - dlat, lat + dlat, lon - dlon, lon + dlon


@require_http_methods(["GET", "POST"])
@login_required
def home(request):
    results = []
    error = None

    if request.method == "POST":
        try:
            lat = float(request.POST["lat"])
            lon = float(request.POST["lon"])
            radius_nm = float(request.POST.get("radius_nm", 10))
            lat_min, lat_max, lon_min, lon_max = nm_bbox(lat, lon, radius_nm)

            payload = vessels_in_bbox(lat_min, lat_max, lon_min, lon_max)
            results = payload.get("data", [])

        except MyShipTrackingError as e:
            # Friendly message (and optionally show e.body while debugging)
            error = str(e)
            # error = f"{e}\n{e.body}"

        except (KeyError, ValueError) as e:
            error = f"Invalid input: {e}"

        except Exception as e:
            # keep as last resort
            error = str(e)

    return render(request, "home.html", {"results": results, "error": error})


# @login_required
# @require_POST
# def save_vessel(request):
#     # Comes from hidden inputs in the table row
#     mmsi = request.POST.get("mmsi")
#     if not mmsi:
#         return redirect("home")

#     name = request.POST.get("name", "") or ""
#     imo = request.POST.get("imo", "") or ""

#     v, _ = SavedVessel.objects.get_or_create(
#         user=request.user,
#         mmsi=int(mmsi),
#         defaults={"name": name, "imo": str(imo), "raw": {}},
#     )

#     # keep metadata fresh
#     v.name = name or v.name
#     v.imo = str(imo or v.imo or "")
#     v.save(update_fields=["name", "imo"])

#     # optional: create an initial location from the search result
#     lat = request.POST.get("lat")
#     lng = request.POST.get("lng")
#     received = request.POST.get("received")

#     ts = parse_datetime(received) if received else None
#     if lat and lng and ts:
#         VesselLocation.objects.get_or_create(
#             vessel=v,
#             ts=ts,
#             defaults={
#                 "lat": float(lat),
#                 "lng": float(lng),
#                 "sog": request.POST.get("speed") or None,
#                 "cog": request.POST.get("course") or None,
#                 "raw": {},
#             },
#         )

#     return redirect("myvessels")




def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")
    else:
        form = UserCreationForm()

    return render(request, "registration/signup.html", {"form": form})



@login_required
def my_vessels(request):
    vessels = (SavedVessel.objects.filter(user=request.user).order_by("-created_at"))
    return render(request, "my_vessels.html", {"vessels": vessels})


@login_required
@require_POST

def my_vessels_delete(request, pk):
    vessel = get_object_or_404(SavedVessel, pk=pk, user=request.user)
    vessel.delete()
    return redirect("myvessels")


@login_required

def my_vessels_detail(request, pk):
    vessel = get_object_or_404(SavedVessel, pk=pk, user=request.user)
    return render(request, "my_vessels_detail.html", {"vessel": vessel})



@login_required
@require_POST
def add_vessel_from_search(request):
    mmsi = request.POST.get("mmsi")
    if not mmsi:
        return redirect("home")

    try:
        mmsi_int = int(mmsi)
    except ValueError:
        return redirect("home")

    name = request.POST.get("name") or ""
    imo = request.POST.get("imo") or ""
    lat = request.POST.get("lat")
    lng = request.POST.get("lng")
    received = request.POST.get("received")

    vessel, _ = SavedVessel.objects.get_or_create(
        user=request.user,
        mmsi=mmsi_int,
        defaults={"name": name, "imo": str(imo)},
    )

    vessel.name = name or vessel.name
    vessel.imo = str(imo or vessel.imo or "")
    vessel.save(update_fields=["name", "imo"])

    ts = parse_datetime(received) if received else None
    if lat and lng and ts:
        VesselLocation.objects.get_or_create(
            vessel=vessel,
            ts=ts,
            defaults={"lat": float(lat), "lng": float(lng)},
        )

    return redirect("myvessels")