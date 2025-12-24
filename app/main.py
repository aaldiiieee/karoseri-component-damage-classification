from fastapi import FastAPI
from .routers import router
from .configs.logging import setup_logging
from .configs.logging_middleware import LoggingMiddleware
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
    title="Karoseri Component Damage Classification",
    description = 
        "A Karoseri Component Damage Classification API for PT. Sukses Tunggal Mandiri using FastAPI \n"
        "### Features\n"
        "- **User Management System**: Manage user accounts, roles, and permissions\n"
        "### Timezone\n"
        "All timestamps are in Asia/Jakarta timezone (UTC+7).\n",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(LoggingMiddleware)

app.include_router(router)