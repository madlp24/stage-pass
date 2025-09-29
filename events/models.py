from django.db import models

# Create your models here.

class Venue(models.Model):
    name = models.CharField(max_length=120)
    address = models.TextField(blank=True)
    capacity = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name

class Event(models.Model):
    venue = models.ForeignKey(Venue, on_delete=models.PROTECT, related_name="events")
    title = models.CharField(max_length=200)
    description = models.TextField()
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    published = models.BooleanField(default=False)
    image = models.URLField(blank=True)

    def __str__(self):
        return f"{self.title} @ {self.venue}"

class TicketType(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="ticket_types")
    name = models.CharField(max_length=120)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    capacity = models.PositiveIntegerField(default=0)
    per_user_limit = models.PositiveIntegerField(default=4)

    def __str__(self):
        return f"{self.name} - {self.event.title}"
