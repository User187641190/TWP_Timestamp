from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, date
# Import Enums จาก models.py (ต้องมีไฟล์ models.py ที่ประกาศ Enum ไว้แล้วนะ)
from models import EmployeeStatus, VehicleStatus, DeliveryBillStatus

# ==========================================
# 1. Base Schemas & Shared (พื้นฐาน)
# ==========================================

# --- User / Login System ---
class UserBase(BaseModel):
    Username: str
    Role: str  # เช่น 'Admin', 'Supervisor', 'CEO'

class UserCreate(UserBase):
    Password: str  # รับ Password เข้ามาตอนสร้าง

class User(UserBase):
    User_id: int
    # ไม่ return Password กลับไป
    class Config:
        from_attributes = True

# --- Product (สินค้า) ---
class ProductBase(BaseModel):
    Product_name: str
    Price: float

class ProductCreate(ProductBase):
    Product_id: str  # สมมติว่าเป็นรหัสสินค้า เช่น 'P-001'

class Product(ProductBase):
    Product_id: str
    class Config:
        from_attributes = True

# ==========================================
# 2. Helper Schemas for Nesting (ตัวช่วยแสดงผล)
# ==========================================
# ใช้สำหรับแสดงข้อมูลย่อในตารางอื่น เพื่อป้องกัน Loop ไม่จบสิ้น

class EmployeeShow(BaseModel):
    Employee_id: int
    Employee_name: str
    Status: EmployeeStatus
    class Config:
        from_attributes = True

class VehicleShow(BaseModel):
    Vehicle_id: int
    license_plate: str
    Vehicle_description: str
    Status: VehicleStatus
    class Config:
        from_attributes = True

class ProductShow(BaseModel):
    Product_id: str
    Product_name: str
    class Config:
        from_attributes = True

# ==========================================
# 3. Main Entity Schemas (ข้อมูลหลัก)
# ==========================================

# --- Employee ---
class EmployeeBase(BaseModel):
    Employee_name: str
    Phone: Optional[str] = None
    Status: EmployeeStatus = EmployeeStatus.ACTIVE

class EmployeeCreate(EmployeeBase):
    Employee_id: int # ระบุ ID เองตอนสร้าง

class Employee(EmployeeBase):
    Employee_id: int
    # ถ้าอยากให้ Employee โชว์รายการบิลของตัวเองด้วย ให้ uncomment บรรทัดล่าง
    # deliveries: List['DeliveryBillBase'] = [] 
    class Config:
        from_attributes = True

# --- Vehicle ---
class VehicleBase(BaseModel):
    license_plate: str
    Vehicle_description: str | None=None
    Status: VehicleStatus = VehicleStatus.AVAILABLE

class VehicleCreate(VehicleBase):
    Vehicle_id: int

class Vehicle(VehicleBase):
    Vehicle_id: int
    class Config:
        from_attributes = True

# ==========================================
# 4. Transaction Schemas (รายการย่อยในบิล)
# ==========================================

# --- Bill Item (รายการสินค้าในบิล) ---
class BillItemBase(BaseModel):
    Quantity: int
    Product_Product_id: str  # รับแค่ ID สินค้า

class BillItemCreate(BillItemBase):
    pass

class BillItem(BillItemBase):
    Bill_item_id: int
    product: Optional[ProductShow] = None # โชว์ชื่อสินค้าด้วย
    class Config:
        from_attributes = True

# --- Time Log (ประวัติเวลา) ---
class DeliveryTimeLogBase(BaseModel):
    Event_time: str      # เช่น "10:30"
    Remark: Optional[str] = None

class DeliveryTimeLogCreate(DeliveryTimeLogBase):
    bill_id: str # ต้องระบุว่าจะลงเวลาให้บิลไหน

class DeliveryTimeLog(DeliveryTimeLogBase):
    Time_log_id: str
    Timestamp: Optional[datetime]
    class Config:
        from_attributes = True

# ==========================================
# 5. Delivery Bill (พระเอกของเรา)
# ==========================================

# --- Base ---
class DeliveryBillBase(BaseModel):
    bill_id: str
    delivery_date: Optional[date] = None
    status: DeliveryBillStatus = DeliveryBillStatus.AWAIT
    
    # FK (รับมาเป็น ID ตอนสร้าง)
    Employee_Employee_id: int
    Vehicle_Vehicle_id: int

# --- Create (POST) ---
class DeliveryBillCreate(DeliveryBillBase):
    # สามารถรับรายการสินค้าพร้อมตอนสร้างบิลได้เลย (Optional)
    items: Optional[List[BillItemCreate]] = []

# --- Update (PUT) ---
class DeliveryBillUpdate(BaseModel):
    start_time: Optional[datetime] = None
    arrive_time: Optional[datetime] = None
    finish_time: Optional[datetime] = None
    status: Optional[DeliveryBillStatus] = None
    Employee_Employee_id: Optional[int] = None
    Vehicle_Vehicle_id: Optional[int] = None

# --- Read / Response (GET) ---
class DeliveryBill(DeliveryBillBase):
    start_time: Optional[datetime] = None
    arrive_time: Optional[datetime] = None
    finish_time: Optional[datetime] = None

    # Nested Relations: ดึงข้อมูลลูกมาโชว์
    employee: Optional[EmployeeShow] = None
    vehicle: Optional[VehicleShow] = None
    items: List[BillItem] = []           # โชว์รายการสินค้า
    time_logs: List[DeliveryTimeLog] = [] # โชว์ประวัติเวลา

    class Config:
        from_attributes = True