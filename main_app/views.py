from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from .models import SavedVessel
from django.contrib.auth import login

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