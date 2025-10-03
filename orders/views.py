from decimal import Decimal

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from events.models import TicketType
from .cart import add_item, set_qty, remove_item, items_with_details, empty
from .models import Order, OrderItem


def cart_detail(request):
    items, grand = items_with_details(request.session, TicketType)
    return render(request, "orders/cart.html", {"items": items, "grand_total": grand})


@require_POST
def cart_add(request, ticket_type_id):
    tt = get_object_or_404(TicketType, pk=ticket_type_id)
    try:
        qty = max(1, int(request.POST.get("qty", "1")))
    except ValueError:
        qty = 1

    # enforce per_user_limit and remaining capacity
    current_qty = int(request.session.get("cart", {}).get(str(tt.id), 0))
    desired_total = current_qty + qty
    if tt.per_user_limit and desired_total > tt.per_user_limit:
        messages.error(request, f"Limit {tt.per_user_limit} per user for {tt.name}.")
        return redirect("event_detail", pk=tt.event_id)

    remaining = tt.remaining_capacity()
    if desired_total > remaining:
        messages.error(request, f"Only {remaining} tickets remaining for {tt.name}.")
        return redirect("event_detail", pk=tt.event_id)

    add_item(request.session, tt.id, qty)
    messages.success(request, f"Added {qty} × {tt.name} to your cart.")
    return redirect("cart_detail")


@require_POST
def cart_update(request, ticket_type_id):
    tt = get_object_or_404(TicketType, pk=ticket_type_id)
    try:
        qty = int(request.POST.get("qty", "1"))
    except ValueError:
        qty = 1

    if qty < 0:
        qty = 0

    if qty > 0:
        if tt.per_user_limit and qty > tt.per_user_limit:
            messages.error(request, f"Limit {tt.per_user_limit} per user for {tt.name}.")
            return redirect("cart_detail")
        remaining = tt.remaining_capacity()
        if qty > remaining:
            messages.error(request, f"Only {remaining} tickets remaining for {tt.name}.")
            return redirect("cart_detail")

    set_qty(request.session, tt.id, qty)
    messages.success(request, "Cart updated.")
    return redirect("cart_detail")


@require_POST
def cart_remove(request, ticket_type_id):
    remove_item(request.session, ticket_type_id)
    messages.info(request, "Item removed from cart.")
    return redirect("cart_detail")


@login_required
def checkout(request):
    items, grand = items_with_details(request.session, TicketType)
    if not items:
        messages.info(request, "Your cart is empty.")
        return redirect("cart_detail")

    # Final validation & atomic order creation
    with transaction.atomic():
        # re-check limits/remaining just before creation
        for it in items:
            tt = it["ticket_type"]
            qty = it["qty"]
            if tt.per_user_limit and qty > tt.per_user_limit:
                messages.error(request, f"Limit {tt.per_user_limit} per user for {tt.name}.")
                return redirect("cart_detail")
            remaining = tt.remaining_capacity()
            if qty > remaining:
                messages.error(request, f"Only {remaining} tickets remaining for {tt.name}.")
                return redirect("cart_detail")

        order = Order.objects.create(user=request.user, status="PAID", total=Decimal("0.00"))
        total = Decimal("0.00")
        for it in items:
            tt = it["ticket_type"]
            qty = it["qty"]
            unit = it["unit_price"]
            OrderItem.objects.create(order=order, ticket_type=tt, qty=qty, unit_price=unit)
            total += unit * qty

        order.total = total
        order.save()

    # Email receipt (console in dev; SMTP if configured via env)
    subject = f"StagePass - Order #{order.pk} confirmed"
    site_root = request.build_absolute_uri("/").rstrip("/")
    order_url = site_root + reverse("order_detail", args=[order.pk])
    message = (
        f"Thanks for your purchase!\n\n"
        f"Order #{order.pk}\n"
        f"Total: ${order.total}\n\n"
        f"View your order: {order_url}\n"
    )
    recipient = [request.user.email] if request.user.email else []
    if recipient:
        try:
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient, fail_silently=True)
        except Exception:
            # don't block checkout on email errors
            pass

    empty(request.session)
    messages.success(request, f"Order #{order.pk} confirmed. Thank you!")
    return render(request, "orders/receipt.html", {"order": order})


@login_required
def my_orders(request):
    orders = (
        Order.objects.filter(user=request.user)
        .prefetch_related("items__ticket_type__event")
        .order_by("-created_at")
    )
    return render(request, "orders/my_orders.html", {"orders": orders})


@login_required
def order_detail(request, pk):
    order = get_object_or_404(
        Order.objects.prefetch_related("items__ticket_type__event"),
        pk=pk, user=request.user
    )
    return render(request, "orders/order_detail.html", {"order": order})
