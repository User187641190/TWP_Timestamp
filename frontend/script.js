const API_URL = "http://127.0.0.1:8000"; 

// ---- 1. AUTHENTICATION ----
async function handleLogin(e) {
    e.preventDefault();
    const u = document.getElementById('username').value;
    const p = document.getElementById('password').value;
    
    try {
        // ยิง API Login
        const res = await fetch(`${API_URL}/login`, {
            method: 'POST',
            headers: {'Content-Type': 'application/x-www-form-urlencoded'},
            body: new URLSearchParams({username: u, password: p})
        });

        if(!res.ok) throw new Error("Login failed");
        const data = await res.json();
        
        // เก็บ Token
        localStorage.setItem('token', data.access_token);
        // รีโหลดเพื่อเข้าหน้า Dashboard
        window.location.reload();

    } catch(err) {
        Swal.fire({
            title: 'ผิดพลาด!',
            text: 'User หรือ Password ผิดพลาด',
            icon: 'error',
            confirmButtonText: 'ตกลง',
            confirmButtonColor: '#3b82f6' // สีฟ้าแบบ Tailwind
        });
    }
}

function logout() {
    localStorage.removeItem('token');
    window.location.reload();
}

// ---- 2. INITIALIZATION ----
window.onload = async () => {
    const token = localStorage.getItem('token');
    if(!token) return; 

    document.getElementById('loginSection').classList.add('hidden');
    document.getElementById('dashboardSection').classList.remove('hidden');

    try {
        const res = await fetch(`${API_URL}/users/me`, {
            headers: {'Authorization': `Bearer ${token}`}
        });
        
        if(!res.ok) throw new Error("Token expired");
        const user = await res.json();

        // 🔍 DEBUG: ดูค่าที่ได้จาก API จริงๆ (กด F12 ดู Console)
        console.log("User Data from API:", user); 

        // แสดงชื่อ
        document.getElementById('user-display-name').innerText = user.Username || user.username;
        
        // ถ้าไม่มี Role_name ส่งมา ให้เดาจาก ID เอา
        let r_id = user.Role_id || user.Role_role_id; // ✅ แก้ตรงนี้: เช็คทั้ง 2 ชื่อ
        
        // Mapping ชื่อ Role เพื่อแสดงผล (กรณี Backend ไม่ส่ง Role_name มา)
        let r_name = user.Role_name;
        if (!r_name) {
            if(r_id == 1) r_name = "Admin";
            else if(r_id == 2) r_name = "Employee";
            else if(r_id == 3) r_name = "CEO";
            else r_name = "Unknown";
        }
        document.getElementById('user-display-role').innerText = r_name;

        // เช็ค Role เพื่อเปิดเมนู
        checkRole(r_id); 

    } catch(err) {
        console.error("Auth Error:", err);
        logout();
    }
};

function checkRole(roleId) {
    // ซ่อนเมนูทั้งหมดก่อน
    document.getElementById('menu-admin').classList.add('hidden');
    document.getElementById('menu-employee').classList.add('hidden');
    document.getElementById('menu-ceo').classList.add('hidden');

    // แปลงเป็นตัวเลขให้ชัวร์ (เผื่อมาเป็น String)
    const id = parseInt(roleId);

    if (id === 1) {
        // === ADMIN ===
        console.log("Welcome Admin!");
        document.getElementById('menu-admin').classList.remove('hidden');
        showPage('admin-user'); // เปิดหน้าแรกของ Admin
    } 
    else if (id === 2) {
        // === EMPLOYEE ===
        console.log("Welcome Employee!");
        document.getElementById('menu-employee').classList.remove('hidden');
        showPage('emp-list-bill'); // เปิดหน้าแรกของ Employee
        loadDropdowns(); // โหลดข้อมูลรถรอไว้เลย
    } 
    else if (id === 3) {
        // === CEO ===
        console.log("Welcome CEO!");
        document.getElementById('menu-ceo').classList.remove('hidden');
        showPage('ceo-page'); // เปิดหน้าแรกของ CEO
        loadCEOCharts(); // วาดกราฟทันที
    } 
    else {
        alert("Role ของคุณไม่ถูกต้อง กรุณาติดต่อผู้ดูแลระบบ");
        logout();
    }
}

