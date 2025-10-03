# events/models.py
from django.db import models
from django.utils.text import slugify
from django.db.models import Sum

class Venue(models.Model):
    name = models.CharField(max_length=120)
    address = models.TextField(blank=True)
    capacity = models.PositiveIntegerField(default=0)
    def __str__(self): return self.name

class Event(models.Model):
    venue = models.ForeignKey(Venue, on_delete=models.PROTECT, related_name="events")
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)  # NEW
    description = models.TextField()
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    published = models.BooleanField(default=False)
    image = models.URLField(blank=True)

    def __str__(self):
        return f"{self.title} @ {self.venue}"

    def save(self, *args, **kwargs):
        # generate slug once (or when title changes and slug empty)
        if not self.slug:
            base = slugify(self.title)[:200] or "event"
            slug = base
            i = 2
            while Event.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{i}"
                i += 1
            self.slug = slug
        super().save(*args, **kwargs)

class TicketType(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="ticket_types")
    name = models.CharField(max_length=120)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    capacity = models.PositiveIntegerField(default=0)
    per_user_limit = models.PositiveIntegerField(default=4)
    def __str__(self): return f"{self.name} - {self.event.title}"

    def sold_quantity(self):
        from orders.models import OrderItem
        return (
            OrderItem.objects
            .filter(ticket_type=self, order__status__in=["PENDING", "PAID"])
            .aggregate(total=Sum("qty"))["total"] or 0
        )

    def remaining_capacity(self):
        return max(self.capacity - self.sold_quantity(), 0)
