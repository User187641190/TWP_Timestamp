import requests
import json

# 🛠️ ตั้งค่า Base URL (แก้ Port ถ้าของคุณไม่ใช่ 8000)
BASE_URL = "http://127.0.0.1:8000"

def print_result(name, response):
    if response.status_code in [200, 201]:
        print(f"✅ {name}: ผ่าน (Status {response.status_code})")
        # print(f"   Response: {response.json()}") # เอาคอมเมนต์ออกถ้าอยากเห็นข้อมูลดิบ
    else:
        print(f"❌ {name}: ไม่ผ่าน (Status {response.status_code})")
        print(f"   Error: {response.text}")

def test_api():
    print("🚀 เริ่มต้นการทดสอบระบบ API ทั้งหมด...\n")

    # ==========================================
    # 1. ทดสอบ Employee (พนักงาน)
    # ==========================================
    print("--- 👤 Testing Employee ---")
    
    # 1.1 สร้าง Employee ใหม่
    emp_data = {
        "Employee_id": 999,  # ID สมมติสำหรับการทดสอบ
        "Employee_name": "Test Script Robot",
        "Phone": "0800000000",
        "Status": "Holiday" # ต้องตรงกับ Enum ใน models.py
    }
    response = requests.post(f"{BASE_URL}/employees/", json=emp_data)
    print_result("Create Employee", response)

    # 1.2 ดึงข้อมูล Employee ทั้งหมด
    response = requests.get(f"{BASE_URL}/employees/")
    print_result("Get All Employees", response)

    # ==========================================
    # 2. ทดสอบ Vehicle (ยานพาหนะ)
    # ==========================================
    print("\n--- 🚗 Testing Vehicle ---")
    
    # 2.1 สร้าง Vehicle ใหม่
    vehicle_data = {
        "Vehicle_id": 888,
        "license_plate": "99-9999",
        "Status": "Available" # ต้องตรงกับ Enum ใน models.py
    }
    # หมายเหตุ: เช็ค URL ให้ตรงกับใน main.py ของคุณ (เช่น /vehicles/ หรือ /vehicle/)
    response = requests.post(f"{BASE_URL}/vehicles/", json=vehicle_data)
    print_result("Create Vehicle", response)

    # 2.2 ดึงข้อมูล Vehicle ทั้งหมด
    response = requests.get(f"{BASE_URL}/vehicles/")
    print_result("Get All Vehicles", response)

    print("\n🏁 จบการทดสอบ")

if __name__ == "__main__":
    try:
        test_api()
    except Exception as e:
        print(f"💥 เกิดข้อผิดพลาดในการเชื่อมต่อ: {e}")
        print("ตรวจสอบว่า Server รันอยู่หรือยัง? (uvicorn main:app --reload)")