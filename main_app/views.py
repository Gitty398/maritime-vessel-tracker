from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.views.decorators.http import require_POST
from .models import SavedVessel
from django.contrib.auth import login
from .forms import SavedVesselForm
from django.db import IntegrityError

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


def home(request):
    return render(request, 'home.html')


@login_required
def my_vessels(request):
    vessels = (SavedVessel.objects.filter(user=request.user).order_by("-created_at"))
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