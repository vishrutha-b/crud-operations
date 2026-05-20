from fastapi import FastAPI,
from fastapi.middleware.cors import CORSMiddleware

from database import Base, engine
from routers import items

# Create all database tables automatically on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="CRUD API with PostgreSQL",
    description="A simple FastAPI backend for CRUD operations using PostgreSQL (pgAdmin).",
    version="1.0.0",
)

# CORS – allow all origins for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(items.router, prefix="/api/v1")


@app.get("/", tags=["Health"])
def health_check():
    """Root endpoint – confirms the API is running."""
    return {"status": "ok", "message": "CRUD API is running 🚀"}
