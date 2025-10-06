from django.contrib.sitemaps import Sitemap
from .models import Event

class EventSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.7

    def items(self):
        return Event.objects.filter(published=True).only("slug", "updated_at" if hasattr(Event, "updated_at") else "starts_at")

    def location(self, obj):
        from django.urls import reverse
        return reverse("event_detail_slug", args=[obj.slug])

    def lastmod(self, obj):
        # Prefer updated_at if your model has it; otherwise falls back to starts_at
        return getattr(obj, "updated_at", obj.starts_at)
