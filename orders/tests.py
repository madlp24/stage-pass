from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from events.models import Event, TicketType, Venue
from orders.models import Order, OrderItem

User = get_user_model()


def future(hours=24):
    return timezone.now() + timedelta(hours=hours)


class OrderModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="u", password="pw")

    def test_default_status_is_paid(self):
        order = Order.objects.create(user=self.user)
        self.assertEqual(order.status, "PAID")

    def test_status_choices_cover_pending_paid_cancelled(self):
        statuses = {code for code, _ in Order.STATUS_CHOICES}
        self.assertEqual(statuses, {"PENDING", "PAID", "CANCELLED"})

    def test_order_str_contains_pk(self):
        order = Order.objects.create(user=self.user)
        self.assertIn(str(order.pk), str(order))

    def test_status_can_transition(self):
        order = Order.objects.create(user=self.user, status="PENDING")
        order.status = "PAID"
        order.save()
        order.refresh_from_db()
        self.assertEqual(order.status, "PAID")

        order.status = "CANCELLED"
        order.save()
        order.refresh_from_db()
        self.assertEqual(order.status, "CANCELLED")


class OrderItemLineTotalTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="u", password="pw")
        self.venue = Venue.objects.create(name="Hall")
        self.event = Event.objects.create(
            venue=self.venue,
            title="Show",
            description="x",
            starts_at=future(24),
            ends_at=future(26),
        )
        self.tt = TicketType.objects.create(
            event=self.event,
            name="GA",
            price=Decimal("20.00"),
            capacity=50,
        )

    def test_line_total_is_qty_times_unit_price(self):
        order = Order.objects.create(user=self.user)
        item = OrderItem.objects.create(
            order=order,
            ticket_type=self.tt,
            qty=3,
            unit_price=Decimal("20.00"),
        )
        self.assertEqual(item.line_total, Decimal("60.00"))


class CartCapacityEnforcementTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="shopper", password="pw"
        )
        self.venue = Venue.objects.create(name="Hall")
        self.event = Event.objects.create(
            venue=self.venue,
            title="Small Show",
            description="x",
            starts_at=future(24),
            ends_at=future(26),
        )
        self.tt = TicketType.objects.create(
            event=self.event,
            name="GA",
            price=Decimal("5.00"),
            capacity=2,
            per_user_limit=10,
        )

    def test_cart_add_blocked_when_capacity_exhausted(self):
        order = Order.objects.create(user=self.user, status="PAID")
        OrderItem.objects.create(
            order=order,
            ticket_type=self.tt,
            qty=2,
            unit_price=Decimal("5.00"),
        )
        self.assertEqual(self.tt.remaining_capacity(), 0)

        resp = self.client.post(
            reverse("cart_add", args=[self.tt.pk]),
            data={"qty": "1"},
        )
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(self.client.session.get("cart", {}), {})

    def test_cart_add_blocked_over_per_user_limit(self):
        tt = TicketType.objects.create(
            event=self.event,
            name="VIP",
            price=Decimal("1.00"),
            capacity=100,
            per_user_limit=2,
        )
        resp = self.client.post(
            reverse("cart_add", args=[tt.pk]),
            data={"qty": "5"},
        )
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(self.client.session.get("cart", {}), {})

    def test_cart_add_succeeds_within_limits(self):
        resp = self.client.post(
            reverse("cart_add", args=[self.tt.pk]),
            data={"qty": "1"},
        )
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(
            self.client.session.get("cart", {}).get(str(self.tt.pk)),
            1,
        )


class OrderAccessControlTests(TestCase):
    def test_unauth_checkout_redirects_to_login(self):
        resp = self.client.get(reverse("checkout"))
        self.assertEqual(resp.status_code, 302)
        self.assertIn("login", resp.url)

    def test_unauth_my_orders_redirects_to_login(self):
        resp = self.client.get(reverse("my_orders"))
        self.assertEqual(resp.status_code, 302)
        self.assertIn("login", resp.url)

    def test_unauth_order_detail_redirects_to_login(self):
        resp = self.client.get(reverse("order_detail", args=[1]))
        self.assertEqual(resp.status_code, 302)
        self.assertIn("login", resp.url)
