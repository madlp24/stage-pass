# core/views.py
from django.shortcuts import render
from events.models import Event

def home(request):
    events = (
        Event.objects.filter(published=True)
        .order_by("starts_at")
        .select_related("venue")[:6]
    )
    return render(request, "core/home.html", {"events": events})

def about(request):
    return render(request, "core/about.html")
