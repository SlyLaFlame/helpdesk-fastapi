import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine
from .routers import auth, tickets, users

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="ICT Helpdesk API",
    description="IT support ticket tracking, modeled on a real institutional ICT department workflow.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:5173").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(tickets.router)


@app.get("/", tags=["health"])
def health():
    return {"status": "ok", "docs": "/docs"}
