from django.views.decorators.cache import cache_page
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.http import HttpResponse  #for CSV export
from django.db.models import Min, Sum, F, DecimalField, IntegerField, Q  #unified imports
from django.db.models import Sum as DSum, F, IntegerField, DecimalField
from django.db.models.functions import Coalesce
from orders.models import OrderItem, Order # for dashboard stats
from .forms import VenueForm, EventForm
from .models import Venue, Event
from django.http import HttpResponseForbidden


# ---------- Public: list + detail ----------
@cache_page(60 * 15)  # cache for 15 minutes
def event_list(request):
    q = request.GET.get("q", "").strip()
    date_from = request.GET.get("from", "").strip()
    date_to = request.GET.get("to", "").strip()

    events = (
        Event.objects.filter(published=True)
        .select_related("venue")                 
        .prefetch_related("ticket_types")        
        .annotate(lowest_price=Min("ticket_types__price"))
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

    return render(
        request,
        "events/event_list.html",
        {"page_obj": page_obj, "q": q, "date_from": date_from, "date_to": date_to},
    )



def event_detail(request, pk):
    event = get_object_or_404(
        Event.objects.only("slug", "published"), pk=pk, published=True
    )
    return redirect("event_detail_slug", slug=event.slug, permanent=True)

@cache_page(60 * 15)  # cache for 15 minutes
def event_detail_slug(request, slug):
    event = get_object_or_404(
        Event.objects.select_related("venue").prefetch_related("ticket_types"),
        slug=slug, published=True
    )
    return render(request, "events/event_detail.html", {"event": event})


# ---------- Organizer: CRUD ----------
@login_required
def venue_create(request):
    if request.method == "POST":
        form = VenueForm(request.POST)
        if form.is_valid():
            venue = form.save(commit=False)
            venue.created_by = request.user
            venue.save()
            messages.success(request, "Venue created successfully.")
            return redirect("event_list")
    else:
        form = VenueForm()
    return render(request, "events/venue_form.html", {"form": form})


@login_required
def event_create(request):
    if request.method == "POST":
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            ev = form.save(commit=False)
            ev.created_by = request.user
            ev.save()
            messages.success(request, "Event created successfully.")
            return redirect("event_list")
    else:
        form = EventForm()
    return render(request, "events/event_form.html", {"form": form})


@login_required
def event_update(request, pk):
    event = get_object_or_404(Event, pk=pk)

    if not (
        request.user.is_superuser
        or (event.created_by and event.created_by == request.user)
    ):
        messages.error(request, "You are not allowed to edit this event.")
        return redirect("event_detail_slug", slug=event.slug)

    if request.method == "POST":
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, "Event updated successfully.")
            return redirect("event_detail_slug", slug=event.slug)
    else:
        form = EventForm(instance=event)

    return render(request, "events/event_form.html", {"form": form})

@login_required
def venue_update(request, pk):
    venue = get_object_or_404(Venue, pk=pk)

    if not (
        request.user.is_superuser
        or (venue.created_by and venue.created_by == request.user)
    ):
        messages.error(request, "You are not allowed to edit this venue.")
        return redirect("event_list")

    if request.method == "POST":
        form = VenueForm(request.POST, instance=venue)
        if form.is_valid():
            form.save()
            messages.success(request, "Venue updated successfully.")
            return redirect("event_list")
    else:
        form = VenueForm(instance=venue)

    return render(request, "events/venue_form.html", {"form": form})


