# 🛒 API Endpoints – Cart

- **GET/POST `/api/v1/checkout/cart/`**
  List & Create cart items
  **Auth required:** ✅ Yes

  **Request body**
  - `product_id` (int, required)-> product identifier
  - `action` (string, required) — choices: `add`, `remove` | default: `add`
  - `quantity` (int, not required) — default: `1`

  **Responses**
  - 201 Created
  - 401 Unauthorized
  - 400 Bad Request

- **DELETE `/api/v1/checkout/cart/clear/`**
  Clear user cart
  **Auth required:** ✅ Yes

  **Responses**
  - 200 OK
  - 204 No Content
  - 401 Unauthorized

- **POST `/api/v1/checkout/`**
  Start checkout and create an order
  **Auth required:** ✅ Yes

  **Request body**
  - `address` (str, required)-> shipping address

  **Responses**
  - 201 Created
  - 400 Bad Request
  - 401 Unauthorized

- **GET `/api/v1/checkout/orders/`**
  Display orders
  **Auth required:** ✅ Yes

  **Responses**
  - 200 OK
  - 401 Unauthorized