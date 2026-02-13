#<<<<<<< HEAD
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# URL สำหรับเชื่อมต่อ Database
# ถ้าใช้ SQLite (ไฟล์อยู่ในเครื่อง) ให้ใช้บรรทัดล่างนี้:
SQLALCHEMY_DATABASE_URL = "oracle+oracledb://Backend:BackendPass@localhost:1521/?service_name=FREEPDB1"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL # check_same_thread ใช้เฉพาะกับ SQLite
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()