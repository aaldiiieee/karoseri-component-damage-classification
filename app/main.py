from fastapi import FastAPI
from .routers import router

app = FastAPI(title="Final Project UNPAM")

app.include_router(router)