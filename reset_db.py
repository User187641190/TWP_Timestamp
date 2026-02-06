<<<<<<< HEAD
from database import engine
from models import Base
from sqlalchemy import text

def reset_database():
    print("🚀 Starting Database Reset...")
    
    # 1. เชื่อมต่อและสั่ง Drop แบบ Force
    with engine.connect() as connection:
        try:
            # ปิด Foreign Key Check ชั่วคราว (เฉพาะ Oracle บางเวอร์ชั่นช่วยได้)
            # connection.execute(text("ALTER SESSION SET CONSTRAINTS = DEFERRED"))
            pass 
        except Exception as e:
            print(f"⚠️ Warning during setup: {e}")

    # 2. ใช้ SQLAlchemy สั่งลบทุก Table ที่อยู่ใน Models
    print("🗑️ Dropping all tables...")
    try:
        Base.metadata.drop_all(bind=engine)
        print("✅ Tables dropped.")
    except Exception as e:
        print(f"❌ Error dropping tables: {e}")

    # 3. สร้างใหม่
    print("🏗️ Creating all tables...")
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Tables created successfully!")
    except Exception as e:
        print(f"❌ Error creating tables: {e}")

if __name__ == "__main__":
=======
from database import engine
from models import Base
from sqlalchemy import text

def reset_database():
    print("🚀 Starting Database Reset...")
    
    # 1. เชื่อมต่อและสั่ง Drop แบบ Force
    with engine.connect() as connection:
        try:
            # ปิด Foreign Key Check ชั่วคราว (เฉพาะ Oracle บางเวอร์ชั่นช่วยได้)
            # connection.execute(text("ALTER SESSION SET CONSTRAINTS = DEFERRED"))
            pass 
        except Exception as e:
            print(f"⚠️ Warning during setup: {e}")

    # 2. ใช้ SQLAlchemy สั่งลบทุก Table ที่อยู่ใน Models
    print("🗑️ Dropping all tables...")
    try:
        Base.metadata.drop_all(bind=engine)
        print("✅ Tables dropped.")
    except Exception as e:
        print(f"❌ Error dropping tables: {e}")

    # 3. สร้างใหม่
    print("🏗️ Creating all tables...")
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Tables created successfully!")
    except Exception as e:
        print(f"❌ Error creating tables: {e}")

if __name__ == "__main__":
>>>>>>> 6a00c194b3ca065d66c637d236f80dea39dd3e2c
    reset_database()