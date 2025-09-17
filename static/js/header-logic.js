// document.addEventListener('DOMContentLoaded', () => {

//     // Kiểm tra trạng thái đăng nhập
//    if (typeof isLoggedIn !== 'undefined' && isLoggedIn()) {
//         const userProfile = getUserProfile();
//         const userName = userProfile.name || "";
//         const token = userProfile.access_token;

//         // BẮT ĐẦU CẬP NHẬT GIAO DIỆN TRƯỚC
        
//         // Cập nhật Top Bar
//         const topBarUserSection = document.getElementById('top-bar-user-section');
//         if (topBarUserSection) {
//             topBarUserSection.innerHTML = `
//                 <a href="/news" class="text-decoration-none text-muted me-3">Blog làm đẹp</a>
//                 <a href="/support" class="text-decoration-none text-muted me-3">Hỗ trợ - Giải đáp</a>
//                 <span class="text-muted fw-bold me-2">Xin chào, ${userName}</span>
//                 <a href="#" class="text-decoration-none text-muted me-3" id="logoutBtnTopBar">Đăng xuất</a>
//             `;
//         }

//         // Cập nhật Desktop User Dropdown
//         const desktopUserDropdown = document.getElementById('desktop-user-dropdown');
//         if (desktopUserDropdown) {
//             desktopUserDropdown.innerHTML = `
//                 <a href="#" class="text-dark text-decoration-none user-dropdown-toggle" data-bs-toggle="dropdown" aria-expanded="false">
//                     <i class="fas fa-user user-icon me-1"></i>
//                 </a>
//                 <ul class="dropdown-menu user-dropdown">
//                     <li><a class="dropdown-item" href="/profile"><i class="fas fa-user-cog me-2"></i>Tài khoản của tôi</a></li>
//                     <li><a class="dropdown-item" href="#"><i class="fas fa-heart me-2"></i>Sản phẩm yêu thích</a></li>
//                     <li><a class="dropdown-item" href="#"><i class="fas fa-history me-2"></i>Lịch sử đơn hàng</a></li>
//                     <li><a class="dropdown-item" href="#" id="logoutBtnDesktop"><i class="fas fa-sign-out-alt me-2"></i>Đăng xuất</a></li>
//                 </ul>
//             `;
//         }

//         // Cập nhật Mobile User Dropdown
//         const mobileUserDropdown = document.getElementById('mobile-user-dropdown');
//         if (mobileUserDropdown) {
//             mobileUserDropdown.innerHTML = `
//                 <a href="#" class="text-dark text-decoration-none user-dropdown-toggle" data-bs-toggle="dropdown" aria-expanded="false">
//                     <i class="fas fa-user user-icon"></i>
//                 </a>
//                 <ul class="dropdown-menu user-dropdown">
//                     <li><a class="dropdown-item" href="/profile"><i class="fas fa-user-cog me-2"></i>Tài khoản của tôi</a></li>
//                     <li><a class="dropdown-item" href="#"><i class="fas fa-heart me-2"></i>Sản phẩm yêu thích</a></li>
//                     <li><a class="dropdown-item" href="#"><i class="fas fa-history me-2"></i>Lịch sử đơn hàng</a></li>
//                     <li><a class="dropdown-item" href="#" id="logoutBtnMobile"><i class="fas fa-sign-out-alt me-2"></i>Đăng xuất</a></li>
//                 </ul>
//             `;
//         }

//         // Gắn sự kiện đăng xuất cho các nút
//         const logoutButtons = document.querySelectorAll('#logoutBtnTopBar, #logoutBtnDesktop, #logoutBtnMobile');
//         logoutButtons.forEach(button => {
//             button.addEventListener('click', (e) => {
//                 e.preventDefault();
//                 logout();
//                 window.location.reload(); 
//             });
//         });
        
    
//     }

//     // Handle nav-search visibility and redirection
//     initNavSearchLogic();
    
//     // Re-check nav-search visibility when navigating (for SPA-like behavior)
//     window.addEventListener('popstate', initNavSearchLogic);
// });

// function initNavSearchLogic() {
//     const isProductsPage = window.location.pathname.includes('/products');
    
//     // Hide nav-search on products page
//     const navSearchContainer = document.getElementById('nav-search-container');
//     const mobileNavSearchContainer = document.getElementById('mobile-nav-search-container');
    
