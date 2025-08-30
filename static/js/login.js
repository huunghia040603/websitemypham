document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM đã được tải. Bắt đầu thiết lập sự kiện.');

    const loginForm = document.getElementById('loginForm');
    const forgotForm = document.getElementById('forgotForm');
    const loginFormContainer = document.getElementById('loginFormContainer');
    const forgotPasswordFormContainer = document.getElementById('forgotPasswordFormContainer');
    const forgotPasswordTrigger = document.getElementById('forgotPasswordTrigger');
    const backToLoginTrigger = document.getElementById('backToLoginTrigger');

    console.log('Đã tìm thấy các phần tử:');
    console.log('loginFormContainer:', loginFormContainer);
    console.log('forgotPasswordFormContainer:', forgotPasswordFormContainer);
    console.log('forgotPasswordTrigger:', forgotPasswordTrigger);
    console.log('backToLoginTrigger:', backToLoginTrigger);

    // Chuyển đổi từ form Đăng nhập sang Quên mật khẩu
    if (forgotPasswordTrigger && loginFormContainer && forgotPasswordFormContainer) {
        forgotPasswordTrigger.addEventListener('click', (e) => {
            e.preventDefault();
            console.log('Link "Quên mật khẩu" đã được click. Chuyển đổi form...');
            loginFormContainer.style.display = 'none';
            forgotPasswordFormContainer.style.display = 'block';
            console.log('Đã chuyển đổi thành công.');
        });
    } else {
        console.error('Không thể thiết lập sự kiện click cho "Quên mật khẩu?". Một trong các phần tử sau không tồn tại: forgotPasswordTrigger, loginFormContainer, forgotPasswordFormContainer.');
    }

    // Quay lại form Đăng nhập từ form Quên mật khẩu
    if (backToLoginTrigger && forgotPasswordFormContainer && loginFormContainer) {
        backToLoginTrigger.addEventListener('click', (e) => {
            e.preventDefault();
            console.log('Link "Quay lại đăng nhập" đã được click. Quay lại form đăng nhập...');
            forgotPasswordFormContainer.style.display = 'none';
            loginFormContainer.style.display = 'block';
            console.log('Đã quay lại thành công.');
        });
    } else {
        console.error('Không thể thiết lập sự kiện click cho "Quay lại đăng nhập". Một trong các phần tử sau không tồn tại: backToLoginTrigger, forgotPasswordFormContainer, loginFormContainer.');
    }

    // Xử lý logic đăng nhập
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            console.log('Form đăng nhập đã được submit.');
            const phoneNumber = document.getElementById('modalPhone').value;
            const password = document.getElementById('modalPassword').value;

            if (!phoneNumber || !password) {
                alert('Vui lòng nhập đầy đủ số điện thoại và mật khẩu.');
                return;
            }

            const apiUrl = 'https://buddyskincare.pythonanywhere.com/auth/login/';
            const data = {
                phone_number: phoneNumber,
                password: password
            };

            try {
                const response = await fetch(apiUrl, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(data)
                });

                if (response.ok) {
                    const result = await response.json();
                    console.log('Đăng nhập bằng số điện thoại thành công:', result);
                    saveLoginState(result);
                    alert('Đăng nhập thành công!');
                    window.location.href = '/';
                } else {
                    const error = await response.json();
                    console.error('Đăng nhập thất bại:', error);
                    alert(`Đăng nhập thất bại: ${error.detail || 'Có lỗi xảy ra.'}`);
                }
            } catch (error) {
                console.error('Lỗi khi gửi yêu cầu:', error);
                alert('Có lỗi khi kết nối đến máy chủ. Vui lòng thử lại sau.');
            }
        });
    }

    // Xử lý logic quên mật khẩu
    if (forgotForm) {
        forgotForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            console.log('Form quên mật khẩu đã được submit.');
            const email = document.getElementById('modalEmail').value;

            if (!email) {
                alert('Vui lòng nhập địa chỉ email.');
                return;
            }

            const apiUrl = 'https://buddyskincare.pythonanywhere.com/users/forgot-password/';
            const data = {
                email: email
            };

            try {
                const response = await fetch(apiUrl, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(data)
                });

                if (response.ok) {
                    const result = await response.json();
                    alert(result.detail || 'Một mã đặt lại mật khẩu đã được gửi đến email của bạn.');
                } else {
                    const error = await response.json();
                    alert(`Gửi yêu cầu thất bại: ${error.detail || 'Có lỗi xảy ra.'}`);
                }
            } catch (error) {
                console.error('Lỗi khi gửi yêu cầu quên mật khẩu:', error);
                alert('Có lỗi khi kết nối đến máy chủ. Vui lòng thử lại sau.');
            }
        });
    }
});

// Hàm xử lý đăng nhập Google
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