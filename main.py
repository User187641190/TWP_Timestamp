<<<<<<< HEAD
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid
from datetime import datetime

# Import ไฟล์ภายในโปรเจค
import models
import schemas
from database import SessionLocal, engine

# สร้าง Tables ใน Database (ถ้ารันครั้งแรก)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Delivery Management API")

# Dependency สำหรับเชื่อมต่อ DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ==========================================
# 1. Management APIs (Employee / Vehicle / Product)
# ==========================================

@app.get("/")
def Nothing():
    return ('Nothing , everything is nothing')

# --- Employee ---
@app.post("/employees/", response_model=schemas.Employee)
def create_employee(employee: schemas.EmployeeCreate, db: Session = Depends(get_db)):
    db_employee = models.Employee(**employee.model_dump())
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee

@app.get("/employees/", response_model=List[schemas.Employee])
def read_employees(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Employee).offset(skip).limit(limit).all()

# --- Vehicle ---
@app.post("/vehicles/", response_model=schemas.Vehicle)
def create_vehicle(vehicle: schemas.VehicleCreate, db: Session = Depends(get_db)):
    db_vehicle = models.Vehicle(**vehicle.model_dump())
    db.add(db_vehicle)
    db.commit()
    db.refresh(db_vehicle)
    return db_vehicle

@app.get("/vehicles/", response_model=List[schemas.Vehicle])
def read_vehicles(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Vehicle).offset(skip).limit(limit).all()

# --- Product (จำเป็นต้องมีเพื่อเอาไปใส่ใน Bill Item) ---
@app.post("/products/", response_model=schemas.Product)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    db_product = models.Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@app.get("/products/", response_model=List[schemas.Product])
def read_products(db: Session = Depends(get_db)):
    return db.query(models.Product).all()

# ==========================================
# 2. Delivery Bill APIs (พระเอกของเรา)
# ==========================================

@app.post("/delivery-bills/", response_model=schemas.DeliveryBill)
def create_delivery_bill(bill: schemas.DeliveryBillCreate, db: Session = Depends(get_db)):
        # 1. สร้างตัวบิลหลัก
    # ใช้ exclude={'items'} เพราะเราจะแยกสร้าง item ต่างหาก
    bill_data = bill.model_dump(exclude={'items'})
    db_bill = models.DeliveryBill(**bill_data)
    
    db.add(db_bill)
    db.commit() # Commit เพื่อให้ได้ Bill ID ใน DB ก่อน (กรณี Auto Increment) แต่เคสนี้เราระบุ ID เองก็ไม่เป็นไร

    # 2. สร้างรายการสินค้า (Bill Items) ถ้ามีส่งมาด้วย
    if bill.items:
        for item in bill.items:
            new_item = models.BillItem(
                # ใช้ Product_id และ Quantity ที่ส่งมา
                Product_Product_id=item.Product_Product_id,
                Quantity=item.Quantity,
                # ผูกกับบิลที่เพิ่งสร้าง
                Delivery_bill_bill_id=db_bill.bill_id 
            )
            db.add(new_item)
        db.commit()

    db.refresh(db_bill)
    return db_bill

@app.get("/delivery-bills/", response_model=List[schemas.DeliveryBill])
def read_delivery_bills(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    # ดึงข้อมูลทั้งหมด (Employee เห็นทุกบิลตามที่ขอ)
    bills = db.query(models.DeliveryBill).offset(skip).limit(limit).all()
    return bills

@app.get("/delivery-bills/{bill_id}", response_model=schemas.DeliveryBill)
def read_delivery_bill_by_id(bill_id: str, db: Session = Depends(get_db)):
    bill = db.query(models.DeliveryBill).filter(models.DeliveryBill.bill_id == bill_id).first()
    if bill is None:
        raise HTTPException(status_code=404, detail="Bill not found")
    return bill

@app.put("/delivery-bills/{bill_id}", response_model=schemas.DeliveryBill)
def update_delivery_bill(bill_id: str, bill_update: schemas.DeliveryBillUpdate, db: Session = Depends(get_db)):
    # 1. หาบิลก่อน
    db_bill = db.query(models.DeliveryBill).filter(models.DeliveryBill.bill_id == bill_id).first()
    if not db_bill:
        raise HTTPException(status_code=404, detail="Bill not found")

    # 2. อัปเดตข้อมูลเฉพาะ field ที่ส่งมา (ไม่เป็น None)
    update_data = bill_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_bill, key, value)

    db.add(db_bill)
    db.commit()
    db.refresh(db_bill)
    return db_bill

