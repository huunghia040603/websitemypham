// search.js

document.addEventListener('DOMContentLoaded', () => {
    const desktopSearchInput = document.querySelector('.search-pill.w-130 input');
    const mobileSearchInput = document.querySelector('#mobileNavbar .search-pill input');
    const mobileSearchButton = document.querySelector('#mobileNavbar .search-pill .btn-icon');
    
    // Gắn sự kiện lắng nghe cho cả hai ô tìm kiếm và nút tìm kiếm trên mobile
    if (desktopSearchInput) {
        desktopSearchInput.addEventListener('keypress', (event) => {
            if (event.key === 'Enter') {
                event.preventDefault();
                const searchTerm = desktopSearchInput.value.trim();
                if (searchTerm) {
                    performSearch(searchTerm);
                }
            }
        });
    }

    if (mobileSearchInput) {
        mobileSearchInput.addEventListener('keypress', (event) => {
            if (event.key === 'Enter') {
                event.preventDefault();
                const searchTerm = mobileSearchInput.value.trim();
                if (searchTerm) {
                    performSearch(searchTerm);
                }
            }
        });
    }

    if (mobileSearchButton) {
        mobileSearchButton.addEventListener('click', (event) => {
            event.preventDefault();
            const searchTerm = mobileSearchInput.value.trim();
            if (searchTerm) {
                performSearch(searchTerm);
            }
        });
    }

    /**
     * Thực hiện tìm kiếm sản phẩm thông qua API.
     * @param {string} searchTerm - Từ khóa cần tìm.
     */
    async function performSearch(searchTerm) {
        const url = `https://buddyskincare.vn/backend/api/products/?search=${encodeURIComponent(searchTerm)}`;
        console.log('Searching for:', searchTerm);
        
        try {
            const response = await fetch(url);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            console.log('Search results:', data);
            
            displayResults(data);
        } catch (error) {
            console.error('Error fetching search data:', error);
            alert('Đã xảy ra lỗi khi tìm kiếm sản phẩm.');
        }
    }

    /**
     * Hiển thị kết quả tìm kiếm (ví dụ đơn giản: chuyển hướng đến trang kết quả).
     * @param {array} products - Mảng dữ liệu sản phẩm trả về từ API.
     */
    function displayResults(products) {
        // Tùy chỉnh cách bạn muốn hiển thị kết quả.
        // Ví dụ này sẽ đơn giản là chuyển hướng đến một trang kết quả.
        // Trong thực tế, bạn có thể muốn tạo một modal, một danh sách dropdown,
        // hoặc render các thẻ sản phẩm ngay trên trang.
        
        // Giả sử bạn có một trang `/search-results.html` để hiển thị.
        // localStorage.setItem('searchResults', JSON.stringify(products));
        // window.location.href = '/search-results.html';

        // Ví dụ: Hiển thị một thông báo đơn giản nếu tìm thấy sản phẩm.
        if (products && products.length > 0) {
            const firstProductName = products[0].name;
            alert(`Tìm thấy ${products.length} sản phẩm. Ví dụ: ${firstProductName}`);
            // Ở đây, bạn sẽ thêm code để render UI thực tế.
        } else {
            alert('Không tìm thấy sản phẩm nào phù hợp.');
        }
    }
});