# ---------- Organizer: Dashboard & CSV ----------
@login_required
def organizer_dashboard(request):
    if not request.user.is_staff:
        messages.error(request, "Organizer dashboard is restricted.")
        return redirect("event_list")

    # Per-row annotations (for the table)
    tt_capacity = Coalesce(Sum("ticket_types__capacity"), 0, output_field=IntegerField())

    sold_q = Coalesce(
        Sum(
            "ticket_types__orderitem__qty",
            filter=Q(ticket_types__orderitem__order__status__in=["PENDING", "PAID"]),
        ),
        0,
        output_field=IntegerField()
    )

    revenue = Coalesce(
        Sum(
            F("ticket_types__orderitem__qty") * F("ticket_types__orderitem__unit_price"),
            filter=Q(ticket_types__orderitem__order__status__in=["PENDING", "PAID"]),
            output_field=DecimalField(max_digits=12, decimal_places=2),
        ),
        0,
        output_field=DecimalField(max_digits=12, decimal_places=2),
    )

    qs = (
        Event.objects
        .select_related("venue")
        .annotate(total_capacity=tt_capacity, sold=sold_q, revenue=revenue)
        .annotate(remaining=Coalesce(F("total_capacity") - F("sold"), 0, output_field=IntegerField()))
        .order_by("-starts_at")
    )

    # Footer totals: aggregate on the underlying relations (NOT on annotated aliases)
    totals_raw = Event.objects.filter(pk__in=qs.values("pk")).aggregate(
        total_capacity=Coalesce(Sum("ticket_types__capacity"), 0, output_field=IntegerField()),
        sold=Coalesce(
            Sum(
                "ticket_types__orderitem__qty",
                filter=Q(ticket_types__orderitem__order__status__in=["PENDING", "PAID"]),
            ),
            0,
            output_field=IntegerField()
        ),
        revenue=Coalesce(
            Sum(
                F("ticket_types__orderitem__qty") * F("ticket_types__orderitem__unit_price"),
                filter=Q(ticket_types__orderitem__order__status__in=["PENDING", "PAID"]),
                output_field=DecimalField(max_digits=12, decimal_places=2),
            ),
            0,
            output_field=DecimalField(max_digits=12, decimal_places=2)
        ),
    )
    totals = {
        "total_capacity": totals_raw["total_capacity"],
        "sold": totals_raw["sold"],
        "revenue": totals_raw["revenue"],
        "remaining": (totals_raw["total_capacity"] or 0) - (totals_raw["sold"] or 0),
    }

    return render(request, "events/dashboard.html", {"events": qs, "totals": totals})


@staff_member_required  # only staff can export
def export_events_csv(request):
    """
    Export events to CSV (id, title, venue, starts_at, ends_at, published, lowest_price, slug).
    """
    import csv

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="events.csv"'
    writer = csv.writer(response)

    # header row
    writer.writerow(["id", "title", "venue", "starts_at", "ends_at",
                     "published", "lowest_price", "slug"])

    qs = (
        Event.objects
        .select_related("venue")
        .annotate(lowest_price=Min("ticket_types__price"))
        .order_by("starts_at")
    )

    for e in qs:
        writer.writerow([
            e.id,
            e.title,
            e.venue.name if e.venue_id else "",
            e.starts_at,
            e.ends_at,
            e.published,
            e.lowest_price or "",
            getattr(e, "slug", ""),
        ])

    return response

@login_required
def event_delete(request, pk):
    event = get_object_or_404(Event, pk=pk)

    if not (
        request.user.is_superuser
        or (event.created_by and event.created_by == request.user)
    ):
        messages.error(request, "You are not allowed to delete this event.")
        return redirect("event_detail_slug", slug=event.slug)

    if request.method == "POST":
        event.delete()
        messages.success(request, "Event deleted.")
        return redirect("event_list")

    return render(request, "events/event_confirm_delete.html", {"event": event})


@login_required
def venue_delete(request, pk):
    venue = get_object_or_404(Venue, pk=pk)

    if not (
        request.user.is_superuser
        or (venue.created_by and venue.created_by == request.user)
    ):
        messages.error(request, "You are not allowed to delete this venue.")
        return redirect("event_list")

    if request.method == "POST":
        venue.delete()
        messages.success(request, "Venue deleted.")
        return redirect("event_list")

    return render(request, "events/venue_confirm_delete.html", {"venue": venue})
