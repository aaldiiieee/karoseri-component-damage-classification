from fastapi import FastAPI, Request, HTTPException
import time
from fastapi.middleware.cors import CORSMiddleware
from .routers import router
from .configs.swagger_config import swagger_config
from .configs.logging import setup_logging
from .configs.logging_middleware import LoggingMiddleware
from .configs.auth_middleware import AuthMiddleware
from .configs.cors_config import CORS_CONFIG
from fastapi.concurrency import asynccontextmanager

# Setup lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle management untuk FastAPI."""
    # Startup
    logger = setup_logging(log_level="INFO")
    logger.info("=" * 50)
    logger.info("Application starting up...")
    logger.info("=" * 50 + "\n")
    
    yield
    
    # Shutdown
    logger.info("=" * 50)
    logger.info("Application shutting down...")
    logger.info("=" * 50 + "\n")

app = FastAPI(
    title="Klasifikasi Tingkat Kerusakan Komponen Produksi Karoseri",
    description = 
        "API untuk Implementasi Metode Naive Bayes dalam Klasifikasi Tingkat Kerusakan "
        "Komponen Produksi Karoseri pada PT. Sukses Tunggal Mandiri.\n"
        "### Fitur Utama\n"
        "- **Manajemen Pengguna**: Kelola akun pengguna dan hak akses sistem\n"
        "- **Manajemen Komponen**: Kelola data komponen produksi karoseri\n"
        "- **Klasifikasi Kerusakan**: Klasifikasi tingkat kerusakan (ringan, sedang, berat) menggunakan Naive Bayes\n"
        "- **Riwayat Prediksi**: Simpan dan pantau hasil klasifikasi\n"
        "### Timezone\n"
        "All timestamps are in Asia/Jakarta timezone (UTC+7).\n",
    version="1.0.0",
    lifespan=lifespan,
    swagger_ui_parameters={"persistAuthorization": True},
)

app.add_middleware(AuthMiddleware)

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff" # Stop MIME-type sniffing attack
    response.headers["X-Frame-Options"] = "DENY" # Prevent clickjacking attacks
    response.headers["X-XSS-Protection"] = "1; mode=block" # optional
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin" # Prevent leaking referrer information
    return response

@app.middleware("http")
async def add_response_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(round(process_time, 3))
    return response


app.add_middleware(CORSMiddleware, **CORS_CONFIG)
app.add_middleware(LoggingMiddleware)

app.include_router(router)
app.openapi = swagger_config(app)
