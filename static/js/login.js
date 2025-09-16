
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM đã được tải. Bắt đầu thiết lập sự kiện.');

    const loginForm = document.getElementById('loginForm');
    const forgotForm = document.getElementById('forgotForm');
    const registerForm = document.getElementById('registerForm');
    const loginFormContainer = document.getElementById('loginFormContainer');
    const forgotPasswordFormContainer = document.getElementById('forgotPasswordFormContainer');
    const registerFormContainer = document.getElementById('registerFormContainer');
    const forgotPasswordTrigger = document.getElementById('forgotPasswordTrigger');
    const backToLoginTrigger = document.getElementById('backToLoginTrigger');
    const openRegisterTrigger = document.getElementById('openRegisterTrigger');
    const backToLoginFromRegister = document.getElementById('backToLoginFromRegister');

    let refreshIntervalId = null;

    // Hàm để lưu trữ trạng thái đăng nhập vào Local Storage
    function saveLoginState(data) {
        // Sử dụng lại hàm saveLoginState từ auth.js để đảm bảo tính đồng bộ
        if (typeof window.saveLoginState === 'function') {
            window.saveLoginState(data);
        } else {
            console.error("❌ Hàm saveLoginState từ auth.js không khả dụng.");
            // Trường hợp dự phòng nếu auth.js chưa được tải
            try {
                const user = data.user || data;
                const userProfile = {
                    access_token: data.access_token,
                    refresh_token: data.refresh_token,
                    id: user.id,
                    phone_number: user.phone_number,
                    name: user.name,
                    email: user.email,
                    avatar: user.avatar
                };
                localStorage.setItem('userProfile', JSON.stringify(userProfile));
                localStorage.setItem('isLoggedIn', 'true');
                localStorage.setItem('refreshToken', data.refresh_token);
                console.log(`✅ Dữ liệu đăng nhập đã được lưu vào 'userProfile'.`);
            } catch (error) {
                console.error('Lỗi khi lưu trữ thông tin đăng nhập:', error);
            }
        }
        
        const expiryTime = new Date().getTime() + 10 * 60 * 1000;
        localStorage.setItem('token_expiry_time', expiryTime);
        console.log(`✅ Thời gian hết hạn đã được lưu. Thời gian: ${new Date(expiryTime).toLocaleTimeString()}`);
    }

    // Hàm gọi API để gia hạn token
    async function refreshAccessToken() {
        console.log('🔄 Bắt đầu quá trình gia hạn token...');
        const userData = JSON.parse(localStorage.getItem('user_data'));
        if (!userData || !userData.refresh_token) {
            console.error("❌ Không tìm thấy refresh token. Vui lòng đăng nhập lại.");
            localStorage.removeItem('user_data');
            localStorage.removeItem('token_expiry_time');
            window.location.href = '/login';
            return false;
        }

        const refreshToken = userData.refresh_token;
        const apiUrl = 'https://buddyskincare.pythonanywhere.com/api/token/refresh/';
        const data = { refresh: refreshToken };

        try {
            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            if (response.ok) {
                const result = await response.json();
                console.log('✅ Token đã được gia hạn thành công.');
                userData.access_token = result.access;
                saveLoginState(userData);
                return true;
            } else {
                console.error('❌ Không thể gia hạn token. Vui lòng đăng nhập lại.');
                localStorage.removeItem('user_data');
                localStorage.removeItem('token_expiry_time');
                window.location.href = '/login';
                return false;
            }
        } catch (error) {
            console.error('❌ Lỗi khi gọi API gia hạn token:', error);
            return false;
        }
    }

    // Hàm kiểm tra và gia hạn token
    async function checkAndRefreshToken() {
        const expiryTime = localStorage.getItem('token_expiry_time');
        if (!expiryTime) {
            console.log("ℹ️ Không có thời gian hết hạn. Bỏ qua kiểm tra.");
            return;
        }

        const currentTime = new Date().getTime();
        const timeLeft = expiryTime - currentTime;
        const timeLeftInMinutes = Math.floor(timeLeft / 60000);

        if (timeLeft < 5 * 60 * 1000 && timeLeft > 0) {
            console.warn(`⚠️ Token sắp hết hạn! Còn lại ${timeLeftInMinutes} phút. Bắt đầu gia hạn...`);
            await refreshAccessToken();
        } else if (timeLeft <= 0) {
            console.error("❌ Token đã hết hạn! Bắt đầu gia hạn...");
            await refreshAccessToken();
        } else {
            console.log(`⏳ Token còn hiệu lực trong ${timeLeftInMinutes} phút.`);
        }
    }

    // Khởi động việc kiểm tra token định kỳ
    function startTokenRefresh() {
        if (refreshIntervalId) {
            clearInterval(refreshIntervalId);
        }
        refreshIntervalId = setInterval(checkAndRefreshToken, 60 * 1000);
        console.log('▶️ Đã thiết lập kiểm tra token tự động mỗi phút.');
    }

    const userData = JSON.parse(localStorage.getItem('user_data'));
    if (userData) {
        startTokenRefresh();
    }

    document.querySelectorAll('[data-toggle-password]')?.forEach(btn => {
        btn.addEventListener('click', () => {
            const input = document.querySelector(btn.getAttribute('data-toggle-password'));
            if (!input) return;
            const isPwd = input.getAttribute('type') === 'password';
            input.setAttribute('type', isPwd ? 'text' : 'password');
            btn.innerHTML = isPwd ? '<i class="far fa-eye-slash"></i>' : '<i class="far fa-eye"></i>';
        });
    });

    if (forgotPasswordTrigger && loginFormContainer && forgotPasswordFormContainer) {
        forgotPasswordTrigger.addEventListener('click', (e) => {
            e.preventDefault();
            loginFormContainer.style.display = 'none';
            registerFormContainer && (registerFormContainer.style.display = 'none');
            forgotPasswordFormContainer.style.display = 'block';
        });
    }

    if (backToLoginTrigger && forgotPasswordFormContainer && loginFormContainer) {
        backToLoginTrigger.addEventListener('click', (e) => {
            e.preventDefault();
            forgotPasswordFormContainer.style.display = 'none';
            registerFormContainer && (registerFormContainer.style.display = 'none');
            loginFormContainer.style.display = 'block';
        });
    }

    if (openRegisterTrigger && registerFormContainer && loginFormContainer) {
        openRegisterTrigger.addEventListener('click', (e) => {
            e.preventDefault();
            loginFormContainer.style.display = 'none';
            forgotPasswordFormContainer && (forgotPasswordFormContainer.style.display = 'none');
            registerFormContainer.style.display = 'block';
        });
    }

    if (backToLoginFromRegister && registerFormContainer && loginFormContainer) {
        backToLoginFromRegister.addEventListener('click', (e) => {
            e.preventDefault();
            registerFormContainer.style.display = 'none';
            forgotPasswordFormContainer && (forgotPasswordFormContainer.style.display = 'none');
            loginFormContainer.style.display = 'block';
        });
    }


    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const phoneNumber = document.getElementById('modalPhone').value.trim();
            const password = document.getElementById('modalPassword').value;
            if (!phoneNumber || !password) {
                alert('Vui lòng nhập đầy đủ số điện thoại và mật khẩu.');
                return;
            }
            const apiUrl = 'https://buddyskincare.pythonanywhere.com/login/';
            const data = { identifier: phoneNumber, password: password };
            try {
                const response = await fetch(apiUrl, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) });
                if (response.ok) {
                    const result = await response.json();
                    saveLoginState(result);
                    // Cập nhật giao diện header ngay lập tức
                    if (typeof window.updateHeaderForLoggedInUser === 'function') {
                        window.updateHeaderForLoggedInUser();
                    }
                    startTokenRefresh();
                    setTimeout(() => { window.location.href = '/'; }, 100);
                } else {
                    const error = await response.json();
                    alert(`Đăng nhập thất bại: ${error.detail || 'Có lỗi xảy ra.'}`);
                }
            } catch (error) {
                alert('Có lỗi khi kết nối đến máy chủ. Vui lòng thử lại sau.');
            }
        });
    }

    if (forgotForm) {
        forgotForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const email = document.getElementById('modalEmail').value.trim();
            if (!email) { alert('Vui lòng nhập địa chỉ email.'); return; }
            const apiUrl = 'https://buddyskincare.pythonanywhere.com/users/forgot-password/';
            try {
                const response = await fetch(apiUrl, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ email }) });
                if (response.ok) {
                    const result = await response.json();
                    alert(result.detail || 'Một mã đặt lại mật khẩu đã được gửi đến email của bạn.');
                } else {
                    const error = await response.json();
                    alert(`Gửi yêu cầu thất bại: ${error.detail || 'Có lỗi xảy ra.'}`);
                }
            } catch (error) {
                alert('Có lỗi khi kết nối đến máy chủ. Vui lòng thử lại sau.');
            }
        });
    }

    if (registerForm) {
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const name = document.getElementById('regName').value.trim();
            const phone = document.getElementById('regPhone').value.trim();
            const password = document.getElementById('regPassword').value;
            const email = document.getElementById('regEmail').value.trim() || null;
            if (!name || !phone || !password) {
                alert('Vui lòng điền Tên, Số điện thoại và Mật khẩu.');
                return;
            }
            const apiUrl = 'https://buddyskincare.pythonanywhere.com/users/register/';
            const data = { name, phone_number: phone, password, email };
            try {
                const response = await fetch(apiUrl, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) });
                if (response.ok) {
                    const result = await response.json();
                    alert('Đăng ký thành công!');
                    registerFormContainer.style.display = 'none';
                    loginFormContainer.style.display = 'block';
                    document.getElementById('modalPhone').value = phone;
                } else {
                    const error = await response.json();
                    alert(`Đăng ký thất bại: ${error.detail || 'Có lỗi xảy ra.'}`);
                }
            } catch (error) {
                alert('Có lỗi khi kết nối đến máy chủ. Vui lòng thử lại sau.');
            }
        });
    }
});

