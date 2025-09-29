from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Min, Q
from .models import Event

# Create your views here.
def event_list(request):
    q = request.GET.get("q", "").strip()
    date_from = request.GET.get("from", "").strip()
    date_to = request.GET.get("to", "").strip()

    events = Event.objects.filter(published=True).annotate(
        lowest_price=Min("ticket_types__price")
    )

    # Keyword filter (title/description/venue name)
    if q:
        events = events.filter(
            Q(title__icontains=q) |
            Q(description__icontains=q) |
            Q(venue__name__icontains=q)
        )

    # Date range (optional; ignore invalid)
    from datetime import datetime
    def parse_dt(s):
        try: return datetime.fromisoformat(s)
        except Exception: return None

    df = parse_dt(date_from)
    dt = parse_dt(date_to)
    if df: events = events.filter(starts_at__gte=df)
    if dt: events = events.filter(starts_at__lte=dt)

    events = events.order_by("starts_at")

    paginator = Paginator(events, 12)  # 12 per page
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(request, "events/event_list.html", {
        "page_obj": page_obj,
        "q": q, "date_from": date_from, "date_to": date_to,
    })

def event_detail(request, pk):
    event = get_object_or_404(
        Event.objects.select_related("venue").prefetch_related("ticket_types"),
        pk=pk, published=True
    )
    return render(request, "events/event_detail.html", {"event": event})