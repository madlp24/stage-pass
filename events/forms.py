from django import forms
from .models import Venue, Event

class VenueForm(forms.ModelForm):
    class Meta:
        model = Venue
        fields = ["name", "address", "capacity"]

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ["venue", "title", "description", "starts_at", "ends_at", "published", "image"]
        widgets = {
            "starts_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "ends_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }

    def clean(self):
        cleaned = super().clean()
        s, e = cleaned.get("starts_at"), cleaned.get("ends_at")
        if s and e and e < s:
            self.add_error("ends_at", "End time must be after start time.")
        return cleaned
