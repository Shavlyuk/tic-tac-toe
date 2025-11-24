from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from src.db.database import create_tables
from src.api.endpoints import router as api_router

app = FastAPI(
    title="Tic-Tac-Toe API",
    description="A simple Tic-Tac-Toe game API with FastAPI and SQLite",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

@app.on_event("startup")
def startup_event():
    create_tables()

app.include_router(api_router, prefix="/api/v1", tags=["games"])

app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)