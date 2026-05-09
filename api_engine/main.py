"""
FastAPI application for the Plan Recommendation Engine
Common endpoints and functions structure
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel
from database import engine
from endpoints import router

# Create FastAPI app
app = FastAPI(
    title="Plan Recommendation Engine API",
    description="API for managing venues, areas, and creating personalized plans",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include common endpoints router
app.include_router(router)

# Startup event to create tables
@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
