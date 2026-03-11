import sys
from sqlalchemy import create_engine, text

DATABASE_URL = "mysql+pymysql://root:12345678@localhost:3306/delivery_db"
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
        print(f"Error Details: {e}")

Test_db()