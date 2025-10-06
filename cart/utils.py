from .models import CartItem


def get_cart_items(user):
    """
    - Fetch user related carts & products and lock the rows for update
    - Return valid carts and out-of-stock items
    """

    user_cart = (
        CartItem.objects.filter(user=user).select_related("product").select_for_update()
    )

    if not user_cart.exists():
        return [], ["No cart found"]

    cart_items, out_of_stock = [], []

    for cart in user_cart:
        product = cart.product
        stock = product.stock
        cart_quantity = cart.quantity

        # out-of-stock items skipped
        if cart_quantity > stock:
            out_of_stock.append(product.title)
            continue

        cart_items.append(cart)

    return (cart_items, out_of_stock)
