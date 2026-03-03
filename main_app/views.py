from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import SavedVessel

def home(request):
    return render(request, 'home.html')


@login_required
def my_vessels(request):
    vessels = (
        SavedVessel.objects
        .filter(user=request.user)
        .order_by("-created_at")
    )
    return render(request, "my_vessels.html", {"vessels": vessels})