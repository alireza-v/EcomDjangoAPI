## EcomDjangoAPI

A full-featured eCommerce backend built with [Django](https://docs.djangoproject.com/en/5.2/) and [DRF](https://www.django-rest-framework.org/).
This project provides APIs for product browsing, cart management, checkout, and user authentication — everything needed to power a modern eCommerce platform.

---

### Table of Contents
- ⚙️ [Features](#features)
- 🚀 [Installation](#installation)
- 🔧 [Environment Variables](#environment-variables)
- 🌱 [Seed Data](#seed-data)
- ✅ [Running Tests](#running-tests)
- 🛠️ [Tech Stack](#tech-stack)
- 📚 [API Documentation](./docs/architecture.md)

---

###  Features
- 🔐 Authentication & Authorization
   - JWT-based authentication (Djoser + SimpleJWT)
   - User registration, login, logout
   - Password reset & account activation
- 🔎 Product catalog with search & filters
   - Product browsing & search
   - Category hierarchy with filtering & sorting
   - Price range & keyword search
- 🛒 Cart management
   - Add, update, and remove items
   - Persistent cart per user
- 💳 Checkout system
   - Order creation
   - Payment flow integration ready (planned for later updates)
- 📊 Admin tools
   - Manage products, categories, and orders
   - Track visit counts & product popularity
- 🧩 RESTful API with Swagger documentation

---

### Installation

#### 🐳 Docker:
1. Build and start containers:
   ```bash
   docker-compose up --build
   ```
2. Access the backend:
   - API: `http://localhost:9000/`
   - Admin: `http://localhost:9000/admin/`

3. Stop containers:
   ```bash
   docker-compose down
   ```

#### 💻 Local setup:
1. Clone the repository:
   ```bash
   git clone https://github.com/alireza-v/EcomDjangoAPI
   ```
2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   ```
3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up the database:
   ```bash
   python manage.py migrate
   ```
5. Create a superuser for accessing the admin panel:
   ```bash
   python manage.py createsuperuser
   ```
6. Run the development server:
   ```bash
   python manage.py runserver
   ```
7. Access the API documentation at `http://localhost:8000/swagger/`.

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

To generate a `SECRET_KEY`, use the following code snippet:

```python
from django.core.management.utils import get_random_secret_key
secret_key = get_random_secret_key()
print(secret_key)
```

---

### Seed Data
To populate the database with initial data for testing:

```bash
# Apply migrations first
python manage.py migrate

# Load sample data using a custom command
python manage.py seed_data
```

### Running Tests

This project uses [pytest](https://pytest-django.readthedocs.io/en/latest/) for running the test suite.

### Run all tests:
```bash
pytest -v -x
```
- `-v`: Verbose output (show more details)
- `-x`: Stop after the first failure

### Run tests for a specific app:
```bash
pytest app-name
```
Example:
```bash
pytest users -v
```

### Run tests for a specific file, class/function:
```bash
pytest app-name/tests/test-file-name::class/function-name
```
Examples:
```bash
pytest users/tests/test_models.py
pytest users/tests/test_models.py::test_user_active
```

---

### 2. Build and Run with Docker Compose

From the root of your project:

```bash
# Build images and start containers
docker-compose up --build
```


### Tech Stack

- **[Django](https://docs.djangoproject.com/en/dev/)**: Web framework for building the backend
- **[Django Rest Framework](https://www.django-rest-framework.org/)**: Toolkit for building RESTful APIs
- **[Djoser](https://djoser.readthedocs.io/en/latest/)**: REST implementation of Django's authentication system
- **[drf-yasg](https://drf-yasg.readthedocs.io/en/stable/)**: Automated generation of Swagger/OpenAPI documentation
- **[pytest](https://docs.pytest.org/en/stable/)**: Testing framework for running test cases
- **[django-admin-interface ](https://github.com/fabiocaccamo/django-admin-interface)**: Customizable admin UI

---
