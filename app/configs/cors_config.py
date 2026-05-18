import os
from dotenv import load_dotenv

load_dotenv()

origins_str = os.getenv("CORS_ORIGINS", "")
CORS_ORIGINS = [o.strip() for o in origins_str.split(",") if o.strip()]
if not CORS_ORIGINS:
    CORS_ORIGINS = ["http://localhost:5173"]

CORS_CONFIG = {
    "allow_origins": CORS_ORIGINS,
    "allow_credentials": True,
    "allow_methods": ["*"],
    "allow_headers": ["*"],
}