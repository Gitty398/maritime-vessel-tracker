from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.views.decorators.http import require_POST
from .models import SavedVessel
from django.views.decorators.http import require_http_methods
from django.contrib.auth import login
from .forms import SavedVesselForm
from django.db import IntegrityError
from .services.marinesia import vessels_nearby_bbox, MarinesiaError
from .api_views import radius_nm_to_bbox

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
                try:
                    payload = vessels_nearby_bbox(lat_min, lat_max, lon_min, lon_max)
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
    vessels = (
        SavedVessel.objects
        .filter(user=request.user)
        .order_by("-created_at")
    )
    return render(request, "my_vessels.html", {"vessels": vessels})



@login_required
@require_POST

def my_vessels_delete(request, pk):
    v = get_object_or_404(SavedVessel, pk=pk, user=request.user)
    v.delete()
    return redirect("myvessels")


@login_required
def my_vessels_detail(request, pk):
    vessel = get_object_or_404(SavedVessel, pk=pk, user=request.user)
    return render(request, "my_vessels_detail.html", {"vessel": vessel})

@login_required
def myvessels_create(request):
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
def myvessels_update(request, pk):
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

    return render(request, "myvessels_form.html", {"form": form, "mode": "edit", "vessel": vessel})
