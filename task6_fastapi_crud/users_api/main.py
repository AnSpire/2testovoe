from fastapi import FastAPI

from .routers import users

app = FastAPI(title="Users CRUD")
app.include_router(users.router)
