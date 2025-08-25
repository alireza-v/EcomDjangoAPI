from drf_yasg.generators import OpenAPISchemaGenerator


class CustomSchemaGenerator(OpenAPISchemaGenerator):
    def get_endpoints(self, request):
        endpoints = super().get_endpoints(request)

        filtered_endpoints = {}

        # Allowed Djoser paths
        allowed_auth_paths = {
            "/auth/users/": ["post"],
            "/auth/jwt/create/": ["post"],
            "/auth/jwt/refesh/": ["post"],
            "/auth/jwt/verify/": ["post"],
            "/auth/jwt/logout/": ["post"],
            "/auth/users/reset_password/": ["post"],
            "/auth/users/reset_password_confirm/": ["post"],
        }

        for path, (view_cls, methods) in endpoints.items():
            if path.startswith("/auth/"):
                if path in allowed_auth_paths:
                    filtered_methods = [
                        (method, view)
                        for method, view in methods
                        if method.lower() in allowed_auth_paths[path]
                    ]
                    if filtered_methods:
                        filtered_endpoints[path] = (view_cls, filtered_methods)

            else:
                filtered_endpoints[path] = (view_cls, methods)

        return filtered_endpoints
