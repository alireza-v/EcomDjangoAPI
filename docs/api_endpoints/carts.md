# 🛒 API Endpoints – Cart

- **GET/POST `/api/v1/checkout/carts/`**
  List & create cart items
  **Auth required:** ✅ Yes

  **Request body**
  - `action` (string, required) — choices: `add`, `remove`
  - `product` (int, required) — product ID
  - `quantity` (int, optional) — number of items

  **Responses**
  - 201 Created
  - 401 Unauthorized

- **POST `/api/v1/checkout/cart/drop/`**
  Reset user cart
  **Auth required:** ✅ Yes

  **Responses**
  - 200 OK
  - 400 Bad Request
  - 401 Unauthorized

- **POST `/api/v1/checkout/`**
  Start checkout and create an order
  **Auth required:** ✅ Yes

  **Responses**
  - 201 Created
  - 400 Bad Request
  - 401 Unauthorized
