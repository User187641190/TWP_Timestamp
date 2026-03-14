from sqlalchemy import Column, Integer, String, ForeignKey, DECIMAL, DateTime
from sqlalchemy.orm import relationship
from database import Base # เช็คให้ชัวร์ว่า import Base มาจากไฟล์ database.py ของคุณนะครับ

class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    address = Column(String(255))
    phone_number = Column(String(20))

    # Relationship
    bills = relationship("DeliveryBill", back_populates="customer")

class Employee(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    work_status = Column(String(50))

class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"))
    employee_id = Column(Integer, ForeignKey("employees.id"))

class Vehicle(Base):
    __tablename__ = "vehicles"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    description = Column(String(255))

class Warehouse(Base):
    __tablename__ = "warehouses"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    address = Column(String(255))
    contact_number = Column(String(20))

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    unit_price = Column(DECIMAL(10, 2))
    stock_qty = Column(Integer)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"))

class DeliveryBill(Base):
    __tablename__ = "delivery_bills"
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    employee_id = Column(Integer, ForeignKey("employees.id"))
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"))
    destination_address = Column(String(255))
    recipient_name = Column(String(100))
    recipient_phone = Column(String(20))

    # Relationship กลับไปหา Customer
    customer = relationship("Customer", back_populates="bills")

class DeliveryItem(Base):
    __tablename__ = "delivery_items"
    id = Column(Integer, primary_key=True, index=True)
    bill_id = Column(Integer, ForeignKey("delivery_bills.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer)

class DeliveryLog(Base):
    __tablename__ = "delivery_logs"
    id = Column(Integer, primary_key=True, index=True)
    bill_id = Column(Integer, ForeignKey("delivery_bills.id"))
    status_type = Column(String(50))
    logged_at = Column(DateTime)