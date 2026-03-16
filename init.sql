
CREATE TABLE IF NOT EXISTS Customer (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_name VARCHAR(100) NOT NULL,
    customer_address VARCHAR(255),
    customer_phone VARCHAR(20)
);

-- =========================
-- Employee
-- =========================
CREATE TABLE IF NOT EXISTS Employee (
    employee_id INT AUTO_INCREMENT PRIMARY KEY,
    employee_name VARCHAR(100) NOT NULL,
    employee_status VARCHAR(50)
);

-- =========================
-- Role
-- =========================
CREATE TABLE IF NOT EXISTS Role (
    role_id INT AUTO_INCREMENT PRIMARY KEY,
    role_name VARCHAR(50) NOT NULL
);

-- =========================
-- User
-- =========================
CREATE TABLE IF NOT EXISTS User (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role_id INT,
    employee_id INT,
    FOREIGN KEY (role_id) REFERENCES Role(role_id),
    FOREIGN KEY (employee_id) REFERENCES Employee(employee_id)
);

-- =========================
-- Vehicle
-- =========================
CREATE TABLE IF NOT EXISTS Vehicle (
    vehicle_id INT AUTO_INCREMENT PRIMARY KEY,
    vehicle_name VARCHAR(100),
    vehicle_description VARCHAR(255)
);

-- =========================
-- Warehouse
-- =========================
CREATE TABLE IF NOT EXISTS Warehouse (
    warehouse_id INT AUTO_INCREMENT PRIMARY KEY,
    warehouse_name VARCHAR(100),
    warehouse_address VARCHAR(255),
    warehouse_phone VARCHAR(20)
);

-- =========================
-- Product
-- =========================
CREATE TABLE IF NOT EXISTS Product (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    product_name VARCHAR(100),
    price DECIMAL(10,2),
    stock_quantity INT,
    warehouse_id INT,
    FOREIGN KEY (warehouse_id) REFERENCES Warehouse(warehouse_id)
);

-- =========================
-- DeliveryBill
-- =========================
CREATE TABLE IF NOT EXISTS DeliveryBill (
    bill_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT,
    employee_id INT,
    vehicle_id INT,
    delivery_address VARCHAR(255),
    receiver_name VARCHAR(100),
    receiver_phone VARCHAR(20),
    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id),
    FOREIGN KEY (employee_id) REFERENCES Employee(employee_id),
    FOREIGN KEY (vehicle_id) REFERENCES Vehicle(vehicle_id)
);

-- =========================
-- BillItem
-- =========================
CREATE TABLE IF NOT EXISTS BillItem (
    bill_item_id INT AUTO_INCREMENT PRIMARY KEY,
    bill_id INT,
    product_id INT,
    product_quantity INT,
    FOREIGN KEY (bill_id) REFERENCES DeliveryBill(bill_id),
    FOREIGN KEY (product_id) REFERENCES Product(product_id)
);

-- =========================
-- DeliveryBill_Time_Log
-- =========================
CREATE TABLE IF NOT EXISTS DeliveryBill_Time_Log (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    bill_id INT,
    event_type VARCHAR(50),
    event_time DATETIME,
    FOREIGN KEY (bill_id) REFERENCES DeliveryBill(bill_id)
);






-- INSERT




-- ==========================================
-- 1. เพิ่มข้อมูลสิทธิ์การใช้งาน (Roles)
-- ==========================================
INSERT INTO roles (id, name) VALUES 
(1, 'Admin'),
(2, 'Employee'),
(3, 'CEO');

-- ==========================================
-- 2. เพิ่มข้อมูลพนักงาน (Employees)
-- ==========================================
INSERT INTO employees (id, name, work_status) VALUES 
(1, 'สมชาย สายซิ่ง (พนักงานขับรถ)', 'Active'),
(2, 'สมหญิง จริตงาม (แอดมิน)', 'Active'),
(3, 'ธนาธิป วิสัยทัศน์ (CEO)', 'Active'),
(4, 'วีระ แบกหนัก (พนักงานขับรถ)', 'Active'),
(5, 'อำนาจ ตรวจสอบ (พนักงานคลัง)', 'Active');

-- ==========================================
-- 3. เพิ่มบัญชีผู้ใช้งาน (Users) 
-- (รหัสผ่านผมใส่เป็น 123456 แบบไม่ได้เข้ารหัสเพื่อให้คุณล็อกอินเทสได้ง่ายๆ ก่อน)
-- ==========================================
INSERT INTO users (id, username, password_hash, role_id, employee_id) VALUES 
(1, 'admin_ying', '123456', 1, 2),
(2, 'driver_chai', '123456', 2, 1),
(3, 'ceo_thanatip', '123456', 3, 3),
(4, 'driver_weera', '123456', 2, 4);

