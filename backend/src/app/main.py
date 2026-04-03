from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware # Add this
from backend.src.app.api import contracts

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", # Common Vite/CRA port
        "http://localhost:3001", # The port in your snippet
        "http://localhost:5173", # Default Vite port
    ], # Your Vite frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(contracts.router, prefix="/contracts", tags=["Contracts"])