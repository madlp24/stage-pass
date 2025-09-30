# orders/cart.py
from decimal import Decimal

SESSION_KEY = "cart"  # { ticket_type_id: qty }

def get_cart(session):
    return session.get(SESSION_KEY, {})

def save_cart(session, cart):
    session[SESSION_KEY] = cart
    session.modified = True

def add_item(session, ticket_type_id, qty):
    cart = get_cart(session)
    cart[str(ticket_type_id)] = cart.get(str(ticket_type_id), 0) + qty
    save_cart(session, cart)

def set_qty(session, ticket_type_id, qty):
    cart = get_cart(session)
    if qty <= 0:
        cart.pop(str(ticket_type_id), None)
    else:
        cart[str(ticket_type_id)] = qty
    save_cart(session, cart)

def remove_item(session, ticket_type_id):
    cart = get_cart(session)
    cart.pop(str(ticket_type_id), None)
    save_cart(session, cart)

def empty(session):
    save_cart(session, {})

def items_with_details(session, TicketType):
    """Return list of dicts: {ticket_type, qty, unit_price, line_total} and grand_total."""
    cart = get_cart(session)
    items = []
    grand = Decimal("0.00")
    ids = [int(k) for k in cart.keys()]
    if not ids:
        return items, grand
    qs = TicketType.objects.filter(id__in=ids).select_related("event")
    for tt in qs:
        qty = int(cart.get(str(tt.id), 0))
        unit = Decimal(tt.price)
        line_total = unit * qty
        items.append({
            "ticket_type": tt,
            "qty": qty,
            "unit_price": unit,
            "line_total": line_total,
        })
        grand += line_total
    return items, grand
