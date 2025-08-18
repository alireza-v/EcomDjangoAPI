# 🛒 API Endpoints – Cart

- **GET/POST `/api/checkout/carts/`**
  List or create cart items
  **Auth required:** ✅ Yes

  **Request body**
  - `action` (string, required) — choices: `add`, `remove`
  - `product` (int, required) — product ID
  - `quantity` (int, optional) — number of items

  **Responses**
  - 201 Created
  - 401 Unauthorized

- **POST `/api/checkout/cart/drop/`**
  Clear all items from user cart
  **Auth required:** ✅ Yes

  **Responses**
  - 200 OK
  - 400 Bad Request
  - 401 Unauthorized

- **POST `/api/checkout/`**
  Start checkout and create an order
  **Auth required:** ✅ Yes

  **Responses**
  - 201 Created
  - 400 Bad Request
  - 401 Unauthorized
