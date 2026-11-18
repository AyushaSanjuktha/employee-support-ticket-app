from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base, SessionLocal
from .seed import seed_sample_data
from .routers import auth, tickets, comments


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create database tables and seed initial sample data on startup."""
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed_sample_data(db)
    yield


app = FastAPI(
    title="Employee Support Ticket App API",
    version="1.0.0",
    lifespan=lifespan
)

# Allow requests from local frontend (Vite default is localhost:5173 / localhost:3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(tickets.router)
app.include_router(comments.router)


@app.get("/api/health")
def health_check() -> dict:
    """Basic health check endpoint."""
    return {"status": "ok", "app": "Employee Support Ticket App"}
