from drf_yasg.generators import OpenAPISchemaGenerator


class CustomSchemaGenerator(OpenAPISchemaGenerator):
    def get_endpoints(self, request):
        endpoints = super().get_endpoints(request)

        filtered_endpoints = {}

        # Allowed specific Djoser auth paths and methods
        allowed_auth_paths = {
            "/auth/users/": ["post"],
            "/auth/token/login/": ["post"],
            "/auth/token/logout/": ["post"],
        }

        for path, (view_cls, methods) in endpoints.items():
            if path.startswith("/auth/"):
                # Include only if path is in allowed_auth_paths with allowed methods
                if path in allowed_auth_paths:
                    filtered_methods = [
                        (method, view)
                        for method, view in methods
                        if method.lower() in allowed_auth_paths[path]
                    ]
                    if filtered_methods:
                        filtered_endpoints[path] = (view_cls, filtered_methods)

            else:
                # Include all non-auth endpoints unfiltered
                filtered_endpoints[path] = (view_cls, methods)

        return filtered_endpoints
