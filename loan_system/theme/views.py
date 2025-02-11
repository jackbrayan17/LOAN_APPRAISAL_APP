from django.shortcuts import render
from django.http import HttpResponse

def theme_test(request):
    return HttpResponse("Theme app is working!")