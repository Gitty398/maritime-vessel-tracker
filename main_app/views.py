from django.shortcuts import render
from django.http import HttpResponse

def home(request):
    return render(request, 'home.html')


def myvessels(request):
    return render(request, 'myvessels.html')


def search(request):
    return
