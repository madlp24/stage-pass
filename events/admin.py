from django.contrib import admin
from .models import Venue, Event, TicketType
admin.site.register([Venue, Event, TicketType])

# Register your models here.
