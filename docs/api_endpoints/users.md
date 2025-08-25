# 👤 API Endpoints – Users



### User Authentication

- **POST `/auth/users/`**
  Register new user

  **Request body**
  - `email` (string, required)
  - `password` (string, required)
  - `username` (string, optional)

  **Responses**
  - 201 Created
  - 400 Bad Request

- **POST `/api/v1/auth/activate/{uid}/{token}/`**
  Activate user account

  **Query param**
  - `uid` (string, required)
  - `token` (string, required)

  **Responses**
  - 200 OK
  - 400 Bad Request

- **POST `/auth/jwt/create/`**
  Login (obtain access & refresh tokens)

  **Request body**
  - `email` (string, required)
  - `password` (string, required)

  **Responses**
  - 200 OK
  - 400 Bad Request
  - 401 Unauthorized

- **POST `/auth/jwt/refresh/`**
  Refresh access token

  **Request body**
  - `refresh` (string, required)

  **Responses**
  - 200 OK
  - 400 Bad Request

- **POST `/auth/jwt/verify/`**
  Verify token validity

  **Request body**
  - `token` (string, required)

  **Responses**
  - 200 OK
  - 401 Unauthorized

- **POST `/auth/jwt/logout/`**
  Logout (Refresh token blacklisted)

  **Request body**
  - `refresh` (string, required)

  **Responses**
  - 200 OK
  - 401 Unauthorized
  - 400 Bad Request


- **POST `/auth/users/reset_password/`**
  Request reset-password

  **Request body**
  - `email` (string, required)

  **Responses**
  - 204 No Content
  - 400 Bad Request

- **POST `/auth/users/reset_password_confirm/`**
  Confirm password-reset

  **Request body**
  - `uid` (string, required)
  - `token` (string, required)
  - `new_password` (string, required)

  **Responses**
  - 204 No Content
  - 400 Bad Request

