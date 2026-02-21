from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import models
from database import get_db
from models import User
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# สมมติว่าฟังก์ชันนี้ถอดรหัส Token และดึง User ออกมา (ส่วนระบบ Login)
# คุณต้องมีฟังก์ชันนี้เพื่อให้รู้ว่า "ใคร" กำลังเรียกใช้งาน API
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    # ตัวอย่างแบบง่าย: เราเอา Username ไปหาใน DB
    user = db.query(models.User).filter(models.User.Username == token).first()
    if not user:
        raise HTTPException(status_code=401, detail="บัตรผ่านไม่ถูกต้อง")
    return user 
        
def check_admin_role(current_user: User = Depends(get_current_user)):
    # ตรวจสอบ role_id จากตาราง User
    if current_user.Role_role_id != 1:  # สมมติ 1 คือ Admin
        raise HTTPException(status_code=403, detail="คุณไม่มีสิทธิ์เข้าถึงส่วนนี้")
    return current_user

def check_employee_role(current_user: User = Depends(get_current_user)):
    # ตรวจสอบ role_id จากตาราง User
    if current_user.Role_role_id != 2:  # สมมติ 1 คือ Admin
        raise HTTPException(status_code=403, detail="คุณไม่มีสิทธิ์เข้าถึงส่วนนี้")
    return current_user

def check_ceo_role(current_user: User = Depends(get_current_user)):
    # ตรวจสอบ role_id จากตาราง User
    if current_user.Role_role_id != 3:  # สมมติ 1 คือ Admin
        raise HTTPException(status_code=403, detail="คุณไม่มีสิทธิ์เข้าถึงส่วนนี้")
    return current_user
  
        