import enum
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Date , Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship
from database import Base
import datetime

###  Enum
class EmployeeStatus(str, enum.Enum):
    ACTIVE = "Active"       #ทำงาน
    ON_LEAVE = "On Leave"   #ลาออก
    HOLIDAY = "Holiday"   #หยุด

class VehicleStatus(str, enum.Enum):
    AVAILABLE = "Available"     #ใช้งานได้
    IN_USE = "In Use"           #ใช้งานอยู่
    MAINTENANCE = "Maintenance" #ซ่อม

class DeliveryBillStatus(str, enum.Enum):
    AWAIT = "Await"         #รอส่ง
    PENDING = "Pending"     #กำลังส่ง
    Delivered = "Delivered" 
    Cancel = "Cancel"       

##NormalAttibute
class Employee(Base):
    __tablename__ = "Employee"

    Employee_id = Column(Integer, primary_key=True)
    Employee_name = Column(String(128))
    Phone = Column(String(10))
    Status = Column(SQLAlchemyEnum(EmployeeStatus), default=EmployeeStatus.HOLIDAY, nullable=False)
    deliveries = relationship("DeliveryBill", back_populates="employee")
    users = relationship("User", back_populates="employee") # แก้ชื่อ back_populates ให้ตรงกันด้วยนะครับ (ถ้ามี)

class Vehicle(Base):
    __tablename__ = "Vehicle"

    Vehicle_id = Column(Integer, primary_key=True)
    license_plate = Column(String(200))
    Vehicle_description = Column(String(200))
    Status = Column(SQLAlchemyEnum(VehicleStatus), default=VehicleStatus.AVAILABLE, nullable=False)
    deliveries = relationship("DeliveryBill", back_populates="vehicle")


class DeliveryBill(Base):
    __tablename__ = "Delivery_bill"

    bill_id = Column(Integer, primary_key=True)
    Receiver_name = Column(String(100), nullable=True)
    Receiver_phone = Column(String(20), nullable=True)
    start_time = Column(DateTime)
    arrive_time = Column(DateTime)
    finish_time = Column(DateTime)
    delivery_date = Column(Date)
    status = Column(SQLAlchemyEnum(DeliveryBillStatus), default=DeliveryBillStatus.AWAIT ,nullable=False)
    # Foreign Keys map ตาม SQL ที่ให้มา
    Employee_Employee_id = Column(Integer, ForeignKey("Employee.Employee_id"), nullable=False)
    Vehicle_Vehicle_id = Column(Integer, ForeignKey("Vehicle.Vehicle_id"), nullable=False)

    # Relationships
    employee = relationship("Employee", back_populates="deliveries")
    vehicle = relationship("Vehicle", back_populates="deliveries")
    items = relationship("BillItem", back_populates="delivery_bill")
    time_logs = relationship("DeliveryTimeLog", back_populates="delivery_bill")

class Product(Base):
    __tablename__ = "Product"

    Product_id = Column(Integer, primary_key=True)
    Product_name = Column(String(500))
    Price = Column(Integer)
    bill_items = relationship("BillItem", back_populates="product")

class BillItem(Base):
    __tablename__ = "Bill_item"
    Bill_item_id = Column(Integer, primary_key=True) # ใน SQL ไม่ได้กำหนด PK ชัดเจนแต่ควรมี หรือใช้ Composite Key
    Quantity = Column(Integer)
    Delivery_bill_bill_id = Column(Integer, ForeignKey("Delivery_bill.bill_id"), nullable=False)
    Product_Product_id = Column(Integer, ForeignKey("Product.Product_id"), nullable=False)
    #relation
    delivery_bill = relationship("DeliveryBill", back_populates="items")
    product = relationship("Product", back_populates="bill_items")

class DeliveryTimeLog(Base):
    __tablename__ = "Delivery_Time_log"

    Time_log_id = Column(String(50), primary_key=True) # สมมติให้เป็น PK
    Event_time = Column(String(200))
    Timestamp = Column(Date)
    Remark = Column(String(2000))
    bill_id = Column(Integer, ForeignKey("Delivery_bill.bill_id"), nullable=False)

    delivery_bill = relationship("DeliveryBill", back_populates="time_logs")

class Role(Base):
    __tablename__ = "Role"

    role_id = Column(Integer, primary_key=True)
    role_name = Column(String(50))
    description = Column(String(200))

    users = relationship("User", back_populates="role")
    permissions = relationship("RolePermissions", back_populates="role")

class Permission(Base):
    __tablename__ = "Permission"

    permission_id = Column(Integer, primary_key=True)
    permission_name = Column(String(50))
    Description = Column(String(200))

    roles = relationship("RolePermissions", back_populates="permission")

class RolePermissions(Base):
    __tablename__ = "Role_permissios"
    
    # เนื่องจากเป็น Link Table ปกติจะใช้ Composite Primary Key
    Permission_permission_id = Column(Integer, ForeignKey("Permission.permission_id"), primary_key=True)
    Role_role_id = Column(Integer, ForeignKey("Role.role_id"), primary_key=True)

    permission = relationship("Permission", back_populates="roles")
    role = relationship("Role", back_populates="permissions")

class User(Base):
    __tablename__ = "User" # User เป็นคำสงวนในบาง DB ต้องระวัง

    User_id = Column(Integer, primary_key=True)
    Username = Column(String(50))
    Password_hash = Column(String(50)) # แนะนำให้ขยายเป็น 255 ในอนาคตถ้าใช้ Hash จริงๆ
    status = Column(String(200))
    Created_at = Column(Date, default=datetime.date.today)
    Employee_Employee_id = Column(Integer, ForeignKey("Employee.Employee_id"), nullable=False)
    Role_role_id = Column(Integer, ForeignKey("Role.role_id"), nullable=False)
    role = relationship("Role", back_populates="users")
    employee = relationship("Employee", back_populates="users")
#=======
