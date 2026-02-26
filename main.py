from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid
from datetime import datetime
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from jose import jwt
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz

# เพิ่มไว้ใน main.py


# Import ไฟล์ภายในโปรเจค
import models
from models import User
import schemas
from database import SessionLocal, engine
from deps import get_current_user, check_ceo_role , check_employee_role , check_admin_role
import deps 
from schemas import UserShow
from deps import SECRET_KEY, ALGORITHM



def reset_daily_employee_status():
    """
    ฟังก์ชันนี้จะทำงานทุก 7.00 น.
    เพื่อรีเซ็ตสถานะพนักงานทุกคน (เช่น ให้กลับมาเป็น Active เพื่อรอเช็คชื่อใหม่)
    """
    print(f"⏰ [7:00 AM] เริ่มทำการรีเซ็ตสถานะพนักงาน... ({datetime.now()})")
    
    # ต้องสร้าง DB Session เองเพราะไม่ได้ผ่าน API Request
    db = SessionLocal() 
    try:
        # ดึงพนักงานทุกคนมา
        employees = db.query(models.Employee).all()
        for emp in employees:
            # ตัวอย่าง: รีเซ็ตสถานะเป็น "Active" (หรือสถานะอื่นตามต้องการ เช่น "Wait Check-in")
            emp.Status = models.EmployeeStatus.ACTIVE 
            
        db.commit()
        print("✅ รีเซ็ตสถานะพนักงานเรียบร้อยแล้ว")
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการรีเซ็ต: {e}")
        db.rollback()
    finally:
        db.close()

# --- ตั้งค่า Scheduler (วางไว้ก่อน app = FastAPI...) ---
scheduler = BackgroundScheduler()
# ตั้งเวลา 7:00 น. ทุกวัน (timezone Bangkok/Asia)
trigger = CronTrigger(hour=7, minute=0, timezone=pytz.timezone('Asia/Bangkok'))
scheduler.add_job(reset_daily_employee_status, trigger)
scheduler.start()


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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # หรือระบุเป็น ["http://127.0.0.1:5500"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def Nothing():
    return ('Nothing , everything is nothing')



#        _  _     _  _         _____     ____     _____   _______ 
#      _| || |_ _| || |_      |  __ \   / __ \   / ____| |__   __|
#     |_  __  _|_  __  _|     | |__) | | |  | | | (___      | |   
#      _| || |_ _| || |_      |  ___/  | |  | |  \___ \     | |   
#     |_  __  _|_  __  _|     | |      | |__| |  ____) |    | |   
#       |_||_|   |_||_|       |_|       \____/  |_____/     |_|   
#                                                                 
#                                                                 
@app.post("/employees", response_model=schemas.Employee)
def create_employee(emp: schemas.EmployeeCreate, db: Session = Depends(get_db), current_user = Depends(check_admin_role)):
    new_emp = models.Employee(
        Employee_name=emp.Employee_name,
        Phone=emp.Phone,
        Status=emp.Status
    )
    db.add(new_emp)
    db.commit()
    db.refresh(new_emp)
    return new_emp

@app.post("/vehicles", response_model=schemas.Vehicle)
def create_vehicle(veh: schemas.VehicleCreate, db: Session = Depends(get_db), current_user = Depends(check_admin_role)):
    new_veh = models.Vehicle(
        License_plate=veh.License_plate,
        Status=veh.Status
    )
    db.add(new_veh)
    db.commit()
    db.refresh(new_veh)
    return new_veh


@app.post("/products/", response_model=schemas.Product)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db) , current_user = Depends(check_ceo_role)):
    db_product = models.Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


@app.put("/delivery-bills/{bill_id}/status")
def update_bill_status(bill_id: int, status_update: schemas.DeliveryBillUpdateStatus, db: Session = Depends(get_db), current_user = Depends(check_employee_role)):
    bill = db.query(models.DeliveryBill).filter(models.DeliveryBill.Bill_id == bill_id).first()
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")
    
    bill.status = status_update.status
    # ถ้าส่งเสร็จ ให้ลงเวลาจบ
    if status_update.status == models.DeliveryBillStatus.DELIVERED:
        bill.finish_time = datetime.now()
        
    db.commit()
    db.refresh(bill)
    return bill

@app.post("/delivery-bills/", response_model=schemas.DeliveryBill)
def create_delivery_bill(bill: schemas.DeliveryBillCreate, db: Session = Depends(get_db) , current_user = Depends(check_employee_role)):
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


