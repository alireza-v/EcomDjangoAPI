## CortextCommerce

An E-commerce backend application built with [Django](https://docs.djangoproject.com/en/5.2/) and [Django REST Framework](https://www.django-rest-framework.org/).
It provides key functionalities, including product catalog and search, shopping cart operations, order processing, payment gateway integration, and JWT-based authentication, all accessible via RESTful APIs.


---
### Table of Contents
- ⚙️ [Features](#features)
- 🚀 [Installation](#installation-guide)
- ✅ [Running Tests](#running-tests)
- 🛠️ [Tech Stack](#stacks)
---

###  Features
- 🔐 **Authentication**
   - Secure login and registration using [Djoser](https://djoser.readthedocs.io/en/2.3.2/) and [SimpleJWT](https://django-rest-framework-simplejwt.readthedocs.io/en/latest/)
   - Supports password reset and user profile updates

- 🔎 **Products**
   - Hierarchical categories with flexible filtering and sorting
   - Price range and keyword search
   - Efficient product pagination for large catalogs

- 🛒 **Cart management**
   - Add, remove, and update items in the shopping cart

- 💳 **Checkout system**
   - Order creation
   - Invoice generation
   - Order history tracking to view past orders

-  💸 **Payments**
   - Integrates with [Zibal](https://zibal.ir/) payment gateway for secure checkout

---

### Installation Guide

#### 🐳 Run with Docker
1. Build and start containers
   ```bash
   docker compose up --build
   ```
2. Access the backend
   - API: `http://localhost:9000/`
   - Admin: `http://localhost:9000/admin/`
3. Stop containers
   ```bash
   docker compose down
   ```
4. (**Optional**) Seed the database with demo data
   Run this command inside your project directory:
   ```bash
   docker compose exec web python manage.py seed_data
   ```


---

### Running Tests

The backend is tested with [pytest-django](https://pytest-django.readthedocs.io/en/latest/), ensuring robust integration test coverage across models, serializers, and API endpoints

### Run all tests
```bash
pytest -v -x
```
- `-v`: Verbose output (show more details)
- `-x`: Stop after the first failure

### Run tests for a specific app
```bash
pytest app-name
```
Example:
```bash
pytest users -v
```

### Run tests for a specific file, class/function
```bash
pytest app-name/tests/test_file_name::class/function_name
```
Examples:
```bash
pytest users/tests/test_models.py -v
pytest users/tests/test_models.py::test_user_registration -v
```

---

### Stacks

- **[Django](https://docs.djangoproject.com/en/5.2/)**: Web framework for building the backend
- **[Django Rest Framework](https://www.django-rest-framework.org/)**: Toolkit for building RESTful APIs
- **[Djoser](https://djoser.readthedocs.io/en/2.3.2/)**: REST implementation of Django's authentication system
- **[drf-yasg](https://drf-yasg.readthedocs.io/en/stable/)**: Automated generation of Swagger/OpenAPI documentation
---
