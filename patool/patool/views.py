from django.shortcuts import render


def default_index(request):
    """Show a basic index page for the application"""
    return render(request, 'registration/landing.html')
