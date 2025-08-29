// Hàm lưu trữ thông tin đăng nhập sau khi đăng nhập thành công
function saveLoginState(data) {
    try {
        // Lưu trữ toàn bộ dữ liệu người dùng (trừ mật khẩu và refresh token)
        const userProfile = {
            access_token: data.access_token,
            phone_number: data.phone_number,
            name: data.name,
            address: data.address,
            dob: data.dob,
            email: data.email
        };
        localStorage.setItem('userProfile', JSON.stringify(userProfile));
        localStorage.setItem('isLoggedIn', 'true');
        // Lưu refresh token riêng để bảo mật và sử dụng khi cần refresh token
        localStorage.setItem('refreshToken', data.refresh_token);
        console.log('Thông tin người dùng và trạng thái đăng nhập đã được lưu.');
    } catch (error) {
        console.error('Lỗi khi lưu trữ thông tin đăng nhập:', error);
    }
}

// Hàm lấy access token
function getAccessToken() {
    const userProfile = localStorage.getItem('userProfile');
    return userProfile ? JSON.parse(userProfile).access_token : null;
}

// Hàm lấy refresh token
function getRefreshToken() {
    return localStorage.getItem('refreshToken');
}

// Hàm lấy thông tin người dùng
function getUserProfile() {
    const userProfile = localStorage.getItem('userProfile');
    return userProfile ? JSON.parse(userProfile) : null;
}

// Hàm kiểm tra trạng thái đăng nhập
function isLoggedIn() {
    return localStorage.getItem('isLoggedIn') === 'true' && !!getAccessToken();
}

// Hàm đăng xuất
function logout() {
    localStorage.removeItem('userProfile');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('isLoggedIn');
    console.log('Tất cả thông tin đăng nhập đã được xóa.');
}