# ==========================================
# 3. Time Log & Actions
# ==========================================

@app.post("/time-logs/", response_model=schemas.DeliveryTimeLog)
def add_time_log(log_data: schemas.DeliveryTimeLogCreate, db: Session = Depends(get_db)):
    """
    Employee คนไหนก็สามารถยิง API นี้เพื่อลงเวลาให้บิลไหนก็ได้
    """
    # 1. เช็คว่าบิลมีจริงไหม
    bill = db.query(models.DeliveryBill).filter(models.DeliveryBill.bill_id == log_data.bill_id).first()
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")

    # 2. สร้าง Time Log (Generate ID เอง)
    new_log = models.DeliveryTimeLog(
        Time_log_id=str(uuid.uuid4()), # สร้าง UUID string
        Event_time=log_data.Event_time,
        Timestamp=datetime.now(), # เวลาปัจจุบันของ Server
        Remark=log_data.Remark,
        Delivery_bill_bill_id=log_data.bill_id
    )
    
    db.add(new_log)
    db.commit()
    db.refresh(new_log)
    
    return new_log

# Endpoint แถม: สำหรับเคลียร์ข้อมูล (ใช้ตอน Test)
# ระวัง! ห้ามเปิดใช้บน Production
@app.delete("/debug/clear-all")
def clear_database(db: Session = Depends(get_db)):
    try:
        db.query(models.DeliveryTimeLog).delete()
        db.query(models.BillItem).delete()
        db.query(models.DeliveryBill).delete()
        # ลบ Master data ทีหลังถ้าจำเป็น
        # db.query(models.Employee).delete()
        # db.query(models.Vehicle).delete()
        db.commit()
        return {"message": "All transaction data cleared"}
    except Exception as e:
        db.rollback()
=======
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid
from datetime import datetime

# Import ไฟล์ภายในโปรเจค
import models
import schemas
from database import SessionLocal, engine

# สร้าง Tables ใน Database (ถ้ารันครั้งแรก)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Delivery Management API")

# Dependency สำหรับเชื่อมต่อ DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ==========================================
# 1. Management APIs (Employee / Vehicle / Product)
# ==========================================

@app.get("/")
def Nothing():
    return ('Nothing , everything is nothing')

# --- Employee ---
@app.post("/employees/", response_model=schemas.Employee)
def create_employee(employee: schemas.EmployeeCreate, db: Session = Depends(get_db)):
    db_employee = models.Employee(**employee.model_dump())
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee

@app.get("/employees/", response_model=List[schemas.Employee])
def read_employees(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Employee).offset(skip).limit(limit).all()

# --- Vehicle ---
@app.post("/vehicles/", response_model=schemas.Vehicle)
def create_vehicle(vehicle: schemas.VehicleCreate, db: Session = Depends(get_db)):
    db_vehicle = models.Vehicle(**vehicle.model_dump())
    db.add(db_vehicle)
    db.commit()
    db.refresh(db_vehicle)
    return db_vehicle

@app.get("/vehicles/", response_model=List[schemas.Vehicle])
def read_vehicles(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Vehicle).offset(skip).limit(limit).all()

# --- Product (จำเป็นต้องมีเพื่อเอาไปใส่ใน Bill Item) ---
@app.post("/products/", response_model=schemas.Product)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    db_product = models.Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@app.get("/products/", response_model=List[schemas.Product])
def read_products(db: Session = Depends(get_db)):
    return db.query(models.Product).all()

# ==========================================
# 2. Delivery Bill APIs (พระเอกของเรา)
# ==========================================

