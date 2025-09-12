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

    // Toggle password visibility buttons (login + register)
    document.querySelectorAll('[data-toggle-password]')?.forEach(btn => {
        btn.addEventListener('click', () => {
            const input = document.querySelector(btn.getAttribute('data-toggle-password'));
            if (!input) return;
            const isPwd = input.getAttribute('type') === 'password';
            input.setAttribute('type', isPwd ? 'text' : 'password');
            btn.innerHTML = isPwd ? '<i class="far fa-eye-slash"></i>' : '<i class="far fa-eye"></i>';
        });
    });

    // Chuyển đổi Đăng nhập -> Quên mật khẩu
    if (forgotPasswordTrigger && loginFormContainer && forgotPasswordFormContainer) {
        forgotPasswordTrigger.addEventListener('click', (e) => {
            e.preventDefault();
            loginFormContainer.style.display = 'none';
            registerFormContainer && (registerFormContainer.style.display = 'none');
            forgotPasswordFormContainer.style.display = 'block';
        });
    }

    // Quay lại Đăng nhập từ Quên mật khẩu
    if (backToLoginTrigger && forgotPasswordFormContainer && loginFormContainer) {
        backToLoginTrigger.addEventListener('click', (e) => {
            e.preventDefault();
            forgotPasswordFormContainer.style.display = 'none';
            registerFormContainer && (registerFormContainer.style.display = 'none');
            loginFormContainer.style.display = 'block';
        });
    }

    // Mở form Đăng ký
    if (openRegisterTrigger && registerFormContainer && loginFormContainer) {
        openRegisterTrigger.addEventListener('click', (e) => {
            e.preventDefault();
            loginFormContainer.style.display = 'none';
            forgotPasswordFormContainer && (forgotPasswordFormContainer.style.display = 'none');
            registerFormContainer.style.display = 'block';
        });
    }

    // Quay lại Đăng nhập từ Đăng ký
    if (backToLoginFromRegister && registerFormContainer && loginFormContainer) {
        backToLoginFromRegister.addEventListener('click', (e) => {
            e.preventDefault();
            registerFormContainer.style.display = 'none';
            forgotPasswordFormContainer && (forgotPasswordFormContainer.style.display = 'none');
            loginFormContainer.style.display = 'block';
        });
    }

    // Xử lý logic đăng nhập
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const phoneNumber = document.getElementById('modalPhone').value.trim();
            const password = document.getElementById('modalPassword').value;
            if (!phoneNumber || !password) {
                alert('Vui lòng nhập đầy đủ số điện thoại và mật khẩu.');
                return;
            }
            const apiUrl = 'https://buddyskincare.pythonanywhere.com/auth/login/';
            const data = { phone_number: phoneNumber, password: password };
            try {
                const response = await fetch(apiUrl, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) });
                if (response.ok) {
                    const result = await response.json();
                    saveLoginState(result);
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

    // Xử lý logic quên mật khẩu
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

    // Xử lý logic đăng ký
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
                    // Auto-login or switch back to login
                    registerFormContainer.style.display = 'none';
                    loginFormContainer.style.display = 'block';
                    // Prefill phone to ease login
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

            // Sửa đổi ở đây để lấy đúng dữ liệu từ `result`
            const userProfileData = {
                access_token: result.access_token,
                refresh_token: result.refresh_token,
                // Lấy thông tin từ object "user_info" hoặc "user"
                // Dựa trên dữ liệu bạn cung cấp, cả hai object này đều có cùng thông tin
                phone_number: result.user.phone_number,
                name: result.user.name,
                address: result.user.address,
                dob: result.user.dob,
                email: result.user.email
            };

            saveLoginState(userProfileData);
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
// Render Google button with cleaner style once script is available
window.addEventListener('load', () => {
    if (window.google && document.getElementById('googleCustomContainer')) {
        try {
            google.accounts.id.initialize({
                client_id: '821773612134-su4afp8ac99s2l6cpvsmf0ti7p2d61aq.apps.googleusercontent.com',
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



