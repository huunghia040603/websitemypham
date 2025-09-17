document.addEventListener('DOMContentLoaded', function() {
    const registerForm = document.getElementById('registerForm');
    const registerFormContainer = document.getElementById('registerFormContainer');
    const loginFormContainer = document.getElementById('loginFormContainer');
    const backToLoginLink = document.getElementById('backToLoginFromRegister');

    if (registerForm) {
        registerForm.addEventListener('submit', function(event) {
            event.preventDefault(); // Ngăn chặn hành vi gửi form mặc định

            // Lấy giá trị từ các trường input
            const name = document.getElementById('regName').value;
            const phoneNumber = document.getElementById('regPhone').value;
            const password = document.getElementById('regPassword').value;
            const email = document.getElementById('regEmail').value;

            // Tạo đối tượng body JSON
            const data = {
                name: name,
                phone_number: phoneNumber,
                password: password,
                email: email
            };

            // URL của API đăng ký
            const registerApiUrl = 'https://buddyskincare.vn/backend/api/auth/register/';

            // Gửi yêu cầu POST đến API
            fetch(registerApiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data),
            })
            .then(response => {
                // Đọc cả phản hồi thành công và thất bại dưới dạng JSON
                return response.json().then(data => ({
                    status: response.status,
                    ok: response.ok,
                    data: data
                }));
            })
            .then(({ status, ok, data }) => {
                if (ok) {
                    // Xử lý khi đăng ký thành công
                    console.log('Đăng ký thành công:', data);
                    alert('Đăng ký thành công! Bạn có thể đăng nhập ngay bây giờ.');

                    // Tự động chuyển về form đăng nhập
                    if (registerFormContainer && loginFormContainer) {
                        registerFormContainer.style.display = 'none';
                        loginFormContainer.style.display = 'block';
                    }
                } else {
                    // Xử lý khi có lỗi từ server (status không phải 2xx)
                    console.error('Lỗi khi đăng ký:', data);
                    let errorMessage = 'Đã có lỗi xảy ra. Vui lòng thử lại.';
                    
                    if (data.phone_number) {
                        errorMessage = data.phone_number.join(' ');
                    } else if (data.email) {
                        errorMessage = data.email.join(' ');
                    } else if (data.password) {
                        errorMessage = data.password.join(' ');
                    } else if (data.non_field_errors) {
                        errorMessage = data.non_field_errors.join(' ');
                    } else if (data.detail) {
                        errorMessage = data.detail;
                    } else {
                        errorMessage = JSON.stringify(data);
                    }
                    alert('Lỗi: ' + errorMessage);
                }
            })
            .catch(error => {
                // Xử lý lỗi mạng (ví dụ: không thể kết nối đến server)
                console.error('Lỗi mạng hoặc không xác định:', error);
                alert('Lỗi kết nối đến máy chủ. Vui lòng kiểm tra kết nối internet và thử lại.');
            });
        });
    }

    // Xử lý chuyển đổi giữa các form (Đăng ký -> Đăng nhập)
    if (backToLoginLink) {
        backToLoginLink.addEventListener('click', function(event) {
            event.preventDefault();
            if (registerFormContainer && loginFormContainer) {
                registerFormContainer.style.display = 'none';
                loginFormContainer.style.display = 'block';
            }
        });
    }
});