document.addEventListener('DOMContentLoaded', () => {

    // Kiểm tra trạng thái đăng nhập
   if (typeof isLoggedIn !== 'undefined' && isLoggedIn()) {
        const userProfile = getUserProfile();
        const userName = userProfile.name || userProfile.phone_number;
        const token = userProfile.access_token;

        // BẮT ĐẦU CẬP NHẬT GIAO DIỆN TRƯỚC
        
        // Cập nhật Top Bar
        const topBarUserSection = document.getElementById('top-bar-user-section');
        if (topBarUserSection) {
            topBarUserSection.innerHTML = `
                <a href="/news" class="text-decoration-none text-muted me-3">Blog làm đẹp</a>
                <a href="/support" class="text-decoration-none text-muted me-3">Hỗ trợ - Giải đáp</a>
                <span class="text-muted fw-bold me-2">Xin chào, ${userName}</span>
                <a href="#" class="text-decoration-none text-muted me-3" id="logoutBtnTopBar">Đăng xuất</a>
            `;
        }

        // Cập nhật Desktop User Dropdown
        const desktopUserDropdown = document.getElementById('desktop-user-dropdown');
        if (desktopUserDropdown) {
            desktopUserDropdown.innerHTML = `
                <a href="#" class="text-dark text-decoration-none user-dropdown-toggle" data-bs-toggle="dropdown" aria-expanded="false">
                    <i class="fas fa-user user-icon me-1"></i>
                </a>
                <ul class="dropdown-menu user-dropdown">
                    <li><a class="dropdown-item" href="/profile"><i class="fas fa-user-cog me-2"></i>Tài khoản của tôi</a></li>
                    <li><a class="dropdown-item" href="#"><i class="fas fa-heart me-2"></i>Sản phẩm yêu thích</a></li>
                    <li><a class="dropdown-item" href="#"><i class="fas fa-history me-2"></i>Lịch sử đơn hàng</a></li>
                    <li><a class="dropdown-item" href="#" id="logoutBtnDesktop"><i class="fas fa-sign-out-alt me-2"></i>Đăng xuất</a></li>
                </ul>
            `;
        }

        // Cập nhật Mobile User Dropdown
        const mobileUserDropdown = document.getElementById('mobile-user-dropdown');
        if (mobileUserDropdown) {
            mobileUserDropdown.innerHTML = `
                <a href="#" class="text-dark text-decoration-none user-dropdown-toggle" data-bs-toggle="dropdown" aria-expanded="false">
                    <i class="fas fa-user user-icon me-1"></i>
                    ${userName}
                </a>
                <ul class="dropdown-menu user-dropdown">
                    <li><a class="dropdown-item" href="/profile"><i class="fas fa-user-cog me-2"></i>Tài khoản của tôi</a></li>
                    <li><a class="dropdown-item" href="#"><i class="fas fa-heart me-2"></i>Sản phẩm yêu thích</a></li>
                    <li><a class="dropdown-item" href="#"><i class="fas fa-history me-2"></i>Lịch sử đơn hàng</a></li>
                    <li><a class="dropdown-item" href="#" id="logoutBtnMobile"><i class="fas fa-sign-out-alt me-2"></i>Đăng xuất</a></li>
                </ul>
            `;
        }

        // Gắn sự kiện đăng xuất cho các nút
        const logoutButtons = document.querySelectorAll('#logoutBtnTopBar, #logoutBtnDesktop, #logoutBtnMobile');
        logoutButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                logout();
                window.location.reload(); 
            });
        });
        
    
    }
});