//     console.log('🔍 Nav Search Logic:', {
//         currentPath: window.location.pathname,
//         isProductsPage: isProductsPage,
//         navSearchContainer: !!navSearchContainer,
//         mobileNavSearchContainer: !!mobileNavSearchContainer
//     });
    
//     if (isProductsPage) {
//         // Add products-page class to body for CSS targeting
//         document.body.classList.add('products-page');
        
//         if (navSearchContainer) {
//             navSearchContainer.style.display = 'none';
//             console.log('✅ Hidden desktop nav-search');
//         }
//         if (mobileNavSearchContainer) {
//             mobileNavSearchContainer.style.display = 'none';
//             console.log('✅ Hidden mobile nav-search');
//         }
//     } else {
//         // Remove products-page class from body
//         document.body.classList.remove('products-page');
        
//         if (navSearchContainer) {
//             navSearchContainer.style.display = 'flex';
//             console.log('✅ Shown desktop nav-search');
//         }
//         if (mobileNavSearchContainer) {
//             mobileNavSearchContainer.style.display = 'block';
//             console.log('✅ Shown mobile nav-search');
//         }
        
//         // Setup search redirection for non-products pages
//         setupSearchRedirection();
//     }
// }

// function setupSearchRedirection() {
//     const navSearchInput = document.getElementById('nav-search-input');
//     const mobileNavSearchInput = document.getElementById('mobile-nav-search-input');
//     const mobileSearchBtn = document.getElementById('mobile-search-btn');
//     const navSearchSuggestions = document.getElementById('nav-search-suggestions');
//     const mobileNavSearchSuggestions = document.getElementById('mobile-nav-search-suggestions');
    
//     let allProducts = [];
//     let searchTimeout;
    
//     // Load products for search suggestions
    //     fetch('https://buddyskincare.vn/backend/api/products/')
//         .then(r => r.ok ? r.json() : [])
//         .then(products => {
//             allProducts = products || [];
//         })
//         .catch(() => {});
    
//     function redirectToProducts(query) {
//         if (query.trim()) {
//             window.location.href = `/products?search=${encodeURIComponent(query.trim())}`;
//         }
//     }
    
//     function performNavSearch(query, suggestionsDiv) {
//         const results = searchProducts(query, allProducts);
//         showNavSuggestions(results, query, suggestionsDiv);
//     }
    
//     function searchProducts(query, products) {
//         const lowerQuery = query.toLowerCase();
//         const results = [];

//         products.forEach(product => {
//             const name = (product.name || '').toLowerCase();
//             const brand = (product.brand_name || '').toLowerCase();
//             const category = (product.category_name || '').toLowerCase();
//             const tags = (product.tags || []).map(tag => 
//                 typeof tag === 'string' ? tag.toLowerCase() : (tag.name || '').toLowerCase()
//             );

//             let score = 0;
//             let matchType = '';

//             // Exact name match (highest priority)
//             if (name.includes(lowerQuery)) {
//                 score += 100;
//                 matchType = 'name';
//             }
//             // Brand match
//             else if (brand.includes(lowerQuery)) {
//                 score += 80;
//                 matchType = 'brand';
//             }
//             // Category match
//             else if (category.includes(lowerQuery)) {
//                 score += 60;
//                 matchType = 'category';
//             }
//             // Tags match
//             else if (tags.some(tag => tag.includes(lowerQuery))) {
//                 score += 40;
//                 matchType = 'tag';
//             }

//             if (score > 0) {
//                 results.push({
//                     product,
//                     score,
//                     matchType
//                 });
//             }
//         });

//         // Sort by score and return top 6 results
//         return results
//             .sort((a, b) => b.score - a.score)
//             .slice(0, 6);
//     }
    
//     function showNavSuggestions(results, query, suggestionsDiv) {
//         if (results.length === 0) {
//             hideNavSuggestions(suggestionsDiv);
//             return;
//         }

//         let html = '';
//         results.forEach(result => {
//             const { product, matchType } = result;
//             const imageUrl = product.image || '/static/image/default-product.jpg';
//             const price = product.discounted_price ? (product.discounted_price * 1000).toLocaleString('vi-VN') : 'N/A';
            
