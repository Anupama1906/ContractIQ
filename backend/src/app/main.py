from fastapi import FastAPI
from app.api import contracts

app = FastAPI()

app.include_router(contracts.router, prefix="/contracts", tags=["Contracts"])