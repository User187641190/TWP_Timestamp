# ใช้ Python เวอร์ชั่น 3.10 เป็นตัวหลัก (เบาและเร็ว)
FROM python:3.10-slim

# ตั้งค่าโฟลเดอร์ทำงานข้างใน Docker
WORKDIR /app

# ก๊อปปี้ไฟล์ requirements.txt เข้าไปก่อน แล้วสั่งติดตั้ง
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ก๊อปปี้ไฟล์โค้ด Python ทั้งหมดของเรา (เช่น main.py, database.py, models.py) เข้าไป
COPY . .

# สั่งรัน FastAPI 
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
