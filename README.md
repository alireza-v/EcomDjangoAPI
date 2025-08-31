## EcomDjangoAPI

A robust and scalable eCommerce backend built with [Django](https://docs.djangoproject.com/en/5.2/) and [DRF](https://www.django-rest-framework.org/).
It provides a comprehensive set of APIs for product browsing, cart management, checkout, and user authentication.

---
### 🌐 Localization Note
The Django model `verbose_name` fields and admin interface labels are written in **Persian (Farsi)** to provide a localized admin experience.
If you prefer English labels, you can update the `verbose_name` in your models or use Django’s built-in [translation framework](https://docs.djangoproject.com/en/stable/topics/i18n/).

---
### Table of Contents
- ⚙️ [Features](#features)
- 🚀 [Installation](#installation-guide)
- 🔧 [Environment Variables](#environment-variables)
- ✅ [Running Tests](#running-tests)
- 🛠️ [Tech Stack](#tools--technologies)
- 📚 [API Documentation](./docs/architecture.md)

---

###  Features
- 🔐 Authentication & Authorization
   - JWT-based authentication (Djoser + SimpleJWT)
   - User registration, login, logout
   - Password reset & account activation
- 🔎 Product catalog with search & filters
   - Hierarchical categories with flexible filtering & sorting
   - Price range & keyword search
   - Efficient product pagination for large catalogs
- 🛒 Cart management
   - Add & Remove products
   - Persistent cart per user
- 💳 Checkout system
   - Order creation
   - Invoice
   - Order history tracking to view past orders
   - Payment flow will be integrated later to finalize the purchase (**planned for later updates**)
- 📊 Admin tools
   - Manage products, categories, and orders
   - Track visit counts & product popularity
- 🧩 RESTful API with Swagger documentation

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

#### 💻 Local setup
1. Clone the repository
   ```bash
   git clone https://github.com/alireza-v/EcomDjangoAPI
   ```
2. Create & activate virtual environment
   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   ```
3. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```
4. Apply database migrations
   ```bash
   python manage.py migrate
   ```
5. Create a superuser
   ```bash
   python manage.py createsuperuser
   ```
6. Run the development server
   ```bash
   python manage.py runserver
   ```
7. Access the application
   - API Docs: `http://localhost:9000/swagger/`
   - Django Admin: `http://localhost:9000/admin/`

---

### Environment Variables

Before running the application, create a `.env` file in the root directory and add the following:

```env
SECRET_KEY=your-secret-key
DOMAIN=your-domain-name
SITE_NAME=your-site-name
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-email-password
```

To generate a `SECRET_KEY`, use the following code snippet

```python
from django.core.management.utils import get_random_secret_key
secret_key = get_random_secret_key()
print(secret_key)
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

### Tools & Technologies

- **[Django](https://docs.djangoproject.com/en/dev/)**: Web framework for building the backend
- **[Django Rest Framework](https://www.django-rest-framework.org/)**: Toolkit for building RESTful APIs
- **[Djoser](https://djoser.readthedocs.io/en/latest/)**: REST implementation of Django's authentication system
- **[drf-yasg](https://drf-yasg.readthedocs.io/en/stable/)**: Automated generation of Swagger/OpenAPI documentation
- **[pytest](https://docs.pytest.org/en/stable/)**: Testing framework for running test cases
- **[django-admin-interface ](https://github.com/fabiocaccamo/django-admin-interface)**: Customizable admin UI

---
