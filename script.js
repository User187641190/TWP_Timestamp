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
        alert("เข้าสู่ระบบไม่สำเร็จ: ชื่อผู้ใช้หรือรหัสผ่านผิด");
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
                </tr>`).join('');
            document.getElementById('table-emps').innerHTML = html;
        }
        else if(type === 'vehicles') {
            html = data.map(v => `
                <tr class="hover:bg-gray-50 border-b">
                    <td class="p-4 font-mono">${v.Vehicle_id}</td>
                    <td class="p-4 font-bold text-blue-900">${v.License_plate}</td>
                    <td class="p-4">
                        <span class="px-2 py-1 rounded-full text-xs ${v.Status === 'Available' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}">
                            ${v.Status}
                        </span>
                    </td>
                </tr>`).join('');
            document.getElementById('table-vehs').innerHTML = html;
        }
        else if(type === 'users') {
            html = data.map(u => `
                <tr class="hover:bg-gray-50 border-b">
                    <td class="p-4 font-mono">${u.User_id}</td>
                    <td class="p-4 font-bold">${u.Username}</td>
                    <td class="p-4 text-sm text-gray-500">${u.Role_role_id === 1 ? 'Admin' : (u.Role_role_id === 3 ? 'CEO/Driver' : 'Employee')}</td>
                    <td class="p-4"><span class="px-2 py-1 bg-blue-50 text-blue-700 rounded text-xs">${u.status || 'Active'}</span></td>
                </tr>`).join('');
            document.getElementById('table-users').innerHTML = html;
        }

    } catch(e) { console.error("Load Error:", e); }
}

async function adminCreateEmp(e) {
    e.preventDefault();
    // Database Auto ID, ส่งแค่ชื่อกับเบอร์
    const body = {
        Employee_name: document.getElementById('emp_name').value,
        Phone: document.getElementById('emp_phone').value,
        Status: "Active" 
    };
    if (phone.length !== 10) {
        Swal.fire({
            title: 'เบอร์โทรศัพท์ไม่ถูกต้อง',
            text: 'กรุณากรอกเบอร์โทรศัพท์ให้ครบ 10 หลัก',
            icon: 'warning',
            confirmButtonColor: '#f59e0b'
        });
        return; // สั่งหยุดทำงาน ไม่ส่งข้อมูลไป Backend
    }
    try {
        await sendPost('/employees/', body);

        // ✅ ใช้ SweetAlert แทน alert ธรรมดา
        Swal.fire({
            title: 'สำเร็จ!',
            text: 'เพิ่มพนักงานใหม่เรียบร้อยแล้ว',
            icon: 'success',
            confirmButtonText: 'ตกลง',
            confirmButtonColor: '#3b82f6' // สีฟ้าแบบ Tailwind
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
        Status: document.getElementById('veh_status').value
    };
    await sendPost('/vehicles', body);

    Swal.fire({
            title: 'สำเร็จ!',
            text: 'เพิ่มรถเรียบร้อยแล้ว',
            icon: 'success',
            confirmButtonText: 'ตกลง',
            confirmButtonColor: '#3b82f6' // สีฟ้าแบบ Tailwind
        });
    loadAdminData('vehicles');
}

async function adminCreateUser(e) {
    e.preventDefault();
    // สำคัญ: ต้องแปลงค่าเป็น Int ก่อนส่ง
    const empId = parseInt(document.getElementById('new_u_empid').value);
    const roleId = parseInt(document.getElementById('new_u_role').value);
    
    if(isNaN(empId)) { alert("กรุณาใส่รหัสพนักงานเป็นตัวเลข"); return; }

    const body = {
        Username: document.getElementById('new_u_name').value,
        Password_hash: document.getElementById('new_u_pass').value,
        Role_role_id: roleId,
        Employee_id: empId,
        status: "Active"
    };
    await sendPost('/users', body);
    Swal.fire({
            title: 'สำเร็จ!',
            text: 'เพิ่มบัญชีผู้ใช้ใหม่เรียบร้อยแล้ว',
            icon: 'success',
            confirmButtonText: 'ตกลง',
            confirmButtonColor: '#3b82f6' // สีฟ้าแบบ Tailwind
        });
    loadAdminData('users');
}

// ---- 5. EMPLOYEE FUNCTIONS ----
async function loadDropdowns() {
    const token = localStorage.getItem('token');
    try {
        // ดึงข้อมูลมาเติมใน Select Box
        const [resV, resE] = await Promise.all([
            fetch(`${API_URL}/vehicles/`, { headers: {'Authorization': `Bearer ${token}`} }),
            fetch(`${API_URL}/employees/`, { headers: {'Authorization': `Bearer ${token}`} })
        ]);
        const vehs = await resV.json();
        const emps = await resE.json();

        document.getElementById('bill_vehicle').innerHTML = vehs.map(v => 
            `<option value="${v.Vehicle_id}">${v.License_plate} (${v.Status})</option>`).join('');
        document.getElementById('bill_employee').innerHTML = emps.map(e => 
            `<option value="${e.Employee_id}">${e.Employee_name}</option>`).join('');
    } catch(e) { console.error(e); }
}

async function createBill(e) {
    e.preventDefault();
    const body = {
        Receiver_name: document.getElementById('bill_receiver').value,
        Receiver_phone: document.getElementById('bill_phone').value,
        Vehicle_Vehicle_id: parseInt(document.getElementById('bill_vehicle').value),
        Employee_Employee_id: parseInt(document.getElementById('bill_employee').value)
    };
    await sendPost('/delivery-bills/', body);
    Swal.fire({
            title: 'สำเร็จ!',
            text: 'เพิ่มบิลใหม่เรียบร้อยแล้ว',
            icon: 'success',
            confirmButtonText: 'ตกลง',
            confirmButtonColor: '#3b82f6' // สีฟ้าแบบ Tailwind
        });
    showPage('emp-list-bill'); // เด้งไปหน้ารายการ
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
        
        if(!res.ok) {
            const err = await res.json();
            alert("❌ เกิดข้อผิดพลาด: " + (err.detail || JSON.stringify(err)));
            throw new Error(err.detail);
        }
        // ถ้าสำเร็จ ให้เคลียร์ฟอร์ม
        document.querySelectorAll('input').forEach(i => i.value = '');
    } catch(e) { 
        console.error(e); 
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