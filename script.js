const API_URL = "http://127.0.0.1:8000";

async function handleLogin(event) {
        event.preventDefault();
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;

        try {
            console.log("กำลังส่งข้อมูล Login...");
            const response = await fetch(`${API_URL}/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: new URLSearchParams({
                    'username': username,
                    'password': password // ใส่ให้ครบตามฟอร์ม
                })
            });

            if (!response.ok) {
                const err = await response.json();
                throw new Error(err.detail || 'Login failed');
            }

            const data = await response.json();
            console.log("Login สำเร็จ! Token:", data);
            
            // บันทึก Token
            localStorage.setItem('token', data.access_token);
            
            // โหลดหน้าเว็บใหม่เพื่อเข้าสู่ระบบ
            window.location.reload();

        } catch (error) {
            console.error("Login Error:", error);
            alert('เข้าสู่ระบบไม่สำเร็จ: ' + error.message);
        }
    }

async function checkLogin() {
        const token = localStorage.getItem('token');
        if (!token) return; // ถ้าไม่มี Token ก็จบ (อยู่หน้า Login)

        try {
            console.log("กำลังดึงข้อมูล User...");
            const response = await fetch(`${API_URL}/users/me`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });

            if (!response.ok) {
                // ถ้า Token หมดอายุหรือ Error ให้เด้งออก
                console.warn("Token ใช้ไม่ได้ หรือหมดอายุ");
                logout();
                return;
            }

            const user = await response.json();
            console.log("ได้ข้อมูล User มาแล้ว:", user); // <--- ดูตรงนี้ใน Console!!

            // --- ส่วนสำคัญ: ซ่อนหน้า Login / เปิดหน้า Dashboard ---
            document.getElementById('loginSection').classList.add('hidden'); 
            
            // สร้างหน้า Dashboard ชั่วคราว (ถ้า HTML ไม่มี)
            let dashboard = document.getElementById('dashboardSection');
            if (!dashboard) {
                // ถ้ายังไม่ได้ทำ div dashboard ไว้ ให้สร้างหลอกๆ ขึ้นมาเทสก่อน
                document.body.innerHTML += `
                    <div id="dashboardSection" class="p-10">
                        <h1 class="text-3xl font-bold">ยินดีต้อนรับคุณ ${user.username}</h1>
                        <p class="text-xl mt-4">สถานะ: <span class="font-bold text-blue-600">${user.role}</span></p>
                        <button onclick="logout()" class="mt-6 bg-red-500 text-white px-4 py-2 rounded">Logout</button>
                    </div>
                `;
                // ซ่อน login form อีกรอบเผื่อ body.innerHTML ทับ
                 document.getElementById('loginSection')?.classList.add('hidden');
            } else {
                 dashboard.classList.remove('hidden');
            }

            // เช็ค Role (แก้ปัญหาตัวเล็ก/ใหญ่)
            const role = (user.role || "").toLowerCase();
            console.log("User Role (normalized):", role);

            if (role === 'admin') {
                console.log("-> โหมด Admin");
                // เรียกฟังก์ชันโหลดข้อมูล Admin
            } else {
                console.log("-> โหมด User ทั่วไป");
            }

        } catch (error) {
            console.error("Check Login Error:", error);
        }
    }

function logout() {
        localStorage.removeItem('token');
        window.location.reload();
    }

window.onload = checkLogin;
