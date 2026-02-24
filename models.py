import enum
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Date, Enum, Identity
from sqlalchemy.orm import relationship
from database import Base
import datetime

# ==========================
# 1. ENUMS (ตัวเลือกต่างๆ)
# ==========================
class EmployeeStatus(str, enum.Enum):
    ACTIVE = "Active"       # ทำงาน
    ON_LEAVE = "On Leave"   # ลา
    HOLIDAY = "Holiday"     # หยุด

class VehicleStatus(str, enum.Enum):
    AVAILABLE = "Available"     # ใช้งานได้
    IN_USE = "In Use"           # ใช้งานอยู่
    MAINTENANCE = "Maintenance" # ซ่อม

class DeliveryBillStatus(str, enum.Enum):
    AWAIT = "Await"         # รอส่ง
    PENDING = "Pending"     # กำลังส่ง
    DELIVERED = "Delivered" # ส่งแล้ว
    CANCEL = "Cancel"       # ยกเลิก

# ==========================
# 2. TABLES (ตาราง)
# ==========================

class Employee(Base):
    __tablename__ = "Employee"

    # Identity ใช้สำหรับ Auto Increment (Oracle 12c+)
    Employee_id = Column(Integer, Identity(start=1), primary_key=True)
    Employee_name = Column(String(128))
    Phone = Column(String(10))
    
    # ใช้ Enum ตรงๆ (ไม่ต้องมี name=... ก็ได้ถ้าไม่ได้ซีเรียสเรื่องชื่อ Constraint ใน Oracle)
    Status = Column(Enum(EmployeeStatus), default=EmployeeStatus.ACTIVE, nullable=False)

    deliveries = relationship("DeliveryBill", back_populates="employee")
    # users = relationship("User", back_populates="employee") 

class Vehicle(Base):
    __tablename__ = "Vehicle"
    Vehicle_id = Column(Integer, Identity(start=1), primary_key=True)
    License_plate = Column(String(20))
    
    Status = Column(Enum(VehicleStatus), default=VehicleStatus.AVAILABLE, nullable=False)
    
    deliveries = relationship("DeliveryBill", back_populates="vehicle")

class DeliveryBill(Base):
    __tablename__ = "DeliveryBill"
    Bill_id = Column(Integer, Identity(start=1), primary_key=True)
    
    # FK
    Employee_Employee_id = Column(Integer, ForeignKey("Employee.Employee_id"))
    Vehicle_Vehicle_id = Column(Integer, ForeignKey("Vehicle.Vehicle_id"))
    
    Receiver_name = Column(String(100))
    Receiver_phone = Column(String(20))
    
    start_time = Column(DateTime, default=datetime.datetime.now)
    arrive_time = Column(DateTime, nullable=True)
    finish_time = Column(DateTime, nullable=True)
    
    status = Column(Enum(DeliveryBillStatus), default=DeliveryBillStatus.AWAIT)

    # Relation
    employee = relationship("Employee", back_populates="deliveries")
    vehicle = relationship("Vehicle", back_populates="deliveries")
    items = relationship("BillItem", back_populates="bill")
    time_logs = relationship("DeliveryTimeLog", back_populates="bill")

class BillItem(Base):
    __tablename__ = "BillItem"
    Item_id = Column(Integer, Identity(start=1), primary_key=True)
    Product_name = Column(String(100))
    Quantity = Column(Integer)
    
    DeliveryBill_Bill_id = Column(Integer, ForeignKey("DeliveryBill.Bill_id"))
    bill = relationship("DeliveryBill", back_populates="items")

class DeliveryTimeLog(Base):
    __tablename__ = "DeliveryTimeLog"
    Log_id = Column(Integer, Identity(start=1), primary_key=True)
    Timestamp = Column(DateTime, default=datetime.datetime.now)
    Status = Column(String(50))
    
    DeliveryBill_Bill_id = Column(Integer, ForeignKey("DeliveryBill.Bill_id"))
    bill = relationship("DeliveryBill", back_populates="time_logs")

# --- Role & User System ---

class Role(Base):
    __tablename__ = "Role"
    role_id = Column(Integer, Identity(start=1), primary_key=True)
    role_name = Column(String(50))
    Description = Column(String(200))
    
    permissions = relationship("RolePermissions", back_populates="role")
    users = relationship("User", back_populates="role") # เพิ่ม relation กลับไปหา User

class Permission(Base):
    __tablename__ = "Permission"
    permission_id = Column(Integer, Identity(start=1), primary_key=True)
    permission_name = Column(String(50))
    Description = Column(String(200))

    roles = relationship("RolePermissions", back_populates="permission")

class RolePermissions(Base):
    __tablename__ = "Role_permissios"
    
    Permission_permission_id = Column(Integer, ForeignKey("Permission.permission_id"), primary_key=True)
    Role_role_id = Column(Integer, ForeignKey("Role.role_id"), primary_key=True)

    permission = relationship("Permission", back_populates="roles")
    role = relationship("Role", back_populates="permissions")

class User(Base):
    __tablename__ = "User" # Oracle อาจจะต้องใช้ชื่ออื่นถ้า User เป็น reserved word (เช่น AppUser) แต่ลองใช้ User ดูก่อนได้ครับ

    User_id = Column(Integer, Identity(start=1), primary_key=True)
    Username = Column(String(50), unique=True) # ควรมี unique
    Password_hash = Column(String(255))
    status = Column(String(50), default="Active")
    Created_at = Column(Date, default=datetime.date.today)
    
    Employee_Employee_id = Column(Integer, ForeignKey("Employee.Employee_id"))
    Role_role_id = Column(Integer, ForeignKey("Role.role_id"))
    
    role = relationship("Role", back_populates="users")
    # employee = relationship("Employee", back_populates="users")