// ---- 3. NAVIGATION ----
function showPage(pageId) {
    // ซ่อนทุกหน้า
    document.querySelectorAll('.page-content').forEach(el => el.classList.add('hidden'));
    // โชว์หน้าที่เลือก
    document.getElementById(pageId).classList.remove('hidden');
    
    // Highlight ปุ่มเมนู (Optional styling logic here)
    document.querySelectorAll('.nav-btn').forEach(btn => btn.classList.remove('bg-slate-700', 'border-l-4', 'border-blue-500'));
    
    // โหลดข้อมูลตามหน้า
    if(pageId === 'admin-emp') loadAdminData('employees');
    if(pageId === 'admin-vehicle') loadAdminData('vehicles');
    if(pageId === 'admin-user') loadAdminData('users');
    if(pageId === 'emp-list-bill') loadBills();
}

// ---- 4. ADMIN FUNCTIONS ----
async function loadAdminData(type) {
    const token = localStorage.getItem('token');
    try {
        const res = await fetch(`${API_URL}/${type}/`, { headers: {'Authorization': `Bearer ${token}`} });
        if(!res.ok) return;
        const data = await res.json();
        
        let html = '';
        if(type === 'employees') {
            html = data.map(e => `
                <tr class="hover:bg-gray-50 border-b">
                    <td class="p-4 font-mono">${e.Employee_id}</td>
                    <td class="p-4 font-bold text-gray-700">${e.Employee_name}</td>
                    <td class="p-4 text-gray-600">${e.Phone}</td>
                    <td class="p-4"><span class="px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs">${e.Status}</span></td>
                    <td class="p-4 text-right">
                        <button onclick="deleteData('employees', ${e.Employee_id})" class="bg-red-500 hover:bg-red-600 text-white px-3 py-1 rounded text-sm shadow-sm transition">
                            <i class="fas fa-trash"></i> ลบ
                        </button>
                    </td>
                </tr>`).join('');
            document.getElementById('table-emps').innerHTML = html;
        }
        else if(type === 'vehicles') {
                // 🔍 ปริ้นข้อมูลออกมาดูใน Console (กด F12)
                console.log("Vehicle Data from API:", data); 

                html = data.map(v => {
                    // รองรับทั้งตัวพิมพ์เล็กและพิมพ์ใหญ่
                    const id = v.Vehicle_id || v.vehicle_id;
                    const plate = v.License_plate || v.license_plate;
                    const status = v.Status || v.status;
                    const desc = v.Description || v.description || "-"; // ถ้าไม่มีรายละเอียดให้แสดงขีด

                    return `
                    <tr class="hover:bg-gray-50 border-b">
                        <td class="p-4 font-mono">${id}</td>
                        <td class="p-4">
                            <div class="font-bold text-blue-900">${plate}</div>
                            <div class="text-xs text-gray-500">${desc}</div> 
                        </td>
                        <td class="p-4">
                            <span class="px-2 py-1 rounded-full text-xs ${status === 'Available' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}">
                                ${status}
                            </span>
                        </td>
                        <td class="p-4 text-right">
                            <button onclick="deleteData('vehicles', ${id})" class="bg-red-500 hover:bg-red-600 text-white px-3 py-1 rounded text-sm shadow-sm transition">
                                <i class="fas fa-trash"></i> ลบ
                            </button>
                        </td>
                    </tr>`;
                }).join('');
                document.getElementById('table-vehs').innerHTML = html;
            }
        else if(type === 'users') {
            html = data.map(u => `
                <tr class="hover:bg-gray-50 border-b">
                    <td class="p-4 font-mono">${u.User_id}</td>
                    <td class="p-4 font-bold">${u.Username}</td>
                    <td class="p-4 text-sm text-gray-500">${u.Role_role_id === 1 ? 'Admin' : (u.Role_role_id === 3 ? 'CEO' : 'Employee')}</td>
                    <td class="p-4"><span class="px-2 py-1 bg-blue-50 text-blue-700 rounded text-xs">${u.status || 'Active'}</span></td>
                    <td class="p-4 text-right">
                        <button onclick="deleteData('users', ${u.User_id})" class="bg-red-500 hover:bg-red-600 text-white px-3 py-1 rounded text-sm shadow-sm transition">
                            <i class="fas fa-trash"></i> ลบ
                        </button>
                    </td>
                </tr>`).join('');
            document.getElementById('table-users').innerHTML = html;
        }

    } catch(e) { console.error("Load Error:", e); }
}

