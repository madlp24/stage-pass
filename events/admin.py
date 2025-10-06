from django.contrib import admin
from .models import Venue, Event, TicketType

class TicketTypeInline(admin.TabularInline):
    model = TicketType
    extra = 1

@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ("name", "capacity")
    search_fields = ("name", "address")

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "venue", "starts_at", "published")
    list_filter = ("published", "venue")
    search_fields = ("title", "description", "venue__name")
    date_hierarchy = "starts_at"
    prepopulated_fields = {"slug": ("title",)}
    inlines = [TicketTypeInline]

@admin.register(TicketType)
class TicketTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "event", "price", "capacity", "per_user_limit")
    list_filter = ("event",)
    search_fields = ("name", "event__title")
