from django.urls import path
from . import views

urlpatterns = [
    path("", views.event_list, name="event_list"),
    path("<int:pk>/", views.event_detail, name="event_detail"),
    path("<int:pk>/delete/", views.event_delete, name="event_delete"),
    path("s/<slug:slug>/", views.event_detail_slug, name="event_detail_slug"),
    path("dashboard/", views.organizer_dashboard, name="dashboard"),
    path("export.csv", views.export_events_csv, name="export_events_csv"),
    path("venues/new/", views.venue_create, name="venue_create"),
    path("new/", views.event_create, name="event_create"),
    path("<int:pk>/edit/", views.event_update, name="event_update"),
]
