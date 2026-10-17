from fastapi import FastAPI

from .routers import auth, protected

app = FastAPI(title="JWT Auth")
app.include_router(auth.router)
app.include_router(protected.router)
