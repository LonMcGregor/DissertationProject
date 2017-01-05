from django.shortcuts import render


def default_index(request):
    return render(request, 'registration/landing.html')