@app.post("/time-logs/", response_model=schemas.DeliveryTimeLog)
def add_time_log(log_data: schemas.DeliveryTimeLogCreate, db: Session = Depends(get_db) , current_user = Depends(check_employee_role)):
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


@app.post("/roles/", response_model=schemas.Role)
def create_role(role: schemas.RoleCreate, db: Session = Depends(get_db) , current_user = Depends(check_admin_role)):
    # เช็คว่ามี ID นี้หรือยัง
    db_role = db.query(models.Role).filter(models.Role.role_id == role.role_id).first()
    if db_role:
        raise HTTPException(status_code=400, detail="Role ID already exists")
    
    # สร้าง Role ใหม่
    new_role = models.Role(
        role_id=role.role_id,
        role_name=role.role_name,
        description=role.description
    )
    db.add(new_role)
    db.commit()
    db.refresh(new_role)
    return new_role


@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db), current_user = Depends(check_admin_role)):
    db_user = db.query(models.User).filter(models.User.User_id == user.User_id).first()
    if db_user:
        raise HTTPException(status_code=400, detail="User ID already exists")
    
    db_emp = db.query(models.Employee).filter(models.Employee.Employee_id == user.Employee_id).first()
    if not db_emp:
        raise HTTPException(status_code=404, detail="Employee ID not found (Must create Employee first)")
    
    db_role = db.query(models.Role).filter(models.Role.role_id == user.Role_role_id).first()
    if not db_role:
        raise HTTPException(status_code=404, detail="Role ID not found (Must create Role first)")
    
    new_user = models.User(
        User_id=user.User_id,
        Username=user.Username,
        Password_hash=user.Password_hash,
        status=user.status,
        Employee_Employee_id=user.Employee_id, 
        Role_role_id=user.Role_role_id
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


# main.py

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # 1. เช็ค User / Password
    # หมายเหตุ: ในระบบจริงควรเช็ค Password Hash แต่ตอนนี้เช็คแบบดิบๆ ไปก่อน
    user = db.query(models.User).filter(models.User.Username == form_data.username).first()

    if not user: # ถ้าไม่เจอ User
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    # (ถ้ามีเช็ค password ให้ใส่ตรงนี้)
    if user.Password_hash != form_data.password:
        raise HTTPException(status_code=400, detail="รหัสผ่านไม่ถูกต้อง")

    # 2. สร้าง JWT Token (นี่คือส่วนสำคัญที่หายไป!)
    data_to_encode = {
        "sub": user.Username,  # sub คือ Subject (เจ้าของ Token)
        "role": str(user.Role_role_id) # ใส่ Role ไปด้วยก็ได้
    }
    # สร้าง Token โดยใช้กุญแจเดียวกับใน deps.py
    encoded_jwt = jwt.encode(data_to_encode, SECRET_KEY, algorithm=ALGORITHM)

    # 3. ส่ง Token กลับไปให้ Frontend
    return {
        "access_token": encoded_jwt, 
        "token_type": "bearer",
        "role": str(user.Role_role_id) # ส่ง Role แยกไปให้ใช้ง่ายๆ
    }

#        _  _     _  _          _____   ______   _______ 
#      _| || |_ _| || |_       / ____| |  ____| |__   __|
#     |_  __  _|_  __  _|     | |  __  | |__       | |   
#      _| || |_ _| || |_      | | |_ | |  __|      | |   
#     |_  __  _|_  __  _|     | |__| | | |____     | |   
#       |_||_|   |_||_|        \_____| |______|    |_|   
#                                                        
#                                                        

@app.get("/employees/", response_model=List[schemas.Employee])
def read_employees(skip: int = 0, limit: int = 100, db: Session = Depends(get_db) , current_user = Depends(get_current_user)):
    return db.query(models.Employee).offset(skip).limit(limit).all()


@app.get("/vehicles/", response_model=List[schemas.Vehicle])
def read_vehicles(skip: int = 0, limit: int = 100, db: Session = Depends(get_db) , current_user = Depends(get_current_user)):
    return db.query(models.Vehicle).offset(skip).limit(limit).all()


@app.get("/products/", response_model=List[schemas.Product])
def read_products(db: Session = Depends(get_db)):
    return db.query(models.Product).all()


@app.get("/delivery-bills/", response_model=List[schemas.DeliveryBill])
def read_delivery_bills(skip: int = 0, limit: int = 100, db: Session = Depends(get_db) , current_user = Depends(check_employee_role)):
    # ดึงข้อมูลทั้งหมด (Employee เห็นทุกบิลตามที่ขอ)
    bills = db.query(models.DeliveryBill).offset(skip).limit(limit).all()
    return bills


@app.get("/delivery-bills/{bill_id}", response_model=schemas.DeliveryBill)
def read_delivery_bill_by_id(bill_id: str, db: Session = Depends(get_db) , current_user = Depends(check_employee_role)):
    bill = db.query(models.DeliveryBill).filter(models.DeliveryBill.bill_id == bill_id).first()
    if bill is None:
        raise HTTPException(status_code=404, detail="Bill not found")
    return bill


@app.get("/roles/", response_model=list[schemas.Role])
def read_roles(skip: int = 0, limit: int = 100, db: Session = Depends(get_db) , current_user = Depends(check_admin_role)):
    roles = db.query(models.Role).offset(skip).limit(limit).all()
    return roles


@app.get("/users/", response_model=list[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db) , current_user = Depends(check_admin_role)):
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users

@app.get("/users/me")  # ลบ response_model=UserShow ออกชั่วคราว เพื่อความยืดหยุ่น
async def read_users_me(current_user: models.User = Depends(get_current_user)):
    # 1. แปลง Role ID เป็นชื่อ (Mapping)
    # เช็คตาม Database ของคุณว่าเลขไหนคือตำแหน่งอะไร
    role_name = "User"
    if current_user.Role_role_id == 1:
        role_name = "Admin"   # ต้องตรงกับที่ JS เช็ค (ตัวเล็ก/ใหญ่สำคัญ)
    elif current_user.Role_role_id == 2:
        role_name = "Staff"   # หรือ Employee
    elif current_user.Role_role_id == 3:
        role_name = "Driver"

    # 2. ส่ง JSON กลับไปแบบ Manual (เพื่อให้ได้ field "role" ที่หน้าเว็บต้องการ)
    return {
        "User_id": current_user.User_id,
        "username": current_user.Username,
        "role": role_name,           # <--- นี่คือตัวที่หน้าเว็บรออยู่!
        "role_id": current_user.Role_role_id,
        "status": current_user.status
    }

@app.get("/dashboard/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    # นับจำนวนรถตามสถานะ
    vehicles = db.query(models.Vehicle).all()
    v_stats = {"Available": 0, "In Use": 0, "Maintenance": 0}
    for v in vehicles:
        # แปลง enum เป็น string เพื่อความชัวร์
        status_str = str(v.Status.value) if hasattr(v.Status, 'value') else str(v.Status)
        if status_str in v_stats:
            v_stats[status_str] += 1

    # นับจำนวนพนักงานตามสถานะ
    employees = db.query(models.Employee).all()
    e_stats = {"Active": 0, "On Leave": 0, "Holiday": 0}
    for e in employees:
        status_str = str(e.Status.value) if hasattr(e.Status, 'value') else str(e.Status)
        if status_str in e_stats:
            e_stats[status_str] += 1
            
    return {"vehicles": v_stats, "employees": e_stats}

#        _  _     _  _         _____    _    _   _______ 
#      _| || |_ _| || |_      |  __ \  | |  | | |__   __|
#     |_  __  _|_  __  _|     | |__) | | |  | |    | |   
#      _| || |_ _| || |_      |  ___/  | |  | |    | |   
#     |_  __  _|_  __  _|     | |      | |__| |    | |   
#       |_||_|   |_||_|       |_|       \____/     |_|   
#                                                        
#                                                        


@app.put("/delivery-bills/{bill_id}", response_model=schemas.DeliveryBill)
def update_delivery_bill(bill_id: str, bill_update: schemas.DeliveryBillUpdate, db: Session = Depends(get_db) , current_user = Depends(check_employee_role)):
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



#        _  _     _  _         _____    ______   _        ______   _______   ______ 
#      _| || |_ _| || |_      |  __ \  |  ____| | |      |  ____| |__   __| |  ____|
#     |_  __  _|_  __  _|     | |  | | | |__    | |      | |__       | |    | |__   
#      _| || |_ _| || |_      | |  | | |  __|   | |      |  __|      | |    |  __|  
#     |_  __  _|_  __  _|     | |__| | | |____  | |____  | |____     | |    | |____ 
#       |_||_|   |_||_|       |_____/  |______| |______| |______|    |_|    |______|
#                                                                                   
#                                                                                   


@app.delete("/debug/clear-all")
def clear_database(db: Session = Depends(get_db) , current_user = Depends(check_admin_role)):
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



