from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from sqlalchemy.exc import SQLAlchemyError

from app.database import init_db
from app.routers import router

load_dotenv()

app = FastAPI(title="Customer Support CRM", version="1.0.0")
BASE_DIR = Path(__file__).resolve().parent

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
app.include_router(router)


@app.on_event("startup")
def startup_event():
    try:
        init_db()
    except SQLAlchemyError:
        print("Database startup failed. The app will continue in a limited mode.")