//             html += `
//                 <div class="suggestion-item p-2 border-bottom" style="cursor: pointer;" data-product-id="${product.id}">
//                     <div class="d-flex align-items-center">
//                         <img src="${imageUrl}" alt="${product.name}" style="width: 40px; height: 40px; object-fit: cover; border-radius: 4px; margin-right: 10px;">
//                         <div class="flex-grow-1">
//                             <div class="fw-bold" style="font-size: 14px;">${product.name}</div>
//                             <div class="text-muted" style="font-size: 12px;">
//                                 ${product.brand_name || 'N/A'} • ${price}đ
//                             </div>
//                         </div>
                        
//                     </div>
//                 </div>
//             `;
//         });

//         // Add "Tìm kiếm tất cả" option
//         html += `
//             <div class="suggestion-item p-2 text-center bg-light" style="cursor: pointer;" data-search-all="true">
//                 <i class="fas fa-search me-2"></i>Tìm kiếm tất cả cho "${query}"
//             </div>
//         `;

//         suggestionsDiv.innerHTML = html;
//         suggestionsDiv.style.display = 'block';

//         // Add click handlers
//         suggestionsDiv.querySelectorAll('.suggestion-item').forEach(item => {
//             item.addEventListener('click', function() {
//                 if (this.dataset.searchAll === 'true') {
//                     redirectToProducts(query);
//                 } else {
//                     const productId = this.dataset.productId;
//                     window.location.href = `/product/${productId}`;
//                 }
//             });

//             // Hover effect
//             item.addEventListener('mouseenter', function() {
//                 this.style.backgroundColor = '#f8f9fa';
//             });
//             item.addEventListener('mouseleave', function() {
//                 this.style.backgroundColor = this.dataset.searchAll === 'true' ? '#f8f9fa' : 'white';
//             });
//         });
//     }
    
//     function hideNavSuggestions(suggestionsDiv) {
//         suggestionsDiv.style.display = 'none';
//     }
    
//     // Desktop search
//     if (navSearchInput) {
//         navSearchInput.addEventListener('input', function(e) {
//             const query = e.target.value.trim();
            
//             clearTimeout(searchTimeout);
            
//             if (query.length < 2) {
//                 hideNavSuggestions(navSearchSuggestions);
//                 return;
//             }

//             searchTimeout = setTimeout(() => {
//                 performNavSearch(query, navSearchSuggestions);
//             }, 300);
//         });
        
//         navSearchInput.addEventListener('keydown', function(e) {
//             if (e.key === 'Enter') {
//                 e.preventDefault();
//                 redirectToProducts(this.value);
//             } else if (e.key === 'Escape') {
//                 hideNavSuggestions(navSearchSuggestions);
//             }
//         });
//     }
    
//     // Mobile search
//     if (mobileNavSearchInput) {
//         mobileNavSearchInput.addEventListener('input', function(e) {
//             const query = e.target.value.trim();
            
//             clearTimeout(searchTimeout);
            
//             if (query.length < 2) {
//                 hideNavSuggestions(mobileNavSearchSuggestions);
//                 return;
//             }

//             searchTimeout = setTimeout(() => {
//                 performNavSearch(query, mobileNavSearchSuggestions);
//             }, 300);
//         });
        
//         mobileNavSearchInput.addEventListener('keydown', function(e) {
//             if (e.key === 'Enter') {
//                 e.preventDefault();
//                 redirectToProducts(this.value);
//             } else if (e.key === 'Escape') {
//                 hideNavSuggestions(mobileNavSearchSuggestions);
//             }
//         });
//     }
    
//     if (mobileSearchBtn) {
//         mobileSearchBtn.addEventListener('click', function(e) {
//             e.preventDefault();
//             if (mobileNavSearchInput) {
//                 redirectToProducts(mobileNavSearchInput.value);
//             }
//         });
//     }
    
//     // Hide suggestions when clicking outside
//     document.addEventListener('click', function(e) {
//         if (navSearchInput && !navSearchInput.contains(e.target) && !navSearchSuggestions.contains(e.target)) {
//             hideNavSuggestions(navSearchSuggestions);
//         }
//         if (mobileNavSearchInput && !mobileNavSearchInput.contains(e.target) && !mobileNavSearchSuggestions.contains(e.target)) {
//             hideNavSuggestions(mobileNavSearchSuggestions);
//         }
//     });
// }

