from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.core.cache import cache
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.utils.dateparse import parse_datetime
from .forms import SavedVesselForm
from .models import SavedVessel, VesselLocation
from .services.geo import radius_nm_to_bbox
from .services.marinesia import MarinesiaError, vessels_nearby_bbox, latest_location_by_mmsi


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
def home(request):
    results = []
    error_message = None
    lat = None
    lon = None
    radius_nm = 10

    if request.method == "POST":
        try:
            lat = float(request.POST.get("lat"))
            lon = float(request.POST.get("lon"))
            radius_nm = float(request.POST.get("radius_nm", 10))
        except (TypeError, ValueError):
            error_message = "Please provide valid numeric values for lat, lon, and radius."
        else:
            if radius_nm <= 0 or radius_nm > 100:
                error_message = "Radius must be between 0 and 100 nautical miles."
            else:
                lat_min, lat_max, lon_min, lon_max = radius_nm_to_bbox(lat, lon, radius_nm)

                cache_key = f"bbox:{round(lat, 4)}:{round(lon, 4)}:{radius_nm}"

                try:
                    payload = cache.get(cache_key)

                    if payload is None:
                        payload = vessels_nearby_bbox(lat_min, lat_max, lon_min, lon_max)
                        cache.set(cache_key, payload, 60)
                    else:
                        print("Using cached results")

                    results = payload.get("data", []) or []

                except MarinesiaError as e:
                    error_message = str(e)
                except Exception as e:
                    error_message = f"Unexpected error: {e}"

    return render(
        request,
        "home.html",
        {
            "results": results,
            "error_message": error_message,
            "submitted_lat": lat,
            "submitted_lon": lon,
            "submitted_radius_nm": radius_nm,
        },
    )


@login_required
def my_vessels(request):
    vessels = SavedVessel.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "my_vessels.html", {"vessels": vessels})


@login_required
def add_vessels_from_search(request):
    if request.method != "POST":
        return redirect("home")

    mmsis = request.POST.getlist("mmsi")
    names = request.POST.getlist("name")
    imos = request.POST.getlist("imo")

    added = 0
    skipped = 0

    for mmsi, name, imo in zip(mmsis, names, imos):
        if not mmsi:
            continue

        _, created = SavedVessel.objects.get_or_create(
            user=request.user,
            mmsi=int(mmsi),
            defaults={
                "name": name or "",
                "imo": imo or "",
                "raw": {},
            },
        )

        if created:
            added += 1
        else:
            skipped += 1

    if added:
        messages.success(request, f"Added {added} vessel(s).")
    if skipped:
        messages.info(request, f"{skipped} vessel(s) were already saved.")

    return redirect("myvessels")


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
def my_vessels_add(request):
    if request.method == "POST":
        form = SavedVesselForm(request.POST)
        if form.is_valid():
            vessel = form.save(commit=False)
            vessel.user = request.user
            try:
                vessel.save()
                return redirect("myvessels")
            except IntegrityError:
                form.add_error("mmsi", "You already saved a vessel with this MMSI.")
    else:
        form = SavedVesselForm()

    return render(request, "myvessels_form.html", {"form": form, "mode": "add"})


@login_required
def my_vessels_edit(request, pk):
    vessel = get_object_or_404(SavedVessel, pk=pk, user=request.user)

    if request.method == "POST":
        form = SavedVesselForm(request.POST, instance=vessel)
        if form.is_valid():
            form.save()
            return redirect("myvessels")
    else:
        form = SavedVesselForm(instance=vessel)

    return render(
        request,
        "myvessels_form.html",
        {"form": form, "mode": "edit", "vessel": vessel},
    )



@login_required
@require_POST
def update_location_by_mmsi(request, mmsi: int):
    print("update_location_by_mmsi hit", mmsi)

    vessel = get_object_or_404(SavedVessel, user=request.user, mmsi=mmsi)

    try:
        payload = latest_location_by_mmsi(int(mmsi))
        print("LATEST LOCATION PAYLOAD =", payload)
    except MarinesiaError as e:
        print("MarinesiaError:", e)
        messages.error(request, str(e))
        return redirect("myvessels")
    except Exception as e:
        print("Unexpected exception calling latest_location_by_mmsi:", e)
        messages.error(request, f"Unexpected error: {e}")
        return redirect("myvessels")

    raw_data = payload.get("data", payload)

    if isinstance(raw_data, list):
        data = raw_data[0] if raw_data else {}
    elif isinstance(raw_data, dict):
        data = raw_data
    else:
        data = {}

    print("NORMALIZED DATA =", data)

    raw_ts = data.get("received") or data.get("ts")
    print("RAW TS =", raw_ts)

    ts = parse_datetime(raw_ts.replace("Z", "+00:00")) if raw_ts else None
    print("PARSED TS =", ts)

    if ts is None:
        messages.error(request, "API did not return a valid timestamp.")
        return redirect("myvessels")

    lat = data.get("lat")
    lng = data.get("lng")
    print("LAT/LNG =", lat, lng)

    if lat is None or lng is None:
        messages.error(request, "API did not return lat/lng.")
        return redirect("myvessels")

    VesselLocation.objects.get_or_create(
        vessel=vessel,
        ts=ts,
        defaults={
            "lat": float(lat),
            "lng": float(lng),
            "sog": data.get("speed") or data.get("sog"),
            "cog": data.get("course") or data.get("cog"),
            "raw": data,
        },
    )

    vessel.name = data.get("vessel_name") or vessel.name
    vessel.imo = str(data.get("imo") or vessel.imo or "")
    vessel.raw = data
    vessel.save(update_fields=["name", "imo", "raw"])

    print("update_location_by_mmsi hit", mmsi)
    print("payload =", payload)
    print("data =", data)
    print("ts =", ts)
    print("lat =", lat, "lng =", lng)

    messages.success(request, f"Updated location for MMSI {mmsi}.")
    print("Created/updated location for", mmsi, "ts=", ts, "lat=", lat, "lng=", lng)
    return redirect("myvessels")