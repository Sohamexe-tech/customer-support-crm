import os
from urllib.parse import quote_plus

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "customer_support_crm")

Base = declarative_base()


def build_database_url(database_name=None):
    username = quote_plus(DB_USER)
    password = quote_plus(DB_PASSWORD)
    database = quote_plus(database_name or DB_NAME)
    return f"mysql+pymysql://{username}:{password}@{DB_HOST}:{DB_PORT}/{database}"


engine = create_engine(build_database_url(), pool_pre_ping=True, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    try:
        admin_engine = create_engine(
            f"mysql+pymysql://{quote_plus(DB_USER)}:{quote_plus(DB_PASSWORD)}@{DB_HOST}:{DB_PORT}/",
            pool_pre_ping=True,
            echo=False,
        )
        with admin_engine.connect() as connection:
            connection.execute(text(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"))
    except OperationalError:
        print("MySQL connection failed. Update the database credentials in .env and ensure the MySQL server is running.")
        return False

    engine.dispose()
    globals()["engine"] = create_engine(build_database_url(), pool_pre_ping=True, echo=False)
    globals()["SessionLocal"] = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    return True
