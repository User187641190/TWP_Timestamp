from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, date
# Import Enums จาก models.py (ต้องมีไฟล์ models.py ที่ประกาศ Enum ไว้แล้วนะ)
from models import EmployeeStatus, VehicleStatus, DeliveryBillStatus

# ==========================================
# 1. Base Schemas & Shared (พื้นฐาน)
# ==========================================

#——————————————————————————            
# --- User / Login System ---
#——————————————————————————            
class UserBase(BaseModel):
    User_id: int
    Username: str
    status: str | None = "Active" 

class UserCreate(UserBase):
    Password_hash: str
    # รับค่า ID แบบสั้นๆ เข้ามา
    Employee_id: int 
    Role_role_id: int 

class User(UserBase):
    # เวลาส่งข้อมูลกลับ ไม่ควรส่ง Password_hash กลับไป (เพื่อความปลอดภัย)
    Employee_Employee_id: int
    Role_role_id: int
    
    class Config:
        from_attributes = True
#——————————————————————————            
# --- Product (สินค้า) ---
#——————————————————————————        

class ProductBase(BaseModel):
    Product_name: str
    Price: float

class ProductCreate(ProductBase):
    Product_id: int  # สมมติว่าเป็นรหัสสินค้า เช่น 'P-001'

class Product(ProductBase):
    Product_id: int
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
    Product_id: int
    Product_name: str
    class Config:
        from_attributes = True

# ==========================================
# 3. Main Entity Schemas (ข้อมูลหลัก)
# ==========================================

#——————————————————————————            
# --- Employee ---
#——————————————————————————            

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
#——————————————————————————            
# --- Vehicle ---
#——————————————————————————            
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

#——————————————————————————            
# --- Bill Item (รายการสินค้าในบิล) ---
#——————————————————————————            
class BillItemBase(BaseModel):
    Product_id: str = Field(alias="Product_id") # แบบนี้จะส่งคำว่า Product_id ได้เลย
    Quantity: int
class BillItemCreate(BillItemBase):
    pass

class BillItem(BillItemBase):
    Bill_item_id: int
    product: Optional[ProductShow] = None # โชว์ชื่อสินค้าด้วย
    class Config:
        from_attributes = True

#——————————————————————————            
# --- Time Log (ประวัติเวลา) ---
#——————————————————————————            
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

#——————————————————————————            
# --- Base ---
#——————————————————————————            
class DeliveryBillBase(BaseModel):
    bill_id: int
    delivery_date: Optional[date] = None
    status: DeliveryBillStatus = DeliveryBillStatus.AWAIT
    Receiver_name : str     #Name
    Receiver_phone : str
    start_time : datetime    #011-111-1111
    Employee_Employee_id: int   #1,2,3 etc.
    Vehicle_Vehicle_id: int #1,2,3 etc.

class DeliveryBillCreate(DeliveryBillBase):
    # สามารถรับรายการสินค้าพร้อมตอนสร้างบิลได้เลย (Optional)
    items: Optional[List[BillItemCreate]] = []

class DeliveryBillUpdate(BaseModel):
    start_time: Optional[datetime] = None
    arrive_time: Optional[datetime] = None
    finish_time: Optional[datetime] = None
    status: Optional[DeliveryBillStatus] = None
    Employee_Employee_id: Optional[int] = None
    Vehicle_Vehicle_id: Optional[int] = None

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

#——————————————————————————            
# - - - Roles - - - 
#——————————————————————————            
class RoleBase(BaseModel):
    role_id: int
    role_name: str
    description: str | None = None

class RoleCreate(RoleBase):
    pass

class Role(RoleBase):
    class Config:
        from_attributes = True
