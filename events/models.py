# events/models.py
from django.db import models
from django.utils.text import slugify
from django.db.models import Sum, F, Q
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.conf import settings

User = settings.AUTH_USER_MODEL
class Venue(models.Model):
    name = models.CharField(max_length=120)
    address = models.TextField(blank=True)
    capacity = models.PositiveIntegerField(default=0)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="venues_created",
    )

    def __str__(self): return self.name


def title_validator(value: str):
    if not value or not value.strip():
        raise ValidationError("Title cannot be empty or contain only spaces.")
    if value != value.strip():
        raise ValidationError("Title cannot start or end with spaces.")


class Event(models.Model):
    venue = models.ForeignKey(Venue, on_delete=models.PROTECT, related_name="events")
    title = models.CharField(max_length=200, validators=[title_validator])
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    description = models.TextField()
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    published = models.BooleanField(default=False)
    image = models.ImageField(upload_to="events/", blank=True, null=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="events_created",
    )
    
    def __str__(self):
        return f"{self.title} @ {self.venue}"

    def clean(self):
        """Model-level validation for dates."""
        errors = {}
        now = timezone.now()

        if self.starts_at and self.starts_at < now:
            errors["starts_at"] = "Start date/time cannot be in the past."

        if self.ends_at and self.ends_at < now:
            errors["ends_at"] = "End date/time cannot be in the past."

        if self.starts_at and self.ends_at and self.ends_at <= self.starts_at:
            errors["ends_at"] = "End date/time must be after the start."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()

        if not self.slug:
            base = slugify(self.title)[:200] or "event"
            slug = base
            i = 2
            while Event.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{i}"
                i += 1
            self.slug = slug
        super().save(*args, **kwargs)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=Q(ends_at__gt=F("starts_at")),
                name="event_end_after_start",
            ),
        ]


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