document.addEventListener('DOMContentLoaded', () => {

    // Hàm cập nhật giao diện header sau khi đăng nhập thành công
    function updateHeaderForLoggedInUser() {
        const userProfile = getUserProfile();
        if (!userProfile) return;

        const userName = userProfile.name || "";
        const topBarUserSection = document.getElementById('top-bar-user-section');
        const desktopUserDropdown = document.getElementById('desktop-user-dropdown');
        const mobileUserDropdown = document.getElementById('mobile-user-dropdown');

        // Cập nhật Top Bar
        if (topBarUserSection) {
            topBarUserSection.innerHTML = `
                <a href="/news" class="text-decoration-none text-muted me-3">Blog làm đẹp</a>
                <a href="/support" class="text-decoration-none text-muted me-3">Hỗ trợ - Giải đáp</a>
                <span class="text-muted fw-bold me-2">Xin chào, ${userName}</span>
                <a href="#" class="text-decoration-none text-muted me-3" id="logoutBtnTopBar">Đăng xuất</a>
            `;
        }

        // Cập nhật Desktop User Dropdown
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
        if (mobileUserDropdown) {
            mobileUserDropdown.innerHTML = `
                <a href="#" class="text-dark text-decoration-none user-dropdown-toggle" data-bs-toggle="dropdown" aria-expanded="false">
                    <i class="fas fa-user user-icon"></i>
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

    // Kiểm tra và cập nhật giao diện khi tải trang
    if (typeof isLoggedIn !== 'undefined' && isLoggedIn()) {
        updateHeaderForLoggedInUser();
    }

    // Handle nav-search visibility and redirection
    initNavSearchLogic();
    
    // Re-check nav-search visibility when navigating (for SPA-like behavior)
    window.addEventListener('popstate', initNavSearchLogic);

    // Make the updateHeaderForLoggedInUser function globally accessible
    window.updateHeaderForLoggedInUser = updateHeaderForLoggedInUser;
});

function initNavSearchLogic() {
    const isProductsPage = window.location.pathname.includes('/products');
    const navSearchContainer = document.getElementById('nav-search-container');
    const mobileNavSearchContainer = document.getElementById('mobile-nav-search-container');
    
    if (isProductsPage) {
        document.body.classList.add('products-page');
        if (navSearchContainer) navSearchContainer.style.display = 'none';
        if (mobileNavSearchContainer) mobileNavSearchContainer.style.display = 'none';
    } else {
        document.body.classList.remove('products-page');
        if (navSearchContainer) navSearchContainer.style.display = 'flex';
        if (mobileNavSearchContainer) mobileNavSearchContainer.style.display = 'block';
        setupSearchRedirection();
    }
}

function setupSearchRedirection() {
    const navSearchInput = document.getElementById('nav-search-input');
    const mobileNavSearchInput = document.getElementById('mobile-nav-search-input');
    const mobileSearchBtn = document.getElementById('mobile-search-btn');
    const navSearchSuggestions = document.getElementById('nav-search-suggestions');
    const mobileNavSearchSuggestions = document.getElementById('mobile-nav-search-suggestions');
    
    let allProducts = [];
    let searchTimeout;
    
        fetch('https://buddyskincare.vn/backend/api/products/')
        .then(r => r.ok ? r.json() : [])
        .then(products => { allProducts = products || []; })
        .catch(() => {});
    
    function redirectToProducts(query) {
        if (query.trim()) {
            window.location.href = `/products?search=${encodeURIComponent(query.trim())}`;
        }
    }
    
    function performNavSearch(query, suggestionsDiv) {
        const results = searchProducts(query, allProducts);
        showNavSuggestions(results, query, suggestionsDiv);
    }
    
    function searchProducts(query, products) {
        const lowerQuery = query.toLowerCase();
        const results = [];

        products.forEach(product => {
            const name = (product.name || '').toLowerCase();
            const brand = (product.brand_name || '').toLowerCase();
            const category = (product.category_name || '').toLowerCase();
            const tags = (product.tags || []).map(tag => 
                typeof tag === 'string' ? tag.toLowerCase() : (tag.name || '').toLowerCase()
            );

            let score = 0;
            let matchType = '';

            if (name.includes(lowerQuery)) {
                score += 100;
                matchType = 'name';
            }
            else if (brand.includes(lowerQuery)) {
                score += 80;
                matchType = 'brand';
            }
            else if (category.includes(lowerQuery)) {
                score += 60;
                matchType = 'category';
            }
            else if (tags.some(tag => tag.includes(lowerQuery))) {
                score += 40;
                matchType = 'tag';
            }

            if (score > 0) {
                results.push({
                    product,
                    score,
                    matchType
                });
            }
        });

        return results
            .sort((a, b) => b.score - a.score)
            .slice(0, 6);
    }
    
    function showNavSuggestions(results, query, suggestionsDiv) {
        if (results.length === 0) {
            hideNavSuggestions(suggestionsDiv);
            return;
        }

        let html = '';
        results.forEach(result => {
            const { product } = result;
            const imageUrl = product.image || '/static/image/default-product.jpg';
            const price = product.discounted_price ? (product.discounted_price * 1000).toLocaleString('vi-VN') : 'N/A';
            
            html += `
                <div class="suggestion-item p-2 border-bottom" style="cursor: pointer;" data-product-id="${product.id}">
                    <div class="d-flex align-items-center">
                        <img src="${imageUrl}" alt="${product.name}" style="width: 40px; height: 40px; object-fit: cover; border-radius: 4px; margin-right: 10px;">
                        <div class="flex-grow-1">
                            <div class="fw-bold" style="font-size: 14px;">${product.name}</div>
                            <div class="text-muted" style="font-size: 12px;">
                                ${product.brand_name || 'N/A'} • ${price}đ
                            </div>
                        </div>
                    </div>
                </div>
            `;
        });

        html += `
            <div class="suggestion-item p-2 text-center bg-light" style="cursor: pointer;" data-search-all="true">
                <i class="fas fa-search me-2"></i>Tìm kiếm tất cả cho "${query}"
            </div>
        `;

        suggestionsDiv.innerHTML = html;
        suggestionsDiv.style.display = 'block';

        suggestionsDiv.querySelectorAll('.suggestion-item').forEach(item => {
            item.addEventListener('click', function() {
                if (this.dataset.searchAll === 'true') {
                    redirectToProducts(query);
                } else {
                    const productId = this.dataset.productId;
                    window.location.href = `/product/${productId}`;
                }
            });

            item.addEventListener('mouseenter', function() { this.style.backgroundColor = '#f8f9fa'; });
            item.addEventListener('mouseleave', function() { this.style.backgroundColor = this.dataset.searchAll === 'true' ? '#f8f9fa' : 'white'; });
        });
    }
    
    function hideNavSuggestions(suggestionsDiv) {
        suggestionsDiv.style.display = 'none';
    }
    
    if (navSearchInput) {
        navSearchInput.addEventListener('input', function(e) {
            const query = e.target.value.trim();
            clearTimeout(searchTimeout);
            if (query.length < 2) { hideNavSuggestions(navSearchSuggestions); return; }
            searchTimeout = setTimeout(() => { performNavSearch(query, navSearchSuggestions); }, 300);
        });
        navSearchInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') { e.preventDefault(); redirectToProducts(this.value); }
            else if (e.key === 'Escape') { hideNavSuggestions(navSearchSuggestions); }
        });
    }
    
    if (mobileNavSearchInput) {
        mobileNavSearchInput.addEventListener('input', function(e) {
            const query = e.target.value.trim();
            clearTimeout(searchTimeout);
            if (query.length < 2) { hideNavSuggestions(mobileNavSearchSuggestions); return; }
            searchTimeout = setTimeout(() => { performNavSearch(query, mobileNavSearchSuggestions); }, 300);
        });
        mobileNavSearchInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') { e.preventDefault(); redirectToProducts(this.value); }
            else if (e.key === 'Escape') { hideNavSuggestions(mobileNavSearchSuggestions); }
        });
    }
    
    if (mobileSearchBtn) {
        mobileSearchBtn.addEventListener('click', function(e) {
            e.preventDefault();
            if (mobileNavSearchInput) { redirectToProducts(mobileNavSearchInput.value); }
        });
    }
    
    document.addEventListener('click', function(e) {
        if (navSearchInput && !navSearchInput.contains(e.target) && !navSearchSuggestions.contains(e.target)) {
            hideNavSuggestions(navSearchSuggestions);
        }
        if (mobileNavSearchInput && !mobileNavSearchInput.contains(e.target) && !mobileNavSearchSuggestions.contains(e.target)) {
            hideNavSuggestions(mobileNavSearchSuggestions);
        }
    });
}