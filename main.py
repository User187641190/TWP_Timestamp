from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware

import models
import schemas
from database import engine, get_db

# สั่งให้สร้างตารางใน Database อัตโนมัติ
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="WMS System API (Refactored)")

# CORS ตั้งค่าให้หน้าบ้านเรียก API ได้
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


from sqlalchemy import text
from fastapi import HTTPException

# API ดึงข้อมูลจาก View (Dynamic Endpoint)
@app.get("/api/views/{view_name}")
def get_view_data(view_name: str, db: Session = Depends(get_db)):
    # ป้องกัน SQL Injection โดยเช็คว่าชื่อ View อยู่ในรายการที่อนุญาตหรือไม่
    allowed_views = [
        "vw_user_roles_details", "vw_warehouse_inventory_value",
        "vw_delivery_bill_info", "vw_bill_total_value",
        "vw_employee_delivery_stats", "vw_latest_delivery_status",
        "vw_vehicle_usage_summary", "vw_customer_order_summary",
        "vw_low_stock_products", "vw_master_delivery_dashboard"
    ]
    
    if view_name not in allowed_views:
        raise HTTPException(status_code=400, detail="ไม่พบ View ที่ต้องการ")
    
    # รัน SQL ดึงข้อมูลจาก View
    query = text(f"SELECT * FROM {view_name}")
    result = db.execute(query).mappings().all()
    
    return result

@app.get("/")
def read_root():
    return {"message": "✅ API is running with the new schema!"}

# --- 1. Roles ---
@app.get("/roles", response_model=list[schemas.RoleResponse])
def get_roles(db: Session = Depends(get_db)):
    return db.query(models.Role).all()

@app.post("/roles", response_model=schemas.RoleResponse)
def create_role(role: schemas.RoleCreate, db: Session = Depends(get_db)):
    db_role = models.Role(**role.dict())
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role

# --- 2. Employees ---
@app.get("/employees", response_model=list[schemas.EmployeeResponse])
def get_employees(db: Session = Depends(get_db)):
    return db.query(models.Employee).all()

@app.post("/employees", response_model=schemas.EmployeeResponse)
def create_employee(emp: schemas.EmployeeCreate, db: Session = Depends(get_db)):
    db_emp = models.Employee(**emp.dict())
    db.add(db_emp)
    db.commit()
    db.refresh(db_emp)
    return db_emp

# --- 3. Customers ---
@app.get("/customers", response_model=list[schemas.CustomerResponse])
def get_customers(db: Session = Depends(get_db)):
    return db.query(models.Customer).all()

@app.post("/customers", response_model=schemas.CustomerResponse)
def create_customer(customer: schemas.CustomerCreate, db: Session = Depends(get_db)):
    db_customer = models.Customer(**customer.dict())
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer

# --- 4. Vehicles ---
@app.get("/vehicles", response_model=list[schemas.VehicleResponse])
def get_vehicles(db: Session = Depends(get_db)):
    return db.query(models.Vehicle).all()

@app.post("/vehicles", response_model=schemas.VehicleResponse)
def create_vehicle(vehicle: schemas.VehicleCreate, db: Session = Depends(get_db)):
    db_vehicle = models.Vehicle(**vehicle.dict())
    db.add(db_vehicle)
    db.commit()
    db.refresh(db_vehicle)
    return db_vehicle

# --- 5. Warehouses ---
@app.get("/warehouses", response_model=list[schemas.WarehouseResponse])
def get_warehouses(db: Session = Depends(get_db)):
    return db.query(models.Warehouse).all()

@app.post("/warehouses", response_model=schemas.WarehouseResponse)
def create_warehouse(warehouse: schemas.WarehouseCreate, db: Session = Depends(get_db)):
    db_warehouse = models.Warehouse(**warehouse.dict())
    db.add(db_warehouse)
    db.commit()
    db.refresh(db_warehouse)
    return db_warehouse

# --- 6. Products ---
@app.get("/products", response_model=list[schemas.ProductResponse])
def get_products(db: Session = Depends(get_db)):
    return db.query(models.Product).all()

@app.post("/products", response_model=schemas.ProductResponse)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    db_product = models.Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

# --- 7. Users ---
@app.get("/users", response_model=list[schemas.UserResponse])
def get_users(db: Session = Depends(get_db)):
    return db.query(models.User).all()

@app.post("/users", response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # 💡 หมายเหตุ: ระบบจริงควรนำ user.password ไปเข้ารหัส (Hash) ก่อนบันทึกลง password_hash
    db_user = models.User(
        username=user.username,
        password_hash=user.password, # เก็บชั่วคราวแบบไม่เข้ารหัสไปก่อน
        role_id=user.role_id,
        employee_id=user.employee_id
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# --- 8. Delivery Bills ---
@app.get("/delivery-bills", response_model=list[schemas.DeliveryBillResponse])
def get_delivery_bills(db: Session = Depends(get_db)):
    return db.query(models.DeliveryBill).all()

@app.post("/delivery-bills", response_model=schemas.DeliveryBillResponse)
def create_delivery_bill(bill: schemas.DeliveryBillCreate, db: Session = Depends(get_db)):
    db_bill = models.DeliveryBill(**bill.dict())
    db.add(db_bill)
    db.commit()
    db.refresh(db_bill)
    return db_bill

# --- 9. Delivery Items ---
@app.get("/delivery-items", response_model=list[schemas.DeliveryItemResponse])
def get_delivery_items(db: Session = Depends(get_db)):
    return db.query(models.DeliveryItem).all()

@app.post("/delivery-items", response_model=schemas.DeliveryItemResponse)
def create_delivery_item(item: schemas.DeliveryItemCreate, db: Session = Depends(get_db)):
    db_item = models.DeliveryItem(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

# --- 10. Delivery Logs ---
@app.get("/delivery-logs", response_model=list[schemas.DeliveryLogResponse])
def get_delivery_logs(db: Session = Depends(get_db)):
    return db.query(models.DeliveryLog).all()

@app.post("/delivery-logs", response_model=schemas.DeliveryLogResponse)
def create_delivery_log(log: schemas.DeliveryLogCreate, db: Session = Depends(get_db)):
    db_log = models.DeliveryLog(**log.dict())
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log