<<<<<<< HEAD
import sys
from sqlalchemy import create_engine, text

# ลอง Connection String ที่เราแก้ล่าสุด
# ตรวจสอบ User/Pass/ServiceName ให้ตรงเป๊ะๆ
DATABASE_URL = "oracle+oracledb://Backend:BackendPass@localhost:1521/?service_name=FREEPDB1"
def Test_db():
    try:
        print(f"🔄 Attempting to connect to: {DATABASE_URL}")
        engine = create_engine(DATABASE_URL)
        
        # ลองเชื่อมต่อจริง
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 'Hello Oracle' FROM DUAL"))
            print(f"✅ Success! Database says: {result.scalar()}")
            
    except Exception as e:
        print("\n❌ Connection Failed!")
        print(f"Error Type: {type(e).__name__}")
=======
import sys
from sqlalchemy import create_engine, text

# ลอง Connection String ที่เราแก้ล่าสุด
# ตรวจสอบ User/Pass/ServiceName ให้ตรงเป๊ะๆ
DATABASE_URL = "oracle+oracledb://Backend:BackendPass@localhost:1521/?service_name=FREEPDB1"
def Test_db():
    try:
        print(f"🔄 Attempting to connect to: {DATABASE_URL}")
        engine = create_engine(DATABASE_URL)
        
        # ลองเชื่อมต่อจริง
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 'Hello Oracle' FROM DUAL"))
            print(f"✅ Success! Database says: {result.scalar()}")
            
    except Exception as e:
        print("\n❌ Connection Failed!")
        print(f"Error Type: {type(e).__name__}")
>>>>>>> 6a00c194b3ca065d66c637d236f80dea39dd3e2c
        print(f"Error Details: {e}")