async function adminCreateEmp(e) {
    e.preventDefault();
    // // Database Auto ID, ส่งแค่ชื่อกับเบอร์
    // const body = {
    //     Employee_name: document.getElementById('emp_name').value,
    //     Phone: document.getElementById('emp_phone').value,
    //     Status: "Active" 
    // };
    const empName = document.getElementById('emp_name').value;
    const empPhone = document.getElementById('emp_phone').value;
    

    if (empPhone.length !== 10) {
        Swal.fire({
            title: 'เบอร์โทรศัพท์ไม่ถูกต้อง',
            text: 'กรุณากรอกเบอร์โทรศัพท์ให้ครบ 10 หลัก',
            icon: 'warning',
            confirmButtonColor: '#f59e0b'
        });
        return; 
    }
    const body = {
        Employee_name: empName, 
        Phone: empPhone,        
        Status: "Active"
    };

    try {
        await sendPost('/employees/', body);
        Swal.fire({
            title: 'สำเร็จ!',
            text: 'เพิ่มพนักงานใหม่เรียบร้อยแล้ว',
            icon: 'success',
            confirmButtonText: 'ตกลง',
            confirmButtonColor: '#3b82f6'
        });
        loadAdminData('employees');

    } catch (err) {
        // กรณี Error (sendPost อาจจะ throw error มา)
        // ปกติ sendPost เรามี alert อยู่แล้ว แต่ถ้าอยากให้สวยด้วยก็แก้ใน sendPost ได้ครับ
    }
}

async function adminCreateVehicle(e) {
    e.preventDefault();
    const body = {
        License_plate: document.getElementById('veh_plate').value,
        Description: document.getElementById('veh_desc').value,
        Status: document.getElementById('veh_status').value
    };
    if (!veh_plate) {
        Swal.fire({
            title: 'แจ้งเตือน',
            text: 'กรุณากรอกทะเบียนรถ',
            icon: 'warning',
            confirmButtonColor: '#f59e0b'
        });
        return;
    }
    try {
        await sendPost('/vehicles', body);
        Swal.fire({
            title: 'สำเร็จ!',
            text: 'เพิ่มยานพาหนะเรียบร้อยแล้ว',
            icon: 'success',
            confirmButtonColor: '#3b82f6'
        });
        loadAdminData('vehicles');

    } catch (err) {
        console.error(err);
        }
}

