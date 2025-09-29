from django.urls import path
from . import views

urlpatterns = [
    path("", views.event_list, name="event_list"),
    path("<int:pk>/", views.event_detail, name="event_detail"),

    # Organizer CRUD
    path("venues/new/", views.venue_create, name="venue_create"),
    path("new/", views.event_create, name="event_create"),
    path("<int:pk>/edit/", views.event_update, name="event_update"),
]
