from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import models
from database import get_db
from models import User
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

SECRET_KEY = "o14jd*%@vt6(l3qd(6%__0k)ptmo&7=$)6isq_n4w7=a6&xw_c"
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
#     # ตัวอย่างแบบง่าย: เราเอา Username ไปหาใน DB
#     user = db.query(models.User).filter(models.User.Username == token).first()
#     if not user:
#         raise HTTPException(status_code=401, detail="บัตรผ่านไม่ถูกต้อง")
#     return user 

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # SECRET_KEY และ ALGORITHM ต้องตรงกับตอนสร้าง Token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    # ค้นหา User ใน Database
    user = db.query(models.User).filter(models.User.Username == username).first()
    if user is None:
        raise credentials_exception
    return user


#############

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
  
        