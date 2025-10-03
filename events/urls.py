from django.urls import path
from . import views

urlpatterns = [
    path("", views.event_list, name="event_list"),
    path("<int:pk>/", views.event_detail, name="event_detail"),           
    path("s/<slug:slug>/", views.event_detail_slug, name="event_detail_slug"),  
    # organizer
    path("dashboard/", views.organizer_dashboard, name="organizer_dashboard"),
    path("export.csv", views.export_events_csv, name="export_events_csv"),
    path("new/", views.event_create, name="event_create"),
    path("<int:pk>/edit/", views.event_update, name="event_update"),
    path("export.csv", views.export_events_csv, name="export_events_csv"),

]

