from django.urls import path
from . import views

urlpatterns = [
    path("events/", views.event_list, name="event_list"),
    path("events/<int:pk>/", views.event_detail, name="event_detail"),
    # Organizer
    path("events/new/", views.event_create, name="event_create"),
    path("events/<int:pk>/edit/", views.event_update, name="event_update"),
    path("venues/new/", views.venue_create, name="venue_create"),
]