async function adminCreateUser(e) {
    e.preventDefault();
    
    const empId = parseInt(document.getElementById('new_u_empid').value);
    const roleId = parseInt(document.getElementById('new_u_role').value);
    
    if(isNaN(empId)) { alert("กรุณาใส่รหัสพนักงานเป็นตัวเลข"); return; }

    try {
            const token = localStorage.getItem('token');
            const resUsers = await fetch(`${API_URL}/users/`, { 
                headers: { 'Authorization': `Bearer ${token}` } 
            });
            const currentUsers = await resUsers.json();

            // 🟢 2. ตรวจสอบว่า Employee_id นี้มีในระบบแล้วหรือยัง
            const isDuplicate = currentUsers.some(u => u.Employee_Employee_id === empId);
            
            if (isDuplicate) {
                Swal.fire({
                    title: '❌ ข้อมูลซ้ำ!',
                    text: `รหัสพนักงาน ${empId} มีบัญชีผู้ใช้งานอยู่แล้วในระบบ`,
                    icon: 'warning', // ใช้ไอคอนแจ้งเตือนสีเหลือง
                    confirmButtonText: 'ตกลง',
                    confirmButtonColor: '#f59e0b' // สีเหลืองส้ม Tailwind
                });
                return; // 🛑 สั่งหยุดการทำงานทันที ไม่ให้ส่ง API สร้าง User ต่อ
            }

        } catch (err) {
            console.error("เช็คข้อมูลซ้ำไม่ได้:", err);
            // ถ้าดึงข้อมูลมาเช็คไม่ได้ อาจจะปล่อยผ่านหรือแจ้งเตือนตามเหมาะสม
        }

    const body = {
        Username: document.getElementById('new_u_name').value,
        Password_hash: document.getElementById('new_u_pass').value,
        Role_role_id: roleId,
        Employee_Employee_id: empId,
        status: "Active"
    };
    try {
        // รอส่งข้อมูล ถ้าเกิด Error (เช่น 404, 422) มันจะกระโดดไปที่ catch ทันที
        await sendPost('/users/', body);
            Swal.fire({
                title: 'สำเร็จ!',
                text: 'เพิ่มบัญชีผู้ใช้ใหม่เรียบร้อยแล้ว',
                icon: 'success',
                confirmButtonText: 'ตกลง',
                confirmButtonColor: '#3b82f6' // สีฟ้าแบบ Tailwind
            });
            loadAdminData('users');
    } catch (error) {
        console.error("สร้าง User ไม่สำเร็จ:", error);
        Swal.fire({
            title: '❌ เกิดข้อผิดพลาด!',
            text: 'ไม่สามารถสร้างผู้ใช้ได้ (ตรวจสอบข้อมูล Employee ID หรือ API URL อีกครั้ง)',
            icon: 'error',
            confirmButtonText: 'ตกลง',
            confirmButtonColor: '#ef4444' // สีแดงแบบ Tailwind
        });
    }
}

// ---- 5. EMPLOYEE FUNCTIONS ----
async function loadDropdowns() {
    const token = localStorage.getItem('token');
    try {
        // ดึงข้อมูลมาเติมใน Select Box
        const [resV, resU , resE] = await Promise.all([
            fetch(`${API_URL}/vehicles/`, { headers: {'Authorization': `Bearer ${token}`} }),
            fetch(`${API_URL}/users/`, { headers: {'Authorization': `Bearer ${token}`} }),
            fetch(`${API_URL}/employees/`, { headers: {'Authorization': `Bearer ${token}`}})
        ]);
        const vehs = await resV.json();
        const user = await resU.json();
        const emp = await resE.json();
        
        document.getElementById('bill_vehicle').innerHTML = vehs.map(v => {
            const id = v.Vehicle_id || v.vehicle_id;
            const plate = v.License_plate || v.license_plate;
            const desc = v.Description || v.description || "";
            // โชว์ทะเบียน + รายละเอียด (ถ้ามี)
            const displayName = desc ? `${plate} (${desc})` : plate;
            return `<option value="${id}">${displayName} - [${v.Status || v.status}]</option>`;
        }).join('');
        
        const filteredEmployees = emp.filter(emp => {
            // หาว่าใน array 'users' มีใครที่ id ตรงกัน และ Role เป็น 2 หรือไม่ (ถ้ามี .some() จะรีเทิร์น true)
            return user.some(user => 
                    user.Role_role_id === 2 && 
                    emp.Employee_id === user.Employee_Employee_id
                );
            });

        document.getElementById('bill_employee').innerHTML = filteredEmployees
            .map(emp => `<option value="${emp.Employee_id}">${emp.Employee_name}</option>`)
            .join('');
    } 
    catch(e) { 
        console.error("Error loading dropdown:", e);    
    }
}

