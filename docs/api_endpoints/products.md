# 🛍️ API Endpoints – Products

### Products

- **GET `/api/products/`**
  List all categories/subcategories/products

  **Responses**
  - 200 OK

- **GET `/api/products/?selected={category-slug}`**
  Retrieve products in the specified category by slug

  **Responses**
  - 200 OK
  - 400 Not Found

- **GET `/api/products/?selected={category-slug}&min_price={min_price}&max_price={max_price}`**
  Filter products within a category by price range

  **Responses**
  - 200 OK

- **GET `/api/products/?selected={category-slug}&sorted={option}`**
  Sort products in the selected category by one of the options below

  **Sort options:**
  - `price_asc`: Price low to high
  - `price_desc`: Price high to low
  - `most_visited`: Most viewed products

  **Responses**
  - 200 OK

- **GET `/api/product/detail/{slug}/`**
  Retrieve product details by slug

  **Responses**
  - 200 OK
  - 404 Not Found

---

### 💬❤️ Feedback & Likes

- **POST `/api/products/feedbacks/`**
  Create feedback for a product
  **Authentication:** Required

  **Request body**
  - `product` (int, required)
  - `description` (string, required)
  - `rating` (int, min=1, max=5, optional)

  **Responses**
  - 201 Created
  - 400 Bad Request
  - 401 Unauthorized

- **POST `/api/products/likes/`**
  Toggle a like for a product
  **Authentication:** Required

  **Request body**
  - `product` (int, required)

  **Responses**
  - 201 Created
  - 200 OK
  - 404 Not Found
  - 401 Unauthorized