async function handleCredentialResponse(response) {
    const googleToken = response.credential;
    console.log("ID Token của Google:", googleToken);

    const apiUrl = 'https://buddyskincare.pythonanywhere.com/api/auth/google/';
    const data = {
        auth_token: googleToken
    };

    try {
        const fetchResponse = await fetch(apiUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        if (fetchResponse.ok) {
            const result = await fetchResponse.json();
            console.log('Đăng nhập bằng Google thành công:', result);

            const userProfileData = {
                access_token: result.access_token,
                refresh_token: result.refresh_token,
                id: result.user.id,
                phone_number: result.user.phone_number,
                name: result.user.name,
                address: result.user.address,
                dob: result.user.dob,
                email: result.user.email,
                avatar: result.user.avatar || result.user_info.picture
            };

            saveLoginState(userProfileData);
            // Cập nhật giao diện header ngay lập tức
            if (typeof window.updateHeaderForLoggedInUser === 'function') {
                window.updateHeaderForLoggedInUser();
            }
            startTokenRefresh();
            alert('Đăng nhập bằng Google thành công!');
            window.location.href = '/';
        } else {
            const error = await fetchResponse.json();
            console.error('Đăng nhập bằng Google thất bại:', error);
            alert(`Đăng nhập bằng Google thất bại: ${error.detail || 'Có lỗi xảy ra.'}`);
        }
    } catch (error) {
        console.error('Lỗi khi gửi yêu cầu đăng nhập Google:', error);
        alert('Có lỗi khi kết nối đến máy chủ. Vui lòng thử lại sau.');
    }
}

window.addEventListener('load', () => {
    if (window.google && document.getElementById('googleCustomContainer')) {
        try {
            google.accounts.id.initialize({
                client_id: '821773612134-1u5206jkloc187irc108rqfcrcvb4420.apps.googleusercontent.com',
                callback: handleCredentialResponse
            });
            google.accounts.id.renderButton(
                document.getElementById('googleCustomContainer'),
                {
                    type: 'standard',
                    theme: 'outline',
                    size: 'large',
                    width: 360,
                    text: 'signin_with',
                    shape: 'rectangular',
                    logo_alignment: 'left'
                }
            );
        } catch (e) {}
    }
});