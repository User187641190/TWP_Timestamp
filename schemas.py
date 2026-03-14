from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

# --- Configuration พื้นฐานสำหรับการแปลง SQLAlchemy Model เป็น JSON ---
class OrmBase(BaseModel):
    class Config:
        from_attributes = True

# =========================
# 1. Roles
# =========================
class RoleBase(BaseModel):
    name: str

class RoleCreate(RoleBase):
    pass

class RoleResponse(RoleBase, OrmBase):
    id: int

# =========================
# 2. Employees
# =========================
class EmployeeBase(BaseModel):
    name: str
    work_status: Optional[str] = None

class EmployeeCreate(EmployeeBase):
    pass

class EmployeeResponse(EmployeeBase, OrmBase):
    id: int

# =========================
# 3. Customers
# =========================
class CustomerBase(BaseModel):
    name: str
    address: Optional[str] = None
    phone_number: Optional[str] = None

class CustomerCreate(CustomerBase):
    pass

class CustomerResponse(CustomerBase, OrmBase):
    id: int

# =========================
# 4. Vehicles
# =========================
class VehicleBase(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class VehicleCreate(VehicleBase):
    pass

class VehicleResponse(VehicleBase, OrmBase):
    id: int

# =========================
# 5. Warehouses
# =========================
class WarehouseBase(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    contact_number: Optional[str] = None

class WarehouseCreate(WarehouseBase):
    pass

class WarehouseResponse(WarehouseBase, OrmBase):
    id: int

# =========================
# 6. Products
# =========================
class ProductBase(BaseModel):
    name: str
    unit_price: Decimal
    stock_qty: int
    warehouse_id: Optional[int] = None

class ProductCreate(ProductBase):
    pass

class ProductResponse(ProductBase, OrmBase):
    id: int

# =========================
# 7. Users
# =========================
class UserCreate(BaseModel):
    username: str
    password: str # รับรหัสผ่านจากหน้าบ้าน
    role_id: Optional[int] = None
    employee_id: Optional[int] = None

class UserResponse(OrmBase):
    id: int
    username: str
    role_id: Optional[int]
    employee_id: Optional[int]
    # ไม่ส่ง password กลับ

# =========================
# 8. Delivery Bills
# =========================
class DeliveryBillBase(BaseModel):
    customer_id: Optional[int] = None
    employee_id: Optional[int] = None
    vehicle_id: Optional[int] = None
    destination_address: Optional[str] = None
    recipient_name: Optional[str] = None
    recipient_phone: Optional[str] = None

class DeliveryBillCreate(DeliveryBillBase):
    pass

class DeliveryBillResponse(DeliveryBillBase, OrmBase):
    id: int

# =========================
# 9. Delivery Items
# =========================
class DeliveryItemBase(BaseModel):
    bill_id: Optional[int] = None
    product_id: Optional[int] = None
    quantity: Optional[int] = None

class DeliveryItemCreate(DeliveryItemBase):
    pass

class DeliveryItemResponse(DeliveryItemBase, OrmBase):
    id: int

# =========================
# 10. Delivery Logs
# =========================
class DeliveryLogBase(BaseModel):
    bill_id: Optional[int] = None
    status_type: Optional[str] = None
    logged_at: Optional[datetime] = None

class DeliveryLogCreate(DeliveryLogBase):
    pass

class DeliveryLogResponse(DeliveryLogBase, OrmBase):
    id: int