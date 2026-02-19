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

# class PermissionChecker:
#     def __init__(self, required_permission: str):
#         self.required_permission = required_permission

#     def __call__(self, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
#         # 1. ดึง Role ของ User คนนี้
#         user_role = user.role # Relationship ใน models.py ต้อง setup ไว้
        
#         # 2. เช็คว่า Role นี้มี Permission ที่ต้องการไหม
#         # เราต้อง Loop ผ่านตาราง RolePermissions ที่เชื่อมอยู่
#         # user.role.permissions คือ list ของ RolePermissions objects
#         has_perm = False
#         for rp in user_role.permissions:
#             if rp.permission.permission_name == self.required_permission:
#                 has_perm = True
#                 break
        
#         # 3. ถ้าไม่มีสิทธิ์ ให้เตะออก (403 Forbidden)
#         if not has_perm:
#             raise HTTPException(
#                 status_code=status.HTTP_403_FORBIDDEN,
#                 detail=f"Operation not permitted. Requires '{self.required_permission}'"
#             )
        
        