async function createBill(e) {
    e.preventDefault();
    const now = new Date();
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    const currentTime = `${hours}:${minutes}`;
    
    const today = new Date();
    const year = today.getFullYear();
    const month = String(today.getMonth() + 1).padStart(2, '0'); // เดือนใน JS เริ่มที่ 0 เลยต้อง +1
    const day = String(today.getDate()).padStart(2, '0');
    const currentDate = `${year}-${month}-${day}`;

    const body = {
        Bill_id: parseInt(document.getElementById('bill_id').value),
        Vehicle_Vehicle_id: parseInt(document.getElementById('bill_vehicle').value),
        Employee_Employee_id: parseInt(document.getElementById('bill_employee').value),
        Receiver_name: document.getElementById('bill_receiver').value,
        Receiver_phone: document.getElementById('bill_phone').value,
        start_time: currentTime,
        delivery_date: currentDate
    };

    try {await sendPost('/delivery-bills/', body);
        Swal.fire({
            title: 'สำเร็จ!',
            text: 'เพิ่มบิลใหม่เรียบร้อยแล้ว',
            icon: 'success',
            confirmButtonText: 'ตกลง',
            confirmButtonColor: '#3b82f6' // สีฟ้าแบบ Tailwind
        });
        showPage('emp-list-bill'); // เด้งไปหน้ารายการ
    }
    catch (error) {
        console.error("เกิดข้อผิดพลาด: ", error);
    }
}

async function loadBills() {
    const token = localStorage.getItem('token');
    const res = await fetch(`${API_URL}/delivery-bills/`, { headers: {'Authorization': `Bearer ${token}`} });
    const bills = await res.json();
    
    const html = bills.map(b => `
        <tr class="border-b hover:bg-gray-50 transition">
            <td class="p-4 font-mono text-sm text-gray-500">#${b.Bill_id}</td>
            <td class="p-4 font-medium">${b.Receiver_name}</td>
            <td class="p-4 text-gray-500">${b.Receiver_phone}</td>
            <td class="p-4">
                <span class="px-3 py-1 rounded-full text-xs font-bold shadow-sm ${getStatusColor(b.status)}">
                    ${b.status}
                </span>
            </td>
            <td class="p-4 text-center">
                <button onclick="openModal(${b.Bill_id}, '${b.status}')" class="bg-blue-50 text-blue-600 border border-blue-200 px-3 py-1 rounded hover:bg-blue-100 text-xs transition">
                    <i class="fas fa-edit"></i> เปลี่ยนสถานะ
                </button>
            </td>
        </tr>
    `).join('');
    document.getElementById('billTableBody').innerHTML = html;
}

// ---- 6. HELPERS ----
async function sendPost(endpoint, body) {
    const token = localStorage.getItem('token');
    try {
        const res = await fetch(`${API_URL}${endpoint}`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json', 'Authorization': `Bearer ${token}`},
            body: JSON.stringify(body)
        });
        
        if (!res.ok) {
            const err = await res.json();
            // ✅ แก้ตรงนี้ เพื่อให้มันแปลง Error ของ FastAPI มาเป็นข้อความให้อ่านง่ายๆ
            const errorMsg = JSON.stringify(err.detail || err, null, 2);
            Swal.fire({
                icon: 'error',
                title: '❌ เกิดข้อผิดพลาด',
                // ใช้ html และ <pre> เพื่อให้เว้นบรรทัด JSON สวยงาม
                html: `<pre style="text-align: left; background: #f8f9fa; padding: 10px; border-radius: 5px; font-size: 14px;">${errorMsg}</pre>`,
                confirmButtonColor: '#ef4444',
                confirmButtonText: 'ตกลง'
            });
            throw new Error(errorMsg);
        }
        // ถ้าสำเร็จ ให้เคลียร์ฟอร์ม
        document.querySelectorAll('input').forEach(i => i.value = '');
    } catch(e) { 
        console.error(e);
        throw e; 
    }
}

function getStatusColor(status) {
    if(status === 'Delivered') return 'bg-green-100 text-green-700 border border-green-200';
    if(status === 'Pending') return 'bg-yellow-100 text-yellow-700 border border-yellow-200';
    if(status === 'Cancel') return 'bg-red-100 text-red-700 border border-red-200';
    return 'bg-gray-100 text-gray-700 border border-gray-200';
}

// Modal Logic
function openModal(id, currentStatus) {
    document.getElementById('modal_bill_id').value = id;
    document.getElementById('modal_bill_display').innerText = id;
    document.getElementById('modal_new_status').value = currentStatus;
    document.getElementById('statusModal').classList.remove('hidden');
}

