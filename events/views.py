from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Min, Q
from .forms import VenueForm, EventForm
from .models import Venue, Event

# Create your views here.
# ---------- Public: list + detail ----------
def event_list(request):
    q = request.GET.get("q", "").strip()
    date_from = request.GET.get("from", "").strip()
    date_to = request.GET.get("to", "").strip()

    events = Event.objects.filter(published=True).annotate(
        lowest_price=Min("ticket_types__price")
    )

    if q:
        events = events.filter(
            Q(title__icontains=q) |
            Q(description__icontains=q) |
            Q(venue__name__icontains=q)
        )

    from datetime import datetime
    def parse_dt(s):
        try:
            return datetime.fromisoformat(s)
        except Exception:
            return None

    df, dt = parse_dt(date_from), parse_dt(date_to)
    if df:
        events = events.filter(starts_at__gte=df)
    if dt:
        events = events.filter(starts_at__lte=dt)

    events = events.order_by("starts_at")
    page_obj = Paginator(events, 12).get_page(request.GET.get("page"))

    return render(request, "events/event_list.html", {
        "page_obj": page_obj, "q": q, "date_from": date_from, "date_to": date_to
    })

def event_detail(request, pk):
    event = get_object_or_404(
        Event.objects.select_related("venue").prefetch_related("ticket_types"),
        pk=pk, published=True
    )
    return render(request, "events/event_detail.html", {"event": event})

# ---------- Organizer: CRUD ----------
@login_required
def venue_create(request):
    if request.method == "POST":
        form = VenueForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Venue created successfully.")
            return redirect("event_list")
    else:
        form = VenueForm()
    return render(request, "events/venue_form.html", {"form": form})

@login_required
def event_create(request):
    if request.method == "POST":
        form = EventForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Event created successfully.")
            return redirect("event_list")
    else:
        form = EventForm()
    return render(request, "events/event_form.html", {"form": form})

@login_required
def event_update(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.method == "POST":
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, "Event updated successfully.")
            return redirect("event_detail", pk=pk)
    else:
        form = EventForm(instance=event)
    return render(request, "events/event_form.html", {"form": form})