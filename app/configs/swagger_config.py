from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

PUBLIC_PATHS = [
    "/auth/",
]

def swagger_config(app: FastAPI):
    def openapi():
        if app.openapi_schema:
            return app.openapi_schema

        openapi_schema = get_openapi(
            title=app.title,
            version=app.version,
            description=app.description,
            routes=app.routes,
        )

        openapi_schema["components"]["securitySchemes"] = {
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
                "description": "JWT token obtained from /auth/ endpoint",
            }
        }

        # Terapkan security ke setiap endpoint
        for path, methods in openapi_schema.get("paths", {}).items():
            is_public = path in PUBLIC_PATHS
            for method_detail in methods.values():
                if isinstance(method_detail, dict):
                    method_detail["security"] = [] if is_public else [{"BearerAuth": []}]

        app.openapi_schema = openapi_schema
        return app.openapi_schema

    return openapi