function closeModal() {
    document.getElementById('statusModal').classList.add('hidden');
}

async function saveStatus() {
    const id = document.getElementById('modal_bill_id').value;
    const status = document.getElementById('modal_new_status').value;
    const token = localStorage.getItem('token');

    const res = await fetch(`${API_URL}/delivery-bills/${id}/status`, {
        method: 'PUT',
        headers: {'Content-Type': 'application/json', 'Authorization': `Bearer ${token}`},
        body: JSON.stringify({ status: status })
    });
    if(res.ok) { closeModal(); loadBills(); }
    else { alert("อัปเดตไม่สำเร็จ"); }
}

// ---- 7. CEO CHARTS ----
let chart1, chart2;
async function loadCEOCharts() {
    const token = localStorage.getItem('token');
    const res = await fetch(`${API_URL}/dashboard/stats`, { headers: {'Authorization': `Bearer ${token}`} });
    const data = await res.json();

    if(chart1) chart1.destroy();
    if(chart2) chart2.destroy();

    // Chart 1: Vehicles
    const ctx1 = document.getElementById('vehicleChart').getContext('2d');
    chart1 = new Chart(ctx1, {
        type: 'doughnut',
        data: {
            labels: Object.keys(data.vehicles),
            datasets: [{
                data: Object.values(data.vehicles),
                backgroundColor: ['#4ade80', '#ef4444', '#fbbf24'] // Green, Red, Yellow
            }]
        }
    });

    // Chart 2: Employees
    const ctx2 = document.getElementById('employeeChart').getContext('2d');
    chart2 = new Chart(ctx2, {
        type: 'bar',
        data: {
            labels: Object.keys(data.employees),
            datasets: [{
                label: 'จำนวนพนักงาน',
                data: Object.values(data.employees),
                backgroundColor: '#60a5fa'
            }]
        },
        options: { scales: { y: { beginAtZero: true } } }
    });
}

async function deleteData(type, id) {
    // 1. เรียกหน้าต่างยืนยัน SweetAlert2
    const result = await Swal.fire({
        title: 'คุณแน่ใจหรือไม่?',
        text: "ข้อมูลนี้จะถูกลบอย่างถาวรและกู้คืนไม่ได้!",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#ef4444', // สีแดง
        cancelButtonColor: '#9ca3af',  // สีเทา
        confirmButtonText: 'ใช่, ลบเลย!',
        cancelButtonText: 'ยกเลิก'
    });

    // 2. ถ้าผู้ใช้กด "ใช่, ลบเลย!"
    if (result.isConfirmed) {
        try {
            // ส่ง Request แบบ DELETE ไปที่ Backend
            // (แก้ URL ให้ตรงกับพอร์ตที่คุณใช้ ปกติคือ 8000)
            const response = await fetch(`http://127.0.0.1:8000/${type}/${id}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                // แจ้งเตือนว่าลบสำเร็จ
                Swal.fire(
                    'ลบสำเร็จ!',
                    'ข้อมูลถูกลบออกจากระบบแล้ว',
                    'success'
                );
                // โหลดตารางใหม่เพื่อให้ข้อมูลอัปเดต
                loadAdminData(type);
            } else {
                // กรณีลบไม่ได้ (เช่น ติด Foreign Key)
                Swal.fire('ลบไม่ได้!', 'เกิดข้อผิดพลาดจากเซิร์ฟเวอร์ หรือข้อมูลนี้ถูกใช้งานอยู่', 'error');
            }
        } catch (error) {
            console.error(error);
            Swal.fire('ผิดพลาด', 'ไม่สามารถเชื่อมต่อกับเซิร์ฟเวอร์ได้', 'error');
        }
    }
}

async function deleteData(type, id) {
    // 1. เรียกหน้าต่างยืนยัน SweetAlert2
    const result = await Swal.fire({
        title: 'คุณแน่ใจหรือไม่?',
        text: "ข้อมูลนี้จะถูกลบอย่างถาวรและกู้คืนไม่ได้!",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#ef4444', // สีแดง
        cancelButtonColor: '#9ca3af',  // สีเทา
        confirmButtonText: 'ใช่, ลบเลย!',
        cancelButtonText: 'ยกเลิก'
    });

    // 2. ถ้าผู้ใช้กด "ใช่, ลบเลย!"
    if (result.isConfirmed) {
        try {
            // ส่ง Request แบบ DELETE ไปที่ Backend
            // (แก้ URL ให้ตรงกับพอร์ตที่คุณใช้ ปกติคือ 8000)
            const response = await fetch(`http://127.0.0.1:8000/${type}/${id}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                // แจ้งเตือนว่าลบสำเร็จ
                Swal.fire(
                    'ลบสำเร็จ!',
                    'ข้อมูลถูกลบออกจากระบบแล้ว',
                    'success'
                );
                // โหลดตารางใหม่เพื่อให้ข้อมูลอัปเดต
                loadAdminData(type);
            } else {
                // กรณีลบไม่ได้ (เช่น ติด Foreign Key)
                Swal.fire('ลบไม่ได้!', 'เกิดข้อผิดพลาดจากเซิร์ฟเวอร์ หรือข้อมูลนี้ถูกใช้งานอยู่', 'error');
            }
        } catch (error) {
            console.error(error);
            Swal.fire('ผิดพลาด', 'ไม่สามารถเชื่อมต่อกับเซิร์ฟเวอร์ได้', 'error');
        }
    }
}

