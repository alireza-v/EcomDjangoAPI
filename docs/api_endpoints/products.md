# 🛍️ API Endpoints – Products

### Products

- **GET `/api/v1/products/categories/`**
  List categories with their products listed

  **Responses**
  - 200 OK

- **GET `/api/v1/products/`**
  List products

  **Responses**
  - 200 OK

- **GET `/api/v1/products/?category={category-slug}`**
  Retrieve products in the specified category by slug

  **Responses**
  - 200 OK
  - 400 Not Found

- **GET `/api/v1/products/?category={category-slug}&min_price={min_price}&max_price={max_price}`**
  Filter products by price within a category

  **Responses**
  - 200 OK

- **GET `/api/v1/products/?category={category-slug}&ordering={option}`**
  Sort products in the selected category by one of the options below

  **Sort options:**
  - `price_asc`: Price low to high
  - `price_desc`: Price high to low
  - `most_visited`: Most viewed products
  - `created_at`: last created item

  **Responses**
  - 200 OK

- **GET `/api/v1/products/{str:slug}/`**
  Retrieve product details using slug

  **Responses**
  - 200 OK
  - 404 Not Found

---

### 💬❤️ Feedback & Likes

- **GET/POST `/api/v1/products/<int:product_id>/feedbacks/`**
  List & Create feedback on a product
  **Authentication:**
  - GET not required
  - POST required

  **Request body(POST)**
  - `comment` (string, required)
  - `rate` (int, min=1, max=5, optional,default=1)

  **Param(GET)**
  - `product_id(int)`

  **Responses**
  - 201 Created
  - 200 OK
  - 401 Unauthorized

- **POST `/api/v1/products/likes/`**
  Like or unlike a product
  **Authentication:** Required

  **Request body**
  - `product` (int, required)

  **Responses**
  - 201 Created
  - 200 OK
  - 404 Not Found
  - 401 Unauthorized