-- ==========================================
-- 4. เพิ่มข้อมูลลูกค้า (Customers)
-- ==========================================
INSERT INTO customers (id, name, address, phone_number) VALUES 
(1, 'บจก. สร้างไทย วิศวกรรม', '123 ม.4 ถ.บางนา-ตราด กทม.', '021112222'),
(2, 'เฮียเส็ง รับเหมาก่อสร้าง', '45/6 ซ.สุขุมวิท 50 กทม.', '0891234567'),
(3, 'สมศักดิ์ โฮมบิลเดอร์', '789 ถ.รามอินทรา กทม.', '0819876543'),
(4, 'เจ๊นก วัสดุภัณฑ์', '12 ตลาดรังสิต ปทุมธานี', '0865554433');

-- ==========================================
-- 5. เพิ่มข้อมูลยานพาหนะ (Vehicles)
-- ==========================================
INSERT INTO vehicles (id, name, description) VALUES 
(1, '1กข-1234 กทม.', 'รถกระบะตอนเดียว (บรรทุก 1 ตัน)'),
(2, '2ฮฮ-5555 กทม.', 'รถหกล้อคอกสูง (บรรทุก 5 ตัน)'),
(3, '3ฒณ-9999 กทม.', 'รถสิบล้อ (บรรทุก 15 ตัน)'),
(4, 'ป้ายแดง-001', 'รถโฟล์คลิฟท์ (ใช้ในโกดัง)');

-- ==========================================
-- 6. เพิ่มข้อมูลคลังสินค้า (Warehouses)
-- ==========================================
INSERT INTO warehouses (id, name, address, contact_number) VALUES 
(1, 'โกดังหลัก (บางนา)', 'กม.10 ถ.บางนา-ตราด', '023334444'),
(2, 'โกดังสาขา 2 (รังสิต)', 'ใกล้ตลาดไท ปทุมธานี', '029998888');

-- ==========================================
-- 7. เพิ่มข้อมูลสินค้า (Products) - ตีมวัสดุก่อสร้าง
-- ==========================================
INSERT INTO products (id, name, unit_price, stock_qty, warehouse_id) VALUES 
(1, 'ปูนซีเมนต์ปอร์ตแลนด์ (ถัง/กระสอบ)', 145.00, 1500, 1),
(2, 'อิฐมวลเบา หนา 7.5 ซม. (ก้อน)', 22.50, 10000, 1),
(3, 'เหล็กเส้นกลม SR24 9มม. (เส้น)', 185.00, 3000, 2),
(4, 'เหล็กข้ออ้อย SD40 12มม. (เส้น)', 260.00, 2500, 2),
(5, 'ทรายหยาบ (คิว)', 450.00, 200, 1),
(6, 'หินคลุก (คิว)', 550.00, 150, 1),
(7, 'กระเบื้องหลังคาลอนคู่ 5มม. (แผ่น)', 65.00, 5000, 2),
(8, 'สีทาภายใน ถัง 18 ลิตร (ถัง)', 1250.00, 80, 1),
(9, 'ท่อ PVC 2 นิ้ว ชั้น 8.5 (เส้น)', 95.00, 600, 2),
(10, 'ปูนกาวซีเมนต์ จระเข้เขียว (ถุง)', 160.00, 400, 1);

-- ==========================================
-- 8. เพิ่มข้อมูลบิลจัดส่ง (Delivery Bills)
-- ==========================================
INSERT INTO delivery_bills (id, customer_id, employee_id, vehicle_id, destination_address, recipient_name, recipient_phone) VALUES 
(1, 1, 1, 3, 'ไซต์งานก่อสร้างคอนโด สุขุมวิท 101', 'นายช่างใหญ่', '0891112233'),
(2, 2, 4, 2, 'หมู่บ้านจัดสรร รามอินทรา ซอย 5', 'เฮียเส็ง', '0891234567'),
(3, 3, 1, 1, 'บ้านเดี่ยว 2 ชั้น ปทุมธานี', 'ช่างเอก', '0812223344');

-- ==========================================
-- 9. เพิ่มรายการสินค้าในบิล (Delivery Items)
-- ==========================================
-- บิลที่ 1: ส่งปูน 500 ถุง, ทราย 20 คิว, หิน 20 คิว (ไซต์งานใหญ่)
INSERT INTO delivery_items (bill_id, product_id, quantity) VALUES 
(1, 1, 500),
(1, 5, 20),
(1, 6, 20);

-- บิลที่ 2: ส่งอิฐมวลเบา 2000 ก้อน, ปูนกาว 100 ถุง
INSERT INTO delivery_items (bill_id, product_id, quantity) VALUES 
(2, 2, 2000),
(2, 10, 100);

-- บิลที่ 3: ส่งกระเบื้องหลังคา 500 แผ่น, ท่อ PVC 50 เส้น
INSERT INTO delivery_items (bill_id, product_id, quantity) VALUES 
(3, 7, 500),
(3, 9, 50);

-- ==========================================
-- 10. เพิ่มบันทึกเวลาและสถานะการจัดส่ง (Delivery Logs)
-- ==========================================
-- บิลที่ 1: ส่งสำเร็จแล้ว
INSERT INTO delivery_logs (bill_id, status_type, logged_at) VALUES 
(1, 'Pending', '2023-10-25 08:00:00'),
(1, 'Shipping', '2023-10-25 09:30:00'),
(1, 'Delivered', '2023-10-25 11:45:00');

