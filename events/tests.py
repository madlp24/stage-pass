from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from events.models import Event, TicketType, Venue, title_validator
from orders.models import Order, OrderItem

User = get_user_model()


def future(hours=24):
    return timezone.now() + timedelta(hours=hours)


class TitleValidatorTests(TestCase):
    def test_empty_title_rejected(self):
        with self.assertRaises(ValidationError):
            title_validator("")

    def test_whitespace_only_title_rejected(self):
        with self.assertRaises(ValidationError):
            title_validator("   ")

    def test_leading_trailing_whitespace_rejected(self):
        with self.assertRaises(ValidationError):
            title_validator(" My Event ")

    def test_valid_title_passes(self):
        title_validator("Jazz Night")


class EventModelTests(TestCase):
    def setUp(self):
        self.venue = Venue.objects.create(name="Main Hall", capacity=100)

    def test_valid_event_saves(self):
        ev = Event.objects.create(
            venue=self.venue,
            title="Concert",
            description="A concert.",
            starts_at=future(24),
            ends_at=future(26),
        )
        self.assertTrue(ev.pk)
        self.assertEqual(ev.slug, "concert")

    def test_duplicate_title_gets_numeric_slug_suffix(self):
        Event.objects.create(
            venue=self.venue,
            title="Same Title",
            description="x",
            starts_at=future(24),
            ends_at=future(26),
        )
        ev2 = Event.objects.create(
            venue=self.venue,
            title="Same Title",
            description="x",
            starts_at=future(48),
            ends_at=future(50),
        )
        self.assertEqual(ev2.slug, "same-title-2")

    def test_past_start_date_rejected(self):
        with self.assertRaises(ValidationError):
            Event.objects.create(
                venue=self.venue,
                title="Past",
                description="x",
                starts_at=timezone.now() - timedelta(hours=2),
                ends_at=future(24),
            )

    def test_end_before_start_rejected(self):
        with self.assertRaises(ValidationError):
            Event.objects.create(
                venue=self.venue,
                title="Backwards",
                description="x",
                starts_at=future(48),
                ends_at=future(24),
            )

    def test_end_equal_to_start_rejected(self):
        when = future(24)
        with self.assertRaises(ValidationError):
            Event.objects.create(
                venue=self.venue,
                title="Zero Length",
                description="x",
                starts_at=when,
                ends_at=when,
            )


class TicketAvailabilityTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="buyer", password="pw")
        self.venue = Venue.objects.create(name="Hall", capacity=50)
        self.event = Event.objects.create(
            venue=self.venue,
            title="Ticketed Event",
            description="x",
            starts_at=future(24),
            ends_at=future(26),
        )
        self.tt = TicketType.objects.create(
            event=self.event,
            name="General",
            price=Decimal("10.00"),
            capacity=5,
            per_user_limit=4,
        )

    def test_remaining_is_full_when_no_orders(self):
        self.assertEqual(self.tt.sold_quantity(), 0)
        self.assertEqual(self.tt.remaining_capacity(), 5)

    def test_paid_order_reduces_remaining(self):
        order = Order.objects.create(user=self.user, status="PAID")
        OrderItem.objects.create(
            order=order,
            ticket_type=self.tt,
            qty=3,
            unit_price=Decimal("10.00"),
        )
        self.assertEqual(self.tt.sold_quantity(), 3)
        self.assertEqual(self.tt.remaining_capacity(), 2)

    def test_pending_order_also_reduces_remaining(self):
        order = Order.objects.create(user=self.user, status="PENDING")
        OrderItem.objects.create(
            order=order,
            ticket_type=self.tt,
            qty=2,
            unit_price=Decimal("10.00"),
        )
        self.assertEqual(self.tt.remaining_capacity(), 3)

    def test_cancelled_order_does_not_reduce_remaining(self):
        order = Order.objects.create(user=self.user, status="CANCELLED")
        OrderItem.objects.create(
            order=order,
            ticket_type=self.tt,
            qty=5,
            unit_price=Decimal("10.00"),
        )
        self.assertEqual(self.tt.remaining_capacity(), 5)

    def test_remaining_capacity_never_negative(self):
        order = Order.objects.create(user=self.user, status="PAID")
        OrderItem.objects.create(
            order=order,
            ticket_type=self.tt,
            qty=10,
            unit_price=Decimal("10.00"),
        )
        self.assertEqual(self.tt.remaining_capacity(), 0)


class AccessControlTests(TestCase):
    def setUp(self):
        self.venue = Venue.objects.create(name="Hall")
        self.owner = User.objects.create_user(
            username="owner", password="pw"
        )
        self.intruder = User.objects.create_user(
            username="intruder", password="pw"
        )
        self.staff = User.objects.create_user(
            username="staffuser", password="pw", is_staff=True
        )
        self.event = Event.objects.create(
            venue=self.venue,
            title="Show",
            description="x",
            starts_at=future(24),
            ends_at=future(26),
            created_by=self.owner,
        )

    def _assert_redirects_to_login(self, url):
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 302)
        self.assertIn("login", resp.url)

    def test_unauth_cannot_access_event_create(self):
        self._assert_redirects_to_login(reverse("event_create"))

    def test_unauth_cannot_access_event_update(self):
        self._assert_redirects_to_login(
            reverse("event_update", args=[self.event.pk])
        )

    def test_unauth_cannot_access_event_delete(self):
        self._assert_redirects_to_login(
            reverse("event_delete", args=[self.event.pk])
        )

    def test_unauth_cannot_access_venue_create(self):
        self._assert_redirects_to_login(reverse("venue_create"))

    def test_unauth_cannot_access_dashboard(self):
        self._assert_redirects_to_login(reverse("dashboard"))

    def test_non_staff_user_redirected_from_dashboard(self):
        self.client.login(username="intruder", password="pw")
        resp = self.client.get(reverse("dashboard"))
        self.assertRedirects(resp, reverse("event_list"))

    def test_non_owner_cannot_update_event(self):
        self.client.login(username="intruder", password="pw")
        resp = self.client.post(
            reverse("event_update", args=[self.event.pk]),
            data={
                "venue": self.venue.pk,
                "title": "Hacked",
                "description": "x",
                "starts_at": future(30).strftime("%Y-%m-%dT%H:%M"),
                "ends_at": future(32).strftime("%Y-%m-%dT%H:%M"),
            },
        )
        self.assertEqual(resp.status_code, 302)
        self.event.refresh_from_db()
        self.assertEqual(self.event.title, "Show")

    def test_non_owner_cannot_delete_event(self):
        self.client.login(username="intruder", password="pw")
        resp = self.client.post(
            reverse("event_delete", args=[self.event.pk])
        )
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(Event.objects.filter(pk=self.event.pk).exists())
