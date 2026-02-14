# configs/auth_middleware.py
from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from .security import decode_token

PUBLIC_PATHS = [
    "/auth/",
    "/docs",
    "/redoc",
    "/openapi.json",
]

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # Skip public paths
        if any(path.startswith(p) for p in PUBLIC_PATHS):
            return await call_next(request)

        # Skip preflight CORS
        if request.method == "OPTIONS":
            return await call_next(request)

        # Cek Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Missing or invalid authorization header"},
            )

        token = auth_header.replace("Bearer ", "")
        payload = decode_token(token)

        if payload is None:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Invalid or expired token"},
            )

        # Simpan user info ke request.state supaya bisa diakses di endpoint
        request.state.user = payload.get("sub")

        return await call_next(request)