// --- script.js ---

// ฟังก์ชันเปิด/ปิดรหัสผ่าน
function togglePassword() {
    // ใช้ id ตามฟอร์มของคุณเลยครับ
    const passwordInput = document.getElementById('new_u_pass'); 
    const eyeIcon = document.getElementById('eye_icon');

    if (passwordInput.type === 'password') {
        // เปลี่ยนเป็นโชว์ตัวหนังสือ
        passwordInput.type = 'text';
        // เปลี่ยนรูปตาเป็นขีดฆ่า
        eyeIcon.classList.remove('fa-eye');
        eyeIcon.classList.add('fa-eye-slash');
    } else {
        // เปลี่ยนกลับเป็นจุดดำๆ
        passwordInput.type = 'password';
        // เปลี่ยนรูปตาเป็นตาปกติ
        eyeIcon.classList.remove('fa-eye-slash');
        eyeIcon.classList.add('fa-eye');
    }
}

function toggleLoginPassword() {
    // ใช้ id ตามฟอร์มของคุณเลยครับ
    const passwordInput = document.getElementById('password'); 
    const eyeIcon = document.getElementById('eye_icon');

    if (passwordInput.type === 'password') {
        // เปลี่ยนเป็นโชว์ตัวหนังสือ
        passwordInput.type = 'text';
        // เปลี่ยนรูปตาเป็นขีดฆ่า
        eyeIcon.classList.remove('fa-eye');
        eyeIcon.classList.add('fa-eye-slash');
    } else {
        // เปลี่ยนกลับเป็นจุดดำๆ
        passwordInput.type = 'password';
        // เปลี่ยนรูปตาเป็นตาปกติ
        eyeIcon.classList.remove('fa-eye-slash');
        eyeIcon.classList.add('fa-eye');
    }
}

async function changeVehicleStatus(vehicleId, newStatus) {
    const token = localStorage.getItem('token');
    
    try {
        const res = await fetch(`${API_URL}/vehicles/${vehicleId}/status`, {
            method: 'PUT',
            headers: { 
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}` 
            },
            body: JSON.stringify({ status: newStatus })
        });

        if (!res.ok) {
            const err = await res.json();
            Swal.fire('ข้อผิดพลาด', err.detail, 'error');
            return;
        }

        Swal.fire('สำเร็จ', 'อัพเดตสถานะรถเรียบร้อยแล้ว', 'success');
        
        // รีเฟรชตารางรถใหม่
        loadAdminData('vehicles'); 
        
    } catch (e) {
        console.error("Error updating status:", e);
    }
}

