from .cart import get_cart

def cart_info(request):
    cart = get_cart(request.session)
    count = sum(int(qty) for qty in cart.values())
    return {"cart_count": count}