@app.post("/delivery-bills/", response_model=schemas.DeliveryBill)
def create_delivery_bill(bill: schemas.DeliveryBillCreate, db: Session = Depends(get_db)):
    # 1. สร้างตัวบิลหลัก
    # ใช้ exclude={'items'} เพราะเราจะแยกสร้าง item ต่างหาก
    bill_data = bill.model_dump(exclude={'items'}) 
    db_bill = models.DeliveryBill(**bill_data)
    
    db.add(db_bill)
    db.commit() # Commit เพื่อให้ได้ Bill ID ใน DB ก่อน (กรณี Auto Increment) แต่เคสนี้เราระบุ ID เองก็ไม่เป็นไร

    # 2. สร้างรายการสินค้า (Bill Items) ถ้ามีส่งมาด้วย
    if bill.items:
        for item in bill.items:
            new_item = models.BillItem(
                # ใช้ Product_id และ Quantity ที่ส่งมา
                Product_Product_id=item.Product_Product_id,
                Quantity=item.Quantity,
                # ผูกกับบิลที่เพิ่งสร้าง
                Delivery_bill_bill_id=db_bill.bill_id 
            )
            db.add(new_item)
        db.commit()

    db.refresh(db_bill)
    return db_bill

@app.get("/delivery-bills/", response_model=List[schemas.DeliveryBill])
def read_delivery_bills(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    # ดึงข้อมูลทั้งหมด (Employee เห็นทุกบิลตามที่ขอ)
    bills = db.query(models.DeliveryBill).offset(skip).limit(limit).all()
    return bills

@app.get("/delivery-bills/{bill_id}", response_model=schemas.DeliveryBill)
def read_delivery_bill_by_id(bill_id: str, db: Session = Depends(get_db)):
    bill = db.query(models.DeliveryBill).filter(models.DeliveryBill.bill_id == bill_id).first()
    if bill is None:
        raise HTTPException(status_code=404, detail="Bill not found")
    return bill

@app.put("/delivery-bills/{bill_id}", response_model=schemas.DeliveryBill)
def update_delivery_bill(bill_id: str, bill_update: schemas.DeliveryBillUpdate, db: Session = Depends(get_db)):
    # 1. หาบิลก่อน
    db_bill = db.query(models.DeliveryBill).filter(models.DeliveryBill.bill_id == bill_id).first()
    if not db_bill:
        raise HTTPException(status_code=404, detail="Bill not found")

    # 2. อัปเดตข้อมูลเฉพาะ field ที่ส่งมา (ไม่เป็น None)
    update_data = bill_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_bill, key, value)

    db.add(db_bill)
    db.commit()
    db.refresh(db_bill)
    return db_bill

# ==========================================
# 3. Time Log & Actions
# ==========================================

@app.post("/time-logs/", response_model=schemas.DeliveryTimeLog)
def add_time_log(log_data: schemas.DeliveryTimeLogCreate, db: Session = Depends(get_db)):
    """
    Employee คนไหนก็สามารถยิง API นี้เพื่อลงเวลาให้บิลไหนก็ได้
    """
    # 1. เช็คว่าบิลมีจริงไหม
    bill = db.query(models.DeliveryBill).filter(models.DeliveryBill.bill_id == log_data.bill_id).first()
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")

    # 2. สร้าง Time Log (Generate ID เอง)
    new_log = models.DeliveryTimeLog(
        Time_log_id=str(uuid.uuid4()), # สร้าง UUID string
        Event_time=log_data.Event_time,
        Timestamp=datetime.now(), # เวลาปัจจุบันของ Server
        Remark=log_data.Remark,
        Delivery_bill_bill_id=log_data.bill_id
    )
    
    db.add(new_log)
    db.commit()
    db.refresh(new_log)
    
    return new_log

# Endpoint แถม: สำหรับเคลียร์ข้อมูล (ใช้ตอน Test)
# ระวัง! ห้ามเปิดใช้บน Production
@app.delete("/debug/clear-all")
def clear_database(db: Session = Depends(get_db)):
    try:
        db.query(models.DeliveryTimeLog).delete()
        db.query(models.BillItem).delete()
        db.query(models.DeliveryBill).delete()
        # ลบ Master data ทีหลังถ้าจำเป็น
        # db.query(models.Employee).delete()
        # db.query(models.Vehicle).delete()
        db.commit()
        return {"message": "All transaction data cleared"}
    except Exception as e:
        db.rollback()
>>>>>>> 6a00c194b3ca065d66c637d236f80dea39dd3e2c
        return {"error": str(e)}