-- บิลที่ 2: กำลังจัดส่ง
INSERT INTO delivery_logs (bill_id, status_type, logged_at) VALUES 
(2, 'Pending', '2023-10-26 10:00:00'),
(2, 'Shipping', '2023-10-26 13:15:00');

-- บิลที่ 3: รอดำเนินการ (เพิ่งสร้างบิล)
INSERT INTO delivery_logs (bill_id, status_type, logged_at) VALUES 
(3, 'Pending', '2023-10-27 09:00:00');





--VIEW
CREATE VIEW vw_user_roles_details AS
SELECT 
    u.id AS user_id, 
    u.username, 
    e.name AS employee_name, 
    r.name AS role_name, 
    e.work_status
FROM users u
JOIN employees e ON u.employee_id = e.id
JOIN roles r ON u.role_id = r.id;

CREATE VIEW vw_warehouse_inventory_value AS
SELECT 
    w.name AS warehouse_name, 
    COUNT(p.id) AS total_product_types, 
    SUM(p.stock_qty) AS total_items_in_stock, 
    SUM(p.stock_qty * p.unit_price) AS total_inventory_value
FROM warehouses w
LEFT JOIN products p ON w.id = p.warehouse_id
GROUP BY w.id, w.name;


CREATE VIEW vw_delivery_bill_info AS
SELECT 
    db.id AS bill_id, 
    c.name AS customer_name, 
    e.name AS driver_name, 
    v.name AS vehicle_plate, 
    db.recipient_name, 
    db.destination_address
FROM delivery_bills db
LEFT JOIN customers c ON db.customer_id = c.id
LEFT JOIN employees e ON db.employee_id = e.id
LEFT JOIN vehicles v ON db.vehicle_id = v.id;

CREATE VIEW vw_bill_total_value AS
SELECT 
    di.bill_id, 
    SUM(di.quantity) AS total_items, 
    SUM(di.quantity * p.unit_price) AS total_price
FROM delivery_items di
JOIN products p ON di.product_id = p.id
GROUP BY di.bill_id;

CREATE VIEW vw_employee_delivery_stats AS
SELECT 
    e.id AS employee_id, 
    e.name AS employee_name, 
    COUNT(db.id) AS total_deliveries
FROM employees e
LEFT JOIN delivery_bills db ON e.id = db.employee_id
GROUP BY e.id, e.name;

CREATE VIEW vw_latest_delivery_status AS
SELECT 
    dl.bill_id, 
    dl.status_type AS current_status, 
    dl.logged_at AS last_updated
FROM delivery_logs dl
WHERE dl.logged_at = (
    SELECT MAX(logged_at)
    FROM delivery_logs dl2
    WHERE dl2.bill_id = dl.bill_id
);

CREATE VIEW vw_vehicle_usage_summary AS
SELECT 
    v.id AS vehicle_id, 
    v.name AS vehicle_plate, 
    v.description, 
    COUNT(db.id) AS total_trips
FROM vehicles v
LEFT JOIN delivery_bills db ON v.id = db.vehicle_id
GROUP BY v.id, v.name, v.description;

CREATE VIEW vw_customer_order_summary AS
SELECT 
    c.id AS customer_id, 
    c.name AS customer_name, 
    COUNT(DISTINCT db.id) AS total_orders, 
    COALESCE(SUM(di.quantity * p.unit_price), 0) AS lifetime_spent
FROM customers c
LEFT JOIN delivery_bills db ON c.id = db.customer_id
LEFT JOIN delivery_items di ON db.id = di.bill_id
LEFT JOIN products p ON di.product_id = p.id
GROUP BY c.id, c.name;

CREATE VIEW vw_low_stock_products AS
SELECT 
    id, 
    name AS product_name, 
    stock_qty, 
    unit_price
FROM products
WHERE stock_qty < (SELECT AVG(stock_qty) FROM products);

CREATE VIEW vw_master_delivery_dashboard AS
SELECT 
    b.id AS bill_id,
    c.name AS customer_name,
    e.name AS driver_name,
    v.name AS vehicle_plate,
    COALESCE(SUM(di.quantity), 0) AS total_items,
    COALESCE(SUM(di.quantity * p.unit_price), 0) AS total_amount,
    (SELECT status_type FROM delivery_logs WHERE bill_id = b.id ORDER BY logged_at DESC LIMIT 1) AS current_status
FROM delivery_bills b
LEFT JOIN customers c ON b.customer_id = c.id
LEFT JOIN employees e ON b.employee_id = e.id
LEFT JOIN vehicles v ON b.vehicle_id = v.id
LEFT JOIN delivery_items di ON b.id = di.bill_id
LEFT JOIN products p ON di.product_id = p.id
GROUP BY b.id, c.name, e.name, v.name;