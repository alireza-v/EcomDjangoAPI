## Project Structure

### 📂 **docs/**
- Contains project documentation files.
- Includes [API Endpoints](./api_endpoints/) documentation.

---

### 📂 **core/**
- Contains core configurations and utilities, including [settings](../core/settings.py).
- Handles project-wide settings, middleware, and URL routing.

---

### 👤 **users/**
Manages user-related functionalities:
- [Models](../users/models.py): Defines user profiles and authentication logic.
- [Views](../users/views.py): Handles user-related API endpoints.
- [Serializers](../users/serializers.py): Serializes user data for API responses.
- [API Endpoints](./api_endpoints/users.md): Documentation for users app API.

---

### 🛍️ **products/**
Manages product-related functionality:
- [Models](../product/models.py): Defines product and category structures.
- [Views](../product/views.py): Handles product-related API endpoints.
- [Serializers](../product/serializers.py): Serializes product data for API responses.
- [API Endpoints](./api_endpoints/products.md): Documentation for products app API.

---

### 🛒 **carts/**
Manages cart-related functionality:
- [Models](../cart/models.py): Defines cart and cart item structures.
- [Views](../cart/views.py): Handles cart-related API endpoints.
- [Serializers](../cart/serializers.py): Serializes cart data for API responses.
- [API Endpoints](./api_endpoints/carts.md): Documentation for carts app API.

---

### 📄 **.env**
Example environment variables file for sensitive configurations, including:
- `SECRET_KEY`
- `DATABASE_URL`
- `EMAIL_HOST_USER`
- `EMAIL_HOST_PASSWORD`
