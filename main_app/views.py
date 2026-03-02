from django.shortcuts import render
from django.http import HttpResponse

def home(request):
    return HttpResponse('<h1>Welcome to the Maritime Vessel Tracker Application</h1>')


def myvessels(request):
    return render(request, 'myvessels.html')
