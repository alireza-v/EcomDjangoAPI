from cart.models import CartItem


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

    for item in user_cart:
        product = item.product
        stock = product.stock
        cart_quantity = item.quantity

        # out-of-stock items skipped
        if cart_quantity >= stock:
            out_of_stock.append(product.title)
            continue

        cart_items.append(item)

    return (cart_items, out_of_stock)
