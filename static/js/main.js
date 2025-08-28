
// // Main JavaScript for BeautySale Website

// document.addEventListener('DOMContentLoaded', function() {
//     // Initialize all components
//     initCountdownTimer();
//     initScrollToTop();
//     initProductCards();
//     initNewsletterForm();
//     initAnimations();
//     initMobileMenu();
//     initCartQuantityControls();
//     initCartBadgeZero();
//     initSearch();
//     initLazyLoading();
//     initSmoothScrolling();
//     initDynamicProducts(); // Thêm hàm mới vào đây

//     // Ensure modal dismiss buttons always work
//     document.addEventListener('click', function(e) {
//         const dismissBtn = e.target.closest('[data-bs-dismiss="modal"]');
//         if (!dismissBtn) return;
//         const modalEl = dismissBtn.closest('.modal');
//         if (modalEl && window.bootstrap) {
//             try {
//                 const instance = bootstrap.Modal.getOrCreateInstance(modalEl);
//                 instance.hide();
//             } catch (err) {
//                 // ignore
//             }
//         }
//     });
// });

// // --- Dynamic Products Section ---

// // URL của API
// const API_URL = 'https://buddyskincare.pythonanywhere.com/products/';

// // Container chứa các sản phẩm
// const productsContainer = document.querySelector('.homepage-products');

// // Chức năng làm sạch container
// function clearProductsContainer() {
//     if (productsContainer) {
//         productsContainer.innerHTML = '';
//     }
// }

// // Hàm định dạng giá tiền với dấu chấm
// function formatPrice(price) {
//     if (price === null || price === undefined) {
//         return 'Đang cập nhật';
//     }
//     // Chuyển đổi giá về dạng số, sau đó định dạng
//     const amount = Number(price);
//     if (isNaN(amount)) {
//         return 'Giá không hợp lệ';
//     }
//     return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(amount);
// }

// // Hàm tạo HTML cho một sản phẩm
// function createProductCard(product) {
//     // Lấy variant đầu tiên để hiển thị thông tin chính
//     const mainVariant = product.variants && product.variants.length > 0 ? product.variants[0] : null;

//     // Lấy ảnh thumbnail và xử lý trường hợp album không phải là mảng
//     // Khắc phục lỗi: Cấu trúc dữ liệu "album" là một đối tượng, không phải mảng.
//     const albumObject = product.album; 
//     const imagesArray = albumObject && Array.isArray(albumObject.images) ? albumObject.images : [];

//     const thumbnailImage = imagesArray.find(img => img.is_thumbnail)?.image;
//     const firstImage = imagesArray.length > 0 ? imagesArray[0].image : null;
//     const imageUrl = thumbnailImage || firstImage || '/static/image/default-product.jpg';

//     // Lấy thương hiệu và danh mục
//     const brandName = product.brand ? product.brand.name : 'Không rõ';
//     const categoryName = product.specific_category ? product.specific_category.name : 'Sản phẩm';

//     // Xử lý giá tiền
//     // Thay đổi cách lấy và xử lý giá tiền
// const originalPrice = mainVariant ? mainVariant.original_price * 1000 : null;
// const discountedPrice = mainVariant ? mainVariant.discounted_price * 1000 : null;
// const rating = mainVariant ? mainVariant.rating : null;
// const fullStars = Math.floor(rating);
// const hasHalfStar = rating % 1 >= 0.5 && rating % 1 < 1; // Điều kiện mới
// // Tạo HTML cho các ngôi sao
//     let starsHTML = '';
//     for (let i = 0; i < fullStars; i++) {
//         starsHTML += '<i class="fas fa-star"></i>';
//     }

//     if (hasHalfStar) {
//     starsHTML += '<i class="fas fa-star-half-alt"></i>';
// }
//     const totalStars = fullStars + (hasHalfStar ? 1 : 0);
// const emptyStars = 5 - totalStars;
// for (let i = 0; i < emptyStars; i++) {
//     starsHTML += '<i class="far fa-star"></i>';
// }
// // Đoạn code còn lại giữ nguyên
// const discountRate = (originalPrice && discountedPrice) ? Math.round(((originalPrice - discountedPrice) / originalPrice) * 100) : 0;
// const stockQuantity = mainVariant ? mainVariant.stock_quantity : 0;
// const soldQuantity = mainVariant.sold_quantity || 0; // Sử dụng sold_quantity từ product chính

// const totalStock = stockQuantity + soldQuantity;
// const progressPercentage = totalStock > 0 ? (soldQuantity / totalStock) * 100 : 0;
// const displayStockQuantity = stockQuantity > 99 ? '99+' : stockQuantity;
    
//     // Xử lý tên sản phẩm
//     const productName = product.name;

//     // Tạo thẻ HTML
//     const cardHTML = `
//         <div class="col-lg-2 col-md-6 col-6">
//             <div class="product-card card h-100 border-0 shadow-sm">
//                 <a href="/products/${product.id}" class="d-block text-decoration-none text-dark">
//                     <div class="position-relative">
//                         <img src="${imageUrl}" class="card-img-top" alt="${productName}">
//                         ${discountRate > 0 ? `<div class="badge-sale">${discountRate}%</div>` : ''}
//                     </div>
//                 </a>
//                 <div class="card-body">
//                     <a href="/products/${product.id}" class="d-block text-decoration-none text-dark">
//                         <h6 class="card-title">${productName}</h6>
//                         <p class="text-muted small">${brandName}</p>
//                     </a>
//                     <div class="d-flex align-items-center mb-2">
//                         ${originalPrice ? `<span class="text-decoration-line-through text-muted me-2 dt">${formatPrice(originalPrice)}</span>` : ''}
//                         <span class="text-danger fw-bold fs-5 dt-text">${formatPrice(discountedPrice)}</span>
//                     </div>
//                     <div class="d-flex align-items-center mb-3">
//                         <div class="stars text-warning me-2">
//                             ${starsHTML}
//                         </div>
//                         <small class="text-muted">(${rating})</small>
//                     </div>
//                     <div class="stock">
//                         <div class="progress">
//                             <div class="progress-bar" role="progressbar" style="width: ${progressPercentage}%" aria-valuenow="${progressPercentage}" aria-valuemin="0" aria-valuemax="100"></div>
//                         </div>
//                         <span class="stock-text">đã bán ${soldQuantity} sản phẩm</span>
//                     </div>
//                     <button class="btn btn-outline-primary w-100 mt-2 add-to-cart-btn" data-product-id="${product.id}">Thêm vào giỏ</button>
//                 </div>
//             </div>
//         </div>
//     `;
//     return cardHTML;
// }

// // Hàm lấy và hiển thị dữ liệu
// async function initDynamicProducts() {
//     try {
//         const response = await fetch(API_URL);
//         if (!response.ok) {
//             throw new Error('Lỗi khi lấy dữ liệu từ API');
//         }
//         const products = await response.json();
        
//         // Xóa nội dung cũ trước khi thêm mới
//         clearProductsContainer();
        
//         // Tạo HTML cho từng sản phẩm và thêm vào container
//         products.forEach(product => {
//             if (productsContainer) {
//                 productsContainer.innerHTML += createProductCard(product);
//             }
//         });

//         // Re-initialize Product Cards with new DOM elements
//         initProductCards();
//         // Re-initialize Animations with new DOM elements
//         initAnimations();

//     } catch (error) {
//         console.error('Đã xảy ra lỗi:', error);
//         if (productsContainer) {
//             productsContainer.innerHTML = '<p class="text-danger">Không thể tải dữ liệu sản phẩm. Vui lòng thử lại sau.</p>';
//         }
//     }
// }

// // --- End of Dynamic Products Section ---

// // Countdown Timer for Flash Sale
// function initCountdownTimer() {
//     const countdownElements = document.querySelectorAll('.countdown-number');
//     if (countdownElements.length === 0) return;

//     // Set target date (2 days from now)
//     const targetDate = new Date();
//     targetDate.setDate(targetDate.getDate() + 2);
//     targetDate.setHours(15, 30, 45, 0);

//     function updateCountdown() {
//         const now = new Date().getTime();
//         const distance = targetDate.getTime() - now;

//         if (distance < 0) {
//             // Countdown finished
//             countdownElements.forEach(el => el.textContent = '00');
//             return;
//         }

//         const days = Math.floor(distance / (1000 * 60 * 60 * 24));
//         const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
//         const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
//         const seconds = Math.floor((distance % (1000 * 60)) / 1000);

//         // Update display
//         if (countdownElements[0]) countdownElements[0].textContent = days.toString().padStart(2, '0');
//         if (countdownElements[1]) countdownElements[1].textContent = hours.toString().padStart(2, '0');
//         if (countdownElements[2]) countdownElements[2].textContent = minutes.toString().padStart(2, '0');
//         if (countdownElements[3]) countdownElements[3].textContent = seconds.toString().padStart(2, '0');
//     }

//     // Update countdown every second
//     updateCountdown();
//     setInterval(updateCountdown, 1000);
// }

// // Scroll to Top Button
// function initScrollToTop() {
//     // Create scroll to top button
//     const scrollButton = document.createElement('button');
//     scrollButton.className = 'scroll-to-top';
//     scrollButton.innerHTML = '<i class="fas fa-arrow-up"></i>';
//     document.body.appendChild(scrollButton);

//     // Show/hide button based on scroll position
//     window.addEventListener('scroll', function() {
//         if (window.pageYOffset > 300) {
//             scrollButton.classList.add('show');
//         } else {
//             scrollButton.classList.remove('show');
//         }
//     });

//     // Scroll to top when clicked
//     scrollButton.addEventListener('click', function() {
//         window.scrollTo({
//             top: 0,
//             behavior: 'smooth'
//         });
//     });
// }

// // Product Cards Interactions
// function initProductCards() {
//     const productCards = document.querySelectorAll('.product-card');
    
//     productCards.forEach(card => {
//         const addToCartBtn = card.querySelector('.add-to-cart-btn');
//         const productImage = card.querySelector('img');

//         if (addToCartBtn) {
//             addToCartBtn.addEventListener('click', function(e) {
//                 e.preventDefault();

//                 // Trigger fly-to-cart animation instead of loading text
//                 flyToCart(productImage, () => {
//                     updateCartCount();
//                 });
//             });
//         }
//     });
// }

// // Update Cart Count
// function updateCartCount() {
//     const cartBadges = document.querySelectorAll('.cart-badge');
//     if (cartBadges.length === 0) return;

//     cartBadges.forEach(cartBadge => {
//         const currentCount = parseInt((cartBadge.textContent || '0').trim(), 10) || 0;
//         cartBadge.textContent = currentCount + 1;

//         // Add animation
//         cartBadge.style.transform = 'scale(1.2)';
//         setTimeout(() => {
//             cartBadge.style.transform = 'scale(1)';
//         }, 200);
//     });
// }

// // Ensure cart badges show 0 on initial load when no items
// function initCartBadgeZero() {
//     const cartBadges = document.querySelectorAll('.cart-badge');
//     if (cartBadges.length === 0) return;
//     cartBadges.forEach(badge => {
//         const current = parseInt((badge.textContent || '').trim(), 10);
//         if (isNaN(current)) {
//             badge.textContent = '0';
//         }
//     });
// }

// // Fly product image to cart icon
// function flyToCart(sourceImageEl, onComplete) {
//     // Pick the visible cart icon (desktop or mobile)
//     const cartIcons = Array.from(document.querySelectorAll('.cart-icon, .fa-shopping-cart'));
//     const visibleCartIcon = cartIcons.find(icon => {
//         const rect = icon.getBoundingClientRect();
//         const style = window.getComputedStyle(icon);
//         return rect.width > 0 && rect.height > 0 && style.visibility !== 'hidden' && style.display !== 'none';
//     });

//     const cartIcon = visibleCartIcon || cartIcons[0];
//     if (!sourceImageEl || !cartIcon) {
//         if (typeof onComplete === 'function') onComplete();
//         return;
//     }

//     const imgRect = sourceImageEl.getBoundingClientRect();
//     const cartRect = cartIcon.getBoundingClientRect();

//     const flying = document.createElement('img');
//     flying.src = sourceImageEl.src;
//     flying.className = 'flying-to-cart';
//     flying.style.position = 'fixed';
//     flying.style.left = imgRect.left + 'px';
//     flying.style.top = imgRect.top + 'px';
//     flying.style.width = Math.max(60, Math.min(imgRect.width, 120)) + 'px';
//     flying.style.height = 'auto';
//     flying.style.borderRadius = '8px';
//     flying.style.zIndex = '9999';
//     flying.style.transition = 'transform 1.25s cubic-bezier(0.22, 1, 0.36, 1), opacity 1.25s ease';
//     flying.style.willChange = 'transform, opacity';
//     flying.style.opacity = '0.95';

//     document.body.appendChild(flying);

//     // Compute translate to cart center
//     const start = flying.getBoundingClientRect();
//     const targetX = cartRect.left + cartRect.width / 2 - (start.left + start.width / 2);
//     const targetY = cartRect.top + cartRect.height / 2 - (start.top + start.height / 2);

//     // Animate on next frame
//     requestAnimationFrame(() => {
//         flying.style.transform = `translate(${targetX}px, ${targetY}px) scale(0.2)`;
//         flying.style.opacity = '0.2';
//     });

//     let hasCompleted = false;
//     const cleanup = () => {
//         if (hasCompleted) return;
//         hasCompleted = true;
//         flying.remove();
//         // Brief bump on cart icon
//         cartIcon.style.transform = 'scale(1.2)';
//         setTimeout(() => {
//             cartIcon.style.transform = 'scale(1)';
//         }, 200);
//         if (typeof onComplete === 'function') onComplete();
//     };

//     flying.addEventListener('transitionend', cleanup, { once: true });
//     // Fallback cleanup
//     setTimeout(cleanup, 1700);
// }

// // Newsletter Form
// function initNewsletterForm() {
//     const newsletterForm = document.querySelector('.newsletter-section .input-group');
//     if (!newsletterForm) return;

//     const emailInput = newsletterForm.querySelector('input[type="email"]');
//     const submitBtn = newsletterForm.querySelector('button');

//     submitBtn.addEventListener('click', function(e) {
//         e.preventDefault();
        
//         const email = emailInput.value.trim();
        
//         if (!email || !isValidEmail(email)) {
//             showNotification('Vui lòng nhập email hợp lệ!', 'error');
//             return;
//         }
        
//         // Add loading state
//         const originalText = this.textContent;
//         this.innerHTML = '<span class="loading"></span> Đang đăng ký...';
//         this.disabled = true;
        
//         // Simulate API call
//         setTimeout(() => {
//             this.innerHTML = '<i class="fas fa-check"></i> Đã đăng ký!';
//             this.classList.remove('btn-light');
//             this.classList.add('btn-success');
//             emailInput.value = '';
            
//             showNotification('Đăng ký thành công! Bạn sẽ nhận được thông báo sớm nhất.', 'success');
            
//             // Reset button after 3 seconds
//             setTimeout(() => {
//                 this.innerHTML = originalText;
//                 this.classList.remove('btn-success');
//                 this.classList.add('btn-light');
//                 this.disabled = false;
//             }, 3000);
//         }, 1500);
//     });
// }

// // Email validation
// function isValidEmail(email) {
//     const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
//     return emailRegex.test(email);
// }

// // Show notification
// function showNotification(message, type = 'info') {
//     // Create notification element
//     const notification = document.createElement('div');
//     notification.className = `alert alert-${type === 'error' ? 'danger' : type === 'success' ? 'success' : 'info'} alert-dismissible fade show position-fixed`;
//     notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
//     notification.innerHTML = `
//         ${message}
//         <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
//     `;
    
//     document.body.appendChild(notification);
    
//     // Auto remove after 5 seconds
//     setTimeout(() => {
//         if (notification.parentNode) {
//             notification.remove();
//         }
//     }, 5000);
// }

// // Animations on scroll
// function initAnimations() {
//     const observerOptions = {
//         threshold: 0.1,
//         rootMargin: '0px 0px -50px 0px'
//     };

//     const observer = new IntersectionObserver(function(entries) {
//         entries.forEach(entry => {
//             if (entry.isIntersecting) {
//                 entry.target.classList.add('fade-in');
//                 observer.unobserve(entry.target);
//             }
//         });
//     }, observerOptions);

//     // Observe elements for animation
//     const animateElements = document.querySelectorAll('.product-card, .category-card, .testimonial-card');
//     animateElements.forEach(el => {
//         observer.observe(el);
//     });
// }

// // Mobile menu enhancements
// function initMobileMenu() {
//     const navbarToggler = document.querySelector('.navbar-toggler');
//     const navbarCollapse = document.querySelector('.navbar-collapse');
    
//     if (navbarToggler && navbarCollapse) {
//         // Close mobile menu when clicking on a link
//         const navLinks = navbarCollapse.querySelectorAll('.nav-link');
//         navLinks.forEach(link => {
//             link.addEventListener('click', () => {
//                 if (window.innerWidth < 992) {
//                     const bsCollapse = new bootstrap.Collapse(navbarCollapse);
//                     bsCollapse.hide();
//                 }
//             });
//         });
//     }
// }

// // Search functionality
// function initSearch() {
//     const searchInput = document.querySelector('input[placeholder*="Tìm kiếm"]');
//     if (!searchInput) return;

//     let searchTimeout;
    
//     searchInput.addEventListener('input', function() {
//         clearTimeout(searchTimeout);
        
//         searchTimeout = setTimeout(() => {
//             const query = this.value.trim();
//             if (query.length >= 2) {
//                 // Simulate search
//                 console.log('Searching for:', query);
//                 // Here you would typically make an API call
//             }
//         }, 500);
//     });
// }

// // Lazy loading for images
// function initLazyLoading() {
//     const images = document.querySelectorAll('img[data-src]');
    
//     const imageObserver = new IntersectionObserver((entries, observer) => {
//         entries.forEach(entry => {
//             if (entry.isIntersecting) {
//                 const img = entry.target;
//                 img.src = img.dataset.src;
//                 img.classList.remove('lazy');
//                 imageObserver.unobserve(img);
//             }
//         });
//     });

//     images.forEach(img => imageObserver.observe(img));
// }

// // Smooth scrolling for anchor links
// function initSmoothScrolling() {
//     const anchorLinks = document.querySelectorAll('a[href^="#"]');
    
//     anchorLinks.forEach(link => {
//         link.addEventListener('click', function(e) {
//             e.preventDefault();
            
//             const targetId = this.getAttribute('href');
//             const targetElement = document.querySelector(targetId);
            
//             if (targetElement) {
//                 targetElement.scrollIntoView({
//                     behavior: 'smooth',
//                     block: 'start'
//                 });
//             }
//         });
//     });
// }

// // Initialize additional features
// document.addEventListener('DOMContentLoaded', function() {
//     initSearch();
//     initLazyLoading();
//     initSmoothScrolling();
// });

// // Utility function to format currency
// function formatCurrency(amount) {
//     return new Intl.NumberFormat('vi-VN', {
//         style: 'currency',
//         currency: 'VND'
//     }).format(amount);
// }

// // Utility function to debounce
// function debounce(func, wait) {
//     let timeout;
//     return function executedFunction(...args) {
//         const later = () => {
//             clearTimeout(timeout);
//             func(...args);
//         };
//         clearTimeout(timeout);
//         timeout = setTimeout(later, wait);
//     };
// }

// // Export functions for global use
// window.BeautySale = {
//     formatCurrency,
//     showNotification,
//     updateCartCount
// };

// // Global scroll to top function
// window.scrollToTop = function() {
//     window.scrollTo({
//         top: 0,
//         behavior: 'smooth'
//     });
// };

// // Initialize floating scroll to top button
// document.addEventListener('DOMContentLoaded', function() {
//     const scrollTopBtn = document.querySelector('.scroll-top-btn');
//     if (scrollTopBtn) {
//         scrollTopBtn.style.display = 'none';
        
//         window.addEventListener('scroll', function() {
//             if (window.scrollY > 300) {
//                 scrollTopBtn.style.display = 'flex';
//             } else {
//                 scrollTopBtn.style.display = 'none';
//             }
//         });
//     }
// }); 

// // Cart quantity controls
// function initCartQuantityControls() {
//     const cartTable = document.querySelector('table');
//     if (!cartTable) return;

//     function parseNumber(text) {
//         return parseInt(String(text).replace(/[^0-9]/g, ''), 10) || 0;
//     }

//     function updateTotals() {
//         const lineTotals = Array.from(document.querySelectorAll('.cart-line-total'));
//         const subtotal = lineTotals.reduce((sum, el) => sum + parseNumber(el.textContent), 0);
//         const subtotalEl = document.querySelector('.cart-subtotal');
//         const shippingEl = document.querySelector('.cart-shipping');
//         const totalEl = document.querySelector('.cart-total');
//         const shipping = shippingEl ? parseNumber(shippingEl.textContent) : 0;
//         if (subtotalEl) subtotalEl.textContent = new Intl.NumberFormat('vi-VN').format(subtotal) + 'đ';
//         if (totalEl) totalEl.textContent = new Intl.NumberFormat('vi-VN').format(subtotal + shipping) + 'đ';

//         // Update global cart badge with total quantity
//         const totalQty = Array.from(document.querySelectorAll('.cart-qty-input'))
//             .reduce((sum, input) => sum + (parseInt(input.value, 10) || 0), 0);
//         document.querySelectorAll('.cart-badge').forEach(badge => {
//             badge.textContent = totalQty;
//         });

//         // Toggle empty cart UI
//         toggleCartEmptyUI(totalQty === 0);
//     }

//     cartTable.addEventListener('click', function(e) {
//         const decreaseBtn = e.target.closest('.cart-qty-decrease');
//         const increaseBtn = e.target.closest('.cart-qty-increase');
//         const removeBtn = e.target.closest('.cart-remove-btn');
//         if (!decreaseBtn && !increaseBtn && !removeBtn) return;

//         const row = e.target.closest('tr');
//         const input = row.querySelector('.cart-qty-input');
//         const priceEl = row.querySelector('.cart-price');
//         const lineTotalEl = row.querySelector('.cart-line-total');
//         const unitPrice = parseNumber(priceEl?.dataset?.price);

//         // Handle remove button explicitly (use modal)
//         if (removeBtn) {
//             const name = row.querySelector('td:nth-child(2) .fw-semibold')?.textContent?.trim() || 'sản phẩm này';
//             showCartConfirm(`Bạn có muốn xóa ${name} khỏi giỏ hàng không?`, () => {
//                 row.remove();
//                 updateTotals();
//             });
//             return;
//         }

//         let qty = parseInt(input.value, 10) || 1;
//         if (increaseBtn) {
//             qty = qty + 1;
//         } else if (decreaseBtn) {
//             if (qty - 1 <= 0) {
//                 const name = row.querySelector('td:nth-child(2) .fw-semibold')?.textContent?.trim() || 'sản phẩm này';
//                 showCartConfirm(`Số lượng về 0. Bạn có muốn xóa ${name} khỏi giỏ hàng không?`, () => {
//                     row.remove();
//                     updateTotals();
//                 });
//                 return;
//             } else {
//                 qty = qty - 1;
//             }
//         }
//         input.value = qty;

//         const newLineTotal = unitPrice * qty;
//         lineTotalEl.textContent = new Intl.NumberFormat('vi-VN').format(newLineTotal) + 'đ';

//         updateTotals();
//     });

//     // Handle typing quantity directly
//     cartTable.addEventListener('input', function(e) {
//         const input = e.target.closest('.cart-qty-input');
//         if (!input) return;
//         const row = input.closest('tr');
//         const priceEl = row.querySelector('.cart-price');
//         const lineTotalEl = row.querySelector('.cart-line-total');
//         const unitPrice = parseNumber(priceEl?.dataset?.price);

//         // Keep only digits
//         const digits = input.value.replace(/[^0-9]/g, '');
//         input.value = digits;
//         const qty = Math.max(0, parseInt(digits || '0', 10));

//         const newLineTotal = unitPrice * qty;
//         lineTotalEl.textContent = new Intl.NumberFormat('vi-VN').format(newLineTotal) + 'đ';
//         updateTotals();
//     });

//     // Enforce minimums and confirm removal on blur/change
//     cartTable.addEventListener('change', function(e) {
//         const input = e.target.closest('.cart-qty-input');
//         if (!input) return;
//         const row = input.closest('tr');
//         let qty = parseInt(input.value || '0', 10) || 0;

//         if (qty <= 0) {
//             const name = row.querySelector('td:nth-child(2) .fw-semibold')?.textContent?.trim() || 'sản phẩm này';
//             showCartConfirm(`Số lượng về 0. Bạn có muốn xóa ${name} khỏi giỏ hàng không?`, () => {
//                 row.remove();
//                 updateTotals();
//             });
//             // restore visual to 0 until user confirms; totals already updated
//             return;
//         }

//         // clamp to reasonable max if needed (optional)
//         if (qty > 9999) qty = 9999;
//         input.value = String(qty);
//         // totals already refreshed in input handler, but ensure now as well
//         const priceEl = row.querySelector('.cart-price');
//         const lineTotalEl = row.querySelector('.cart-line-total');
//         const unitPrice = parseNumber(priceEl?.dataset?.price);
//         const newLineTotal = unitPrice * qty;
//         lineTotalEl.textContent = new Intl.NumberFormat('vi-VN').format(newLineTotal) + 'đ';
//         updateTotals();
//     });

//     // Initial sync on load
//     updateTotals();
// }

// // Toggle empty cart state UI (hide summary, show empty message, disable checkout)
// function toggleCartEmptyUI(isEmpty) {
//     const leftCol = document.querySelector('.row.g-4 .col-lg-8');
//     const firstCard = leftCol ? leftCol.querySelector('.card.border-0.shadow-sm') : null;
//     const summaryCol = document.querySelector('.row.g-4 .col-lg-4');
//     const summaryCards = summaryCol ? summaryCol.querySelectorAll('.card') : [];
//     const checkoutLinks = document.querySelectorAll('a[href="/checkout"]');

//     // Manage summary visibility and checkout enable/disable
//     checkoutLinks.forEach(a => {
//         if (isEmpty) {
//             a.classList.add('disabled');
//             a.setAttribute('aria-disabled', 'true');
//             a.setAttribute('tabindex', '-1');
//         } else {
//             a.classList.remove('disabled');
//             a.removeAttribute('aria-disabled');
//             a.removeAttribute('tabindex');
//         }
//     });

//     summaryCards.forEach(card => {
//         if (isEmpty) card.classList.add('d-none'); else card.classList.remove('d-none');
//     });

//     if (!leftCol || !firstCard) return;

//     let emptyEl = leftCol.querySelector('#cart-empty-state');
//     if (isEmpty) {
//         // Hide table card
//         firstCard.classList.add('d-none');
//         if (!emptyEl) {
//             emptyEl = document.createElement('div');
//             emptyEl.id = 'cart-empty-state';
//             emptyEl.className = 'card border-0 shadow-sm';
//             emptyEl.innerHTML = `
//                 <div class="card-body text-center py-5">
//                     <img src="/static/image/gif/khoc.gif" alt="empty" class="mx-auto mb-3" style="width: 120px; height: 120px; object-fit: cover; display:block;">
//                     <h5 class="fw-bold mb-2">Giỏ hàng trống</h5>
//                     <p class="text-muted mb-4">Bạn chưa thêm sản phẩm nào. Khám phá sản phẩm và thêm vào giỏ nhé!</p>
//                     <a href="/products" class="btn btn-primary"><i class="fas fa-shopping-bag me-2"></i>Mua sắm ngay</a>
//                 </div>`;
//             // Insert after the hidden first card
//             firstCard.insertAdjacentElement('afterend', emptyEl);
//         }
//     } else {
//         firstCard.classList.remove('d-none');
//         if (emptyEl) emptyEl.remove();
//     }
// }

// // Helper: show confirmation modal for cart actions
// function showCartConfirm(message, onOk) {
//     const modalEl = document.getElementById('cartConfirmModal');
//     const msgEl = document.getElementById('cartConfirmMessage');
//     const okBtn = document.getElementById('cartConfirmOkBtn');
//     if (!modalEl || !msgEl || !okBtn) {
//         if (confirm(message)) onOk && onOk();
//         return;
//     }
//     msgEl.textContent = message;
//     const modal = new bootstrap.Modal(modalEl);
//     let gifRestartIntervalId = null;

//     const handleOk = () => {
//         cleanup();
//         modal.hide();
//         onOk && onOk();
//     };

//     const cleanup = () => {
//         okBtn.removeEventListener('click', handleOk);
//         modalEl.removeEventListener('hidden.bs.modal', cleanup);
//         modalEl.removeEventListener('shown.bs.modal', handleShown);
//         // Stop and reset GIF on close to avoid infinite loop effect
//         const gif = document.getElementById('cartSadGif');
//         if (gif) {
//             const src = gif.getAttribute('src');
//             gif.setAttribute('src', '');
//             // small delay then restore to reset one-shot playback on next open
//             setTimeout(() => gif.setAttribute('src', src), 0);
//         }
//         if (gifRestartIntervalId) {
//             clearInterval(gifRestartIntervalId);
//             gifRestartIntervalId = null;
//         }
//     };

//     // When modal is shown, keep the GIF looping by restarting its src periodically
//     const handleShown = () => {
//         const gif = document.getElementById('cartSadGif');
//         if (!gif) return;
//         const restartMs = parseInt(gif.getAttribute('data-restart-ms') || '3000', 10);
//         if (gifRestartIntervalId) clearInterval(gifRestartIntervalId);
//         gifRestartIntervalId = setInterval(() => {
//             const src = gif.getAttribute('src');
//             gif.setAttribute('src', '');
//             setTimeout(() => gif.setAttribute('src', src), 0);
//         }, Math.max(1500, restartMs));
//     };

//     okBtn.addEventListener('click', handleOk);
//     modalEl.addEventListener('hidden.bs.modal', cleanup);
//     modalEl.addEventListener('shown.bs.modal', handleShown);
//     modal.show();
// }


// // Main JavaScript for BeautySale Website

// document.addEventListener('DOMContentLoaded', function() {
//     // Initialize all components
//     initCountdownTimer();
//     initScrollToTop();
//     initProductCards();
//     initNewsletterForm();
//     initAnimations();
//     initMobileMenu();
//     initCartQuantityControls();
//     initCartBadgeZero();
//     initSearch();
//     initLazyLoading();
//     initSmoothScrolling();
//     initFlashSaleProducts(); // Khởi tạo Flash Sale
//     initNewProducts(); // Khởi tạo sản phẩm mới

//     // Ensure modal dismiss buttons always work
//     document.addEventListener('click', function(e) {
//         const dismissBtn = e.target.closest('[data-bs-dismiss="modal"]');
//         if (!dismissBtn) return;
//         const modalEl = dismissBtn.closest('.modal');
//         if (modalEl && window.bootstrap) {
//             try {
//                 const instance = bootstrap.Modal.getOrCreateInstance(modalEl);
//                 instance.hide();
//             } catch (err) {
//                 // ignore
//             }
//         }
//     });
// });

// // --- Dynamic Products Section ---

// // Hàm chung để fetch và render sản phẩm
// async function fetchAndRenderProducts(apiUrl, containerSelector) {
//     const container = document.querySelector(containerSelector);
//     if (!container) {
//         console.error(`Không tìm thấy container với selector: ${containerSelector}`);
//         return;
//     }

//     // Xóa nội dung cũ trước khi thêm mới
//     container.innerHTML = '';

//     try {
//         const response = await fetch(apiUrl);
//         if (!response.ok) {
//             throw new Error('Lỗi khi lấy dữ liệu từ API');
//         }
//         const products = await response.json();
        
//         if (products.length === 0) {
//              container.innerHTML = '<p class="text-muted text-center py-4">Không có sản phẩm nào để hiển thị.</p>';
//              return;
//         }

//         products.forEach(product => {
//             container.innerHTML += createProductCard(product);
//         });

//         // Re-initialize Product Cards with new DOM elements
//         initProductCards();
//         // Re-initialize Animations with new DOM elements
//         initAnimations();

//     } catch (error) {
//         console.error(`Đã xảy ra lỗi khi tải dữ liệu từ ${apiUrl}:`, error);
//         container.innerHTML = '<p class="text-danger text-center py-4">Không thể tải dữ liệu sản phẩm. Vui lòng thử lại sau.</p>';
//     }
// }

// // Hàm khởi tạo cho Flash Sale
// function initFlashSaleProducts() {
//     const flashSaleApiUrl = 'https://buddyskincare.pythonanywhere.com/products/?tags=FlashSale';
//     const containerSelector = '#flash-sale-products';
//     fetchAndRenderProducts(flashSaleApiUrl, containerSelector);
// }

// // Hàm khởi tạo cho sản phẩm mới
// function initNewProducts() {
//     const newProductsApiUrl = 'https://buddyskincare.pythonanywhere.com/latest-products/';
//     const containerSelector = '#new-products';
//     fetchAndRenderProducts(newProductsApiUrl, containerSelector);
// }


// // Chức năng làm sạch container
// function clearProductsContainer() {
//     // Hàm này không còn cần thiết cho việc chung, nhưng vẫn giữ nếu có nhu cầu khác.
//     // Tốt hơn là nên dùng logic clear container bên trong fetchAndRenderProducts.
// }

// // Hàm định dạng giá tiền với dấu chấm
// function formatPrice(price) {
//     if (price === null || price === undefined) {
//         return 'Đang cập nhật';
//     }
//     // Chuyển đổi giá về dạng số, sau đó định dạng
//     const amount = Number(price);
//     if (isNaN(amount)) {
//         return 'Giá không hợp lệ';
//     }
//     return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(amount);
// }

// // Hàm tạo HTML cho một sản phẩm
// function createProductCard(product) {
//     // Lấy variant đầu tiên để hiển thị thông tin chính
//     const mainVariant = product.variants && product.variants.length > 0 ? product.variants[0] : null;

//     // Lấy ảnh thumbnail và xử lý trường hợp album không phải là mảng
//     // Khắc phục lỗi: Cấu trúc dữ liệu "album" là một đối tượng, không phải mảng.
//     const albumObject = product.album; 
//     const imagesArray = albumObject && Array.isArray(albumObject.images) ? albumObject.images : [];

//     const thumbnailImage = imagesArray.find(img => img.is_thumbnail)?.image;
//     const firstImage = imagesArray.length > 0 ? imagesArray[0].image : null;
//     const imageUrl = thumbnailImage || firstImage || '/static/image/default-product.jpg';

//     // Lấy thương hiệu và danh mục
//     const brandName = product.brand ? product.brand.name : 'Không rõ';
//     const categoryName = product.specific_category ? product.specific_category.name : 'Sản phẩm';

//     // Xử lý giá tiền
//     // Thay đổi cách lấy và xử lý giá tiền
// const originalPrice = mainVariant ? mainVariant.original_price * 1000 : null;
// const discountedPrice = mainVariant ? mainVariant.discounted_price * 1000 : null;
// const rating = mainVariant ? mainVariant.rating : null;
// const fullStars = Math.floor(rating);
// const hasHalfStar = rating % 1 >= 0.5 && rating % 1 < 1; // Điều kiện mới
// // Tạo HTML cho các ngôi sao
//     let starsHTML = '';
//     for (let i = 0; i < fullStars; i++) {
//         starsHTML += '<i class="fas fa-star"></i>';
//     }

//     if (hasHalfStar) {
//     starsHTML += '<i class="fas fa-star-half-alt"></i>';
// }
//     const totalStars = fullStars + (hasHalfStar ? 1 : 0);
// const emptyStars = 5 - totalStars;
// for (let i = 0; i < emptyStars; i++) {
//     starsHTML += '<i class="far fa-star"></i>';
// }
// // Đoạn code còn lại giữ nguyên
// const discountRate = (originalPrice && discountedPrice) ? Math.round(((originalPrice - discountedPrice) / originalPrice) * 100) : 0;
// const stockQuantity = mainVariant ? mainVariant.stock_quantity : 0;
// const soldQuantity = mainVariant.sold_quantity || 0; // Sử dụng sold_quantity từ product chính

// const totalStock = stockQuantity + soldQuantity;
// const progressPercentage = totalStock > 0 ? (soldQuantity / totalStock) * 100 : 0;
// const displayStockQuantity = stockQuantity > 99 ? '99+' : stockQuantity;
    
//     // Xử lý tên sản phẩm
//     const productName = product.name;

//     // Tạo thẻ HTML
//     const cardHTML = `
//         <div class="col-lg-2 col-md-6 col-6">
//             <div class="product-card card h-100 border-0 shadow-sm">
//                 <a href="/products/${product.id}" class="d-block text-decoration-none text-dark">
//                     <div class="position-relative">
//                         <img src="${imageUrl}" class="card-img-top" alt="${productName}">
//                         ${discountRate > 0 ? `<div class="badge-sale">${discountRate}%</div>` : ''}
//                     </div>
//                 </a>
//                 <div class="card-body">
//                     <a href="/products/${product.id}" class="d-block text-decoration-none text-dark">
//                         <h6 class="card-title">${productName}</h6>
//                         <p class="text-muted small">${brandName}</p>
//                     </a>
//                     <div class="d-flex align-items-center mb-2">
//                         ${originalPrice ? `<span class="text-decoration-line-through text-muted me-2 dt">${formatPrice(originalPrice)}</span>` : ''}
//                         <span class="text-danger fw-bold fs-5 dt-text">${formatPrice(discountedPrice)}</span>
//                     </div>
//                     <div class="d-flex align-items-center mb-3">
//                         <div class="stars text-warning me-2">
//                             ${starsHTML}
//                         </div>
//                         <small class="text-muted">(${rating})</small>
//                     </div>
//                     <div class="stock">
//                         <div class="progress">
//                             <div class="progress-bar" role="progressbar" style="width: ${progressPercentage}%" aria-valuenow="${progressPercentage}" aria-valuemin="0" aria-valuemax="100"></div>
//                         </div>
//                         <span class="stock-text">đã bán ${soldQuantity} sản phẩm</span>
//                     </div>
//                     <button class="btn btn-outline-primary w-100 mt-2 add-to-cart-btn" data-product-id="${product.id}">Thêm vào giỏ</button>
//                 </div>
//             </div>
//         </div>
//     `;
//     return cardHTML;
// }

// // --- End of Dynamic Products Section ---

// // Countdown Timer for Flash Sale
// function initCountdownTimer() {
//     const countdownElements = document.querySelectorAll('.countdown-number');
//     if (countdownElements.length === 0) return;

//     // Set target date (2 days from now)
//     const targetDate = new Date();
//     targetDate.setDate(targetDate.getDate() + 2);
//     targetDate.setHours(15, 30, 45, 0);

//     function updateCountdown() {
//         const now = new Date().getTime();
//         const distance = targetDate.getTime() - now;

//         if (distance < 0) {
//             // Countdown finished
//             countdownElements.forEach(el => el.textContent = '00');
//             return;
//         }

//         const days = Math.floor(distance / (1000 * 60 * 60 * 24));
//         const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
//         const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
//         const seconds = Math.floor((distance % (1000 * 60)) / 1000);

//         // Update display
//         if (countdownElements[0]) countdownElements[0].textContent = days.toString().padStart(2, '0');
//         if (countdownElements[1]) countdownElements[1].textContent = hours.toString().padStart(2, '0');
//         if (countdownElements[2]) countdownElements[2].textContent = minutes.toString().padStart(2, '0');
//         if (countdownElements[3]) countdownElements[3].textContent = seconds.toString().padStart(2, '0');
//     }

//     // Update countdown every second
//     updateCountdown();
//     setInterval(updateCountdown, 1000);
// }

// // Scroll to Top Button
// function initScrollToTop() {
//     // Create scroll to top button
//     const scrollButton = document.createElement('button');
//     scrollButton.className = 'scroll-to-top';
//     scrollButton.innerHTML = '<i class="fas fa-arrow-up"></i>';
//     document.body.appendChild(scrollButton);

//     // Show/hide button based on scroll position
//     window.addEventListener('scroll', function() {
//         if (window.pageYOffset > 300) {
//             scrollButton.classList.add('show');
//         } else {
//             scrollButton.classList.remove('show');
//         }
//     });

//     // Scroll to top when clicked
//     scrollButton.addEventListener('click', function() {
//         window.scrollTo({
//             top: 0,
//             behavior: 'smooth'
//         });
//     });
// }

// // Product Cards Interactions
// function initProductCards() {
//     const productCards = document.querySelectorAll('.product-card');
    
//     productCards.forEach(card => {
//         const addToCartBtn = card.querySelector('.add-to-cart-btn');
//         const productImage = card.querySelector('img');

//         if (addToCartBtn) {
//             addToCartBtn.addEventListener('click', function(e) {
//                 e.preventDefault();

//                 // Trigger fly-to-cart animation instead of loading text
//                 flyToCart(productImage, () => {
//                     updateCartCount();
//                 });
//             });
//         }
//     });
// }

// // Update Cart Count
// function updateCartCount() {
//     const cartBadges = document.querySelectorAll('.cart-badge');
//     if (cartBadges.length === 0) return;

//     cartBadges.forEach(cartBadge => {
//         const currentCount = parseInt((cartBadge.textContent || '0').trim(), 10) || 0;
//         cartBadge.textContent = currentCount + 1;

//         // Add animation
//         cartBadge.style.transform = 'scale(1.2)';
//         setTimeout(() => {
//             cartBadge.style.transform = 'scale(1)';
//         }, 200);
//     });
// }

// // Ensure cart badges show 0 on initial load when no items
// function initCartBadgeZero() {
//     const cartBadges = document.querySelectorAll('.cart-badge');
//     if (cartBadges.length === 0) return;
//     cartBadges.forEach(badge => {
//         const current = parseInt((badge.textContent || '').trim(), 10);
//         if (isNaN(current)) {
//             badge.textContent = '0';
//         }
//     });
// }

// // Fly product image to cart icon
// function flyToCart(sourceImageEl, onComplete) {
//     // Pick the visible cart icon (desktop or mobile)
//     const cartIcons = Array.from(document.querySelectorAll('.cart-icon, .fa-shopping-cart'));
//     const visibleCartIcon = cartIcons.find(icon => {
//         const rect = icon.getBoundingClientRect();
//         const style = window.getComputedStyle(icon);
//         return rect.width > 0 && rect.height > 0 && style.visibility !== 'hidden' && style.display !== 'none';
//     });

//     const cartIcon = visibleCartIcon || cartIcons[0];
//     if (!sourceImageEl || !cartIcon) {
//         if (typeof onComplete === 'function') onComplete();
//         return;
//     }

//     const imgRect = sourceImageEl.getBoundingClientRect();
//     const cartRect = cartIcon.getBoundingClientRect();

//     const flying = document.createElement('img');
//     flying.src = sourceImageEl.src;
//     flying.className = 'flying-to-cart';
//     flying.style.position = 'fixed';
//     flying.style.left = imgRect.left + 'px';
//     flying.style.top = imgRect.top + 'px';
//     flying.style.width = Math.max(60, Math.min(imgRect.width, 120)) + 'px';
//     flying.style.height = 'auto';
//     flying.style.borderRadius = '8px';
//     flying.style.zIndex = '9999';
//     flying.style.transition = 'transform 1.25s cubic-bezier(0.22, 1, 0.36, 1), opacity 1.25s ease';
//     flying.style.willChange = 'transform, opacity';
//     flying.style.opacity = '0.95';

//     document.body.appendChild(flying);

//     // Compute translate to cart center
//     const start = flying.getBoundingClientRect();
//     const targetX = cartRect.left + cartRect.width / 2 - (start.left + start.width / 2);
//     const targetY = cartRect.top + cartRect.height / 2 - (start.top + start.height / 2);

//     // Animate on next frame
//     requestAnimationFrame(() => {
//         flying.style.transform = `translate(${targetX}px, ${targetY}px) scale(0.2)`;
//         flying.style.opacity = '0.2';
//     });

//     let hasCompleted = false;
//     const cleanup = () => {
//         if (hasCompleted) return;
//         hasCompleted = true;
//         flying.remove();
//         // Brief bump on cart icon
//         cartIcon.style.transform = 'scale(1.2)';
//         setTimeout(() => {
//             cartIcon.style.transform = 'scale(1)';
//         }, 200);
//         if (typeof onComplete === 'function') onComplete();
//     };

//     flying.addEventListener('transitionend', cleanup, { once: true });
//     // Fallback cleanup
//     setTimeout(cleanup, 1700);
// }

// // Newsletter Form
// function initNewsletterForm() {
//     const newsletterForm = document.querySelector('.newsletter-section .input-group');
//     if (!newsletterForm) return;

//     const emailInput = newsletterForm.querySelector('input[type="email"]');
//     const submitBtn = newsletterForm.querySelector('button');

//     submitBtn.addEventListener('click', function(e) {
//         e.preventDefault();
        
//         const email = emailInput.value.trim();
        
//         if (!email || !isValidEmail(email)) {
//             showNotification('Vui lòng nhập email hợp lệ!', 'error');
//             return;
//         }
        
//         // Add loading state
//         const originalText = this.textContent;
//         this.innerHTML = '<span class="loading"></span> Đang đăng ký...';
//         this.disabled = true;
        
//         // Simulate API call
//         setTimeout(() => {
//             this.innerHTML = '<i class="fas fa-check"></i> Đã đăng ký!';
//             this.classList.remove('btn-light');
//             this.classList.add('btn-success');
//             emailInput.value = '';
            
//             showNotification('Đăng ký thành công! Bạn sẽ nhận được thông báo sớm nhất.', 'success');
            
//             // Reset button after 3 seconds
//             setTimeout(() => {
//                 this.innerHTML = originalText;
//                 this.classList.remove('btn-success');
//                 this.classList.add('btn-light');
//                 this.disabled = false;
//             }, 3000);
//         }, 1500);
//     });
// }

// // Email validation
// function isValidEmail(email) {
//     const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
//     return emailRegex.test(email);
// }

// // Show notification
// function showNotification(message, type = 'info') {
//     // Create notification element
//     const notification = document.createElement('div');
//     notification.className = `alert alert-${type === 'error' ? 'danger' : type === 'success' ? 'success' : 'info'} alert-dismissible fade show position-fixed`;
//     notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
//     notification.innerHTML = `
//         ${message}
//         <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
//     `;
    
//     document.body.appendChild(notification);
    
//     // Auto remove after 5 seconds
//     setTimeout(() => {
//         if (notification.parentNode) {
//             notification.remove();
//         }
//     }, 5000);
// }

// // Animations on scroll
// function initAnimations() {
//     const observerOptions = {
//         threshold: 0.1,
//         rootMargin: '0px 0px -50px 0px'
//     };

//     const observer = new IntersectionObserver(function(entries) {
//         entries.forEach(entry => {
//             if (entry.isIntersecting) {
//                 entry.target.classList.add('fade-in');
//                 observer.unobserve(entry.target);
//             }
//         });
//     }, observerOptions);

//     // Observe elements for animation
//     const animateElements = document.querySelectorAll('.product-card, .category-card, .testimonial-card');
//     animateElements.forEach(el => {
//         observer.observe(el);
//     });
// }

// // Mobile menu enhancements
// function initMobileMenu() {
//     const navbarToggler = document.querySelector('.navbar-toggler');
//     const navbarCollapse = document.querySelector('.navbar-collapse');
    
//     if (navbarToggler && navbarCollapse) {
//         // Close mobile menu when clicking on a link
//         const navLinks = navbarCollapse.querySelectorAll('.nav-link');
//         navLinks.forEach(link => {
//             link.addEventListener('click', () => {
//                 if (window.innerWidth < 992) {
//                     const bsCollapse = new bootstrap.Collapse(navbarCollapse);
//                     bsCollapse.hide();
//                 }
//             });
//         });
//     }
// }

// // Search functionality
// function initSearch() {
//     const searchInput = document.querySelector('input[placeholder*="Tìm kiếm"]');
//     if (!searchInput) return;

//     let searchTimeout;
    
//     searchInput.addEventListener('input', function() {
//         clearTimeout(searchTimeout);
        
//         searchTimeout = setTimeout(() => {
//             const query = this.value.trim();
//             if (query.length >= 2) {
//                 // Simulate search
//                 console.log('Searching for:', query);
//                 // Here you would typically make an API call
//             }
//         }, 500);
//     });
// }

// // Lazy loading for images
// function initLazyLoading() {
//     const images = document.querySelectorAll('img[data-src]');
    
//     const imageObserver = new IntersectionObserver((entries, observer) => {
//         entries.forEach(entry => {
//             if (entry.isIntersecting) {
//                 const img = entry.target;
//                 img.src = img.dataset.src;
//                 img.classList.remove('lazy');
//                 imageObserver.unobserve(img);
//             }
//         });
//     });

//     images.forEach(img => imageObserver.observe(img));
// }

// // Smooth scrolling for anchor links
// function initSmoothScrolling() {
//     const anchorLinks = document.querySelectorAll('a[href^="#"]');
    
//     anchorLinks.forEach(link => {
//         link.addEventListener('click', function(e) {
//             e.preventDefault();
            
//             const targetId = this.getAttribute('href');
//             const targetElement = document.querySelector(targetId);
            
//             if (targetElement) {
//                 targetElement.scrollIntoView({
//                     behavior: 'smooth',
//                     block: 'start'
//                 });
//             }
//         });
//     });
// }

// // Initialize additional features
// document.addEventListener('DOMContentLoaded', function() {
//     initSearch();
//     initLazyLoading();
//     initSmoothScrolling();
// });

// // Utility function to format currency
// function formatCurrency(amount) {
//     return new Intl.NumberFormat('vi-VN', {
//         style: 'currency',
//         currency: 'VND'
//     }).format(amount);
// }

// // Utility function to debounce
// function debounce(func, wait) {
//     let timeout;
//     return function executedFunction(...args) {
//         const later = () => {
//             clearTimeout(timeout);
//             func(...args);
//         };
//         clearTimeout(timeout);
//         timeout = setTimeout(later, wait);
//     };
// }

// // Export functions for global use
// window.BeautySale = {
//     formatCurrency,
//     showNotification,
//     updateCartCount
// };

// // Global scroll to top function
// window.scrollToTop = function() {
//     window.scrollTo({
//         top: 0,
//         behavior: 'smooth'
//     });
// };

// // Initialize floating scroll to top button
// document.addEventListener('DOMContentLoaded', function() {
//     const scrollTopBtn = document.querySelector('.scroll-top-btn');
//     if (scrollTopBtn) {
//         scrollTopBtn.style.display = 'none';
        
//         window.addEventListener('scroll', function() {
//             if (window.scrollY > 300) {
//                 scrollTopBtn.style.display = 'flex';
//             } else {
//                 scrollTopBtn.style.display = 'none';
//             }
//         });
//     }
// }); 

// // Cart quantity controls
// function initCartQuantityControls() {
//     const cartTable = document.querySelector('table');
//     if (!cartTable) return;

//     function parseNumber(text) {
//         return parseInt(String(text).replace(/[^0-9]/g, ''), 10) || 0;
//     }

//     function updateTotals() {
//         const lineTotals = Array.from(document.querySelectorAll('.cart-line-total'));
//         const subtotal = lineTotals.reduce((sum, el) => sum + parseNumber(el.textContent), 0);
//         const subtotalEl = document.querySelector('.cart-subtotal');
//         const shippingEl = document.querySelector('.cart-shipping');
//         const totalEl = document.querySelector('.cart-total');
//         const shipping = shippingEl ? parseNumber(shippingEl.textContent) : 0;
//         if (subtotalEl) subtotalEl.textContent = new Intl.NumberFormat('vi-VN').format(subtotal) + 'đ';
//         if (totalEl) totalEl.textContent = new Intl.NumberFormat('vi-VN').format(subtotal + shipping) + 'đ';

//         // Update global cart badge with total quantity
//         const totalQty = Array.from(document.querySelectorAll('.cart-qty-input'))
//             .reduce((sum, input) => sum + (parseInt(input.value, 10) || 0), 0);
//         document.querySelectorAll('.cart-badge').forEach(badge => {
//             badge.textContent = totalQty;
//         });

//         // Toggle empty cart UI
//         toggleCartEmptyUI(totalQty === 0);
//     }

//     cartTable.addEventListener('click', function(e) {
//         const decreaseBtn = e.target.closest('.cart-qty-decrease');
//         const increaseBtn = e.target.closest('.cart-qty-increase');
//         const removeBtn = e.target.closest('.cart-remove-btn');
//         if (!decreaseBtn && !increaseBtn && !removeBtn) return;

//         const row = e.target.closest('tr');
//         const input = row.querySelector('.cart-qty-input');
//         const priceEl = row.querySelector('.cart-price');
//         const lineTotalEl = row.querySelector('.cart-line-total');
//         const unitPrice = parseNumber(priceEl?.dataset?.price);

//         // Handle remove button explicitly (use modal)
//         if (removeBtn) {
//             const name = row.querySelector('td:nth-child(2) .fw-semibold')?.textContent?.trim() || 'sản phẩm này';
//             showCartConfirm(`Bạn có muốn xóa ${name} khỏi giỏ hàng không?`, () => {
//                 row.remove();
//                 updateTotals();
//             });
//             return;
//         }

//         let qty = parseInt(input.value, 10) || 1;
//         if (increaseBtn) {
//             qty = qty + 1;
//         } else if (decreaseBtn) {
//             if (qty - 1 <= 0) {
//                 const name = row.querySelector('td:nth-child(2) .fw-semibold')?.textContent?.trim() || 'sản phẩm này';
//                 showCartConfirm(`Số lượng về 0. Bạn có muốn xóa ${name} khỏi giỏ hàng không?`, () => {
//                     row.remove();
//                     updateTotals();
//                 });
//                 return;
//             } else {
//                 qty = qty - 1;
//             }
//         }
//         input.value = qty;

//         const newLineTotal = unitPrice * qty;
//         lineTotalEl.textContent = new Intl.NumberFormat('vi-VN').format(newLineTotal) + 'đ';

//         updateTotals();
//     });

//     // Handle typing quantity directly
//     cartTable.addEventListener('input', function(e) {
//         const input = e.target.closest('.cart-qty-input');
//         if (!input) return;
//         const row = input.closest('tr');
//         const priceEl = row.querySelector('.cart-price');
//         const lineTotalEl = row.querySelector('.cart-line-total');
//         const unitPrice = parseNumber(priceEl?.dataset?.price);

//         // Keep only digits
//         const digits = input.value.replace(/[^0-9]/g, '');
//         input.value = digits;
//         const qty = Math.max(0, parseInt(digits || '0', 10));

//         const newLineTotal = unitPrice * qty;
//         lineTotalEl.textContent = new Intl.NumberFormat('vi-VN').format(newLineTotal) + 'đ';
//         updateTotals();
//     });

//     // Enforce minimums and confirm removal on blur/change
//     cartTable.addEventListener('change', function(e) {
//         const input = e.target.closest('.cart-qty-input');
//         if (!input) return;
//         const row = input.closest('tr');
//         let qty = parseInt(input.value || '0', 10) || 0;

//         if (qty <= 0) {
//             const name = row.querySelector('td:nth-child(2) .fw-semibold')?.textContent?.trim() || 'sản phẩm này';
//             showCartConfirm(`Số lượng về 0. Bạn có muốn xóa ${name} khỏi giỏ hàng không?`, () => {
//                 row.remove();
//                 updateTotals();
//             });
//             // restore visual to 0 until user confirms; totals already updated
//             return;
//         }

//         // clamp to reasonable max if needed (optional)
//         if (qty > 9999) qty = 9999;
//         input.value = String(qty);
//         // totals already refreshed in input handler, but ensure now as well
//         const priceEl = row.querySelector('.cart-price');
//         const lineTotalEl = row.querySelector('.cart-line-total');
//         const unitPrice = parseNumber(priceEl?.dataset?.price);
//         const newLineTotal = unitPrice * qty;
//         lineTotalEl.textContent = new Intl.NumberFormat('vi-VN').format(newLineTotal) + 'đ';
//         updateTotals();
//     });

//     // Initial sync on load
//     updateTotals();
// }

// // Toggle empty cart state UI (hide summary, show empty message, disable checkout)
// function toggleCartEmptyUI(isEmpty) {
//     const leftCol = document.querySelector('.row.g-4 .col-lg-8');
//     const firstCard = leftCol ? leftCol.querySelector('.card.border-0.shadow-sm') : null;
//     const summaryCol = document.querySelector('.row.g-4 .col-lg-4');
//     const summaryCards = summaryCol ? summaryCol.querySelectorAll('.card') : [];
//     const checkoutLinks = document.querySelectorAll('a[href="/checkout"]');

//     // Manage summary visibility and checkout enable/disable
//     checkoutLinks.forEach(a => {
//         if (isEmpty) {
//             a.classList.add('disabled');
//             a.setAttribute('aria-disabled', 'true');
//             a.setAttribute('tabindex', '-1');
//         } else {
//             a.classList.remove('disabled');
//             a.removeAttribute('aria-disabled');
//             a.removeAttribute('tabindex');
//         }
//     });

//     summaryCards.forEach(card => {
//         if (isEmpty) card.classList.add('d-none'); else card.classList.remove('d-none');
//     });

//     if (!leftCol || !firstCard) return;

//     let emptyEl = leftCol.querySelector('#cart-empty-state');
//     if (isEmpty) {
//         // Hide table card
//         firstCard.classList.add('d-none');
//         if (!emptyEl) {
//             emptyEl = document.createElement('div');
//             emptyEl.id = 'cart-empty-state';
//             emptyEl.className = 'card border-0 shadow-sm';
//             emptyEl.innerHTML = `
//                 <div class="card-body text-center py-5">
//                     <img src="/static/image/gif/khoc.gif" alt="empty" class="mx-auto mb-3" style="width: 120px; height: 120px; object-fit: cover; display:block;">
//                     <h5 class="fw-bold mb-2">Giỏ hàng trống</h5>
//                     <p class="text-muted mb-4">Bạn chưa thêm sản phẩm nào. Khám phá sản phẩm và thêm vào giỏ nhé!</p>
//                     <a href="/products" class="btn btn-primary"><i class="fas fa-shopping-bag me-2"></i>Mua sắm ngay</a>
//                 </div>`;
//             // Insert after the hidden first card
//             firstCard.insertAdjacentElement('afterend', emptyEl);
//         }
//     } else {
//         firstCard.classList.remove('d-none');
//         if (emptyEl) emptyEl.remove();
//     }
// }

// // Helper: show confirmation modal for cart actions
// function showCartConfirm(message, onOk) {
//     const modalEl = document.getElementById('cartConfirmModal');
//     const msgEl = document.getElementById('cartConfirmMessage');
//     const okBtn = document.getElementById('cartConfirmOkBtn');
//     if (!modalEl || !msgEl || !okBtn) {
//         if (confirm(message)) onOk && onOk();
//         return;
//     }
//     msgEl.textContent = message;
//     const modal = new bootstrap.Modal(modalEl);
//     let gifRestartIntervalId = null;

//     const handleOk = () => {
//         cleanup();
//         modal.hide();
//         onOk && onOk();
//     };

//     const cleanup = () => {
//         okBtn.removeEventListener('click', handleOk);
//         modalEl.removeEventListener('hidden.bs.modal', cleanup);
//         modalEl.removeEventListener('shown.bs.modal', handleShown);
//         // Stop and reset GIF on close to avoid infinite loop effect
//         const gif = document.getElementById('cartSadGif');
//         if (gif) {
//             const src = gif.getAttribute('src');
//             gif.setAttribute('src', '');
//             // small delay then restore to reset one-shot playback on next open
//             setTimeout(() => gif.setAttribute('src', src), 0);
//         }
//         if (gifRestartIntervalId) {
//             clearInterval(gifRestartIntervalId);
//             gifRestartIntervalId = null;
//         }
//     };

//     // When modal is shown, keep the GIF looping by restarting its src periodically
//     const handleShown = () => {
//         const gif = document.getElementById('cartSadGif');
//         if (!gif) return;
//         const restartMs = parseInt(gif.getAttribute('data-restart-ms') || '3000', 10);
//         if (gifRestartIntervalId) clearInterval(gifRestartIntervalId);
//         gifRestartIntervalId = setInterval(() => {
//             const src = gif.getAttribute('src');
//             gif.setAttribute('src', '');
//             setTimeout(() => gif.setAttribute('src', src), 0);
//         }, Math.max(1500, restartMs));
//     };

//     okBtn.addEventListener('click', handleOk);
//     modalEl.addEventListener('hidden.bs.modal', cleanup);
//     modalEl.addEventListener('shown.bs.modal', handleShown);
//     modal.show();
// }





// Main JavaScript for BeautySale Website

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components
    initCountdownTimer();
    initScrollToTop();
    initProductCards();
    initNewsletterForm();
    initAnimations();
    initMobileMenu();
    initCartQuantityControls();
    initCartBadgeZero();
    initSearch();
    initLazyLoading();
    initSmoothScrolling();
    initFlashSaleProducts(); // Khởi tạo Flash Sale
    initNewProducts(); // Khởi tạo sản phẩm mới

    // Ensure modal dismiss buttons always work
    document.addEventListener('click', function(e) {
        const dismissBtn = e.target.closest('[data-bs-dismiss="modal"]');
        if (!dismissBtn) return;
        const modalEl = dismissBtn.closest('.modal');
        if (modalEl && window.bootstrap) {
            try {
                const instance = bootstrap.Modal.getOrCreateInstance(modalEl);
                instance.hide();
            } catch (err) {
                // ignore
            }
        }
    });
});

// --- Dynamic Products Section ---

// Hàm chung để fetch và render sản phẩm
async function fetchAndRenderProducts(apiUrl, containerSelector) {
    const container = document.querySelector(containerSelector);
    if (!container) {
        console.error(`Không tìm thấy container với selector: ${containerSelector}`);
        return;
    }

    // Xóa nội dung cũ trước khi thêm mới
    container.innerHTML = '';

    try {
        const response = await fetch(apiUrl);
        if (!response.ok) {
            throw new Error('Lỗi khi lấy dữ liệu từ API');
        }
        const products = await response.json();
        
        if (products.length === 0) {
            container.innerHTML = '<p class="text-muted text-center py-4">Không có sản phẩm nào để hiển thị.</p>';
            return;
        }

        products.forEach(product => {
            container.innerHTML += createProductCard(product);
        });

        // Re-initialize Product Cards with new DOM elements
        initProductCards();
        // Re-initialize Animations with new DOM elements
        initAnimations();

    } catch (error) {
        console.error(`Đã xảy ra lỗi khi tải dữ liệu từ ${apiUrl}:`, error);
        container.innerHTML = '<p class="text-danger text-center py-4">Không thể tải dữ liệu sản phẩm. Vui lòng thử lại sau.</p>';
    }
}

// Hàm khởi tạo cho Flash Sale
function initFlashSaleProducts() {
    const flashSaleApiUrl = 'https://buddyskincare.pythonanywhere.com/products/?tags=FlashSale';
    const containerSelector = '#flash-sale-products';
    fetchAndRenderProducts(flashSaleApiUrl, containerSelector);
}

// Hàm khởi tạo cho sản phẩm mới
function initNewProducts() {
    const newProductsApiUrl = 'https://buddyskincare.pythonanywhere.com/latest-products/';
    const containerSelector = '#new-product-products'; // Đã sửa lỗi ở đây
    fetchAndRenderProducts(newProductsApiUrl, containerSelector);
}


// Chức năng làm sạch container
function clearProductsContainer() {
    // Hàm này không còn cần thiết cho việc chung, nhưng vẫn giữ nếu có nhu cầu khác.
    // Tốt hơn là nên dùng logic clear container bên trong fetchAndRenderProducts.
}

// Hàm định dạng giá tiền với dấu chấm
function formatPrice(price) {
    if (price === null || price === undefined) {
        return 'Đang cập nhật';
    }
    // Chuyển đổi giá về dạng số, sau đó định dạng
    const amount = Number(price);
    if (isNaN(amount)) {
        return 'Giá không hợp lệ';
    }
    return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(amount);
}

// Hàm tạo HTML cho một sản phẩm
function createProductCard(product) {
    // Lấy variant đầu tiên để hiển thị thông tin chính
    const mainVariant = product.variants && product.variants.length > 0 ? product.variants[0] : null;

    // Lấy ảnh thumbnail và xử lý trường hợp album không phải là mảng
    // Khắc phục lỗi: Cấu trúc dữ liệu "album" là một đối tượng, không phải mảng.
    const albumObject = product.album; 
    const imagesArray = albumObject && Array.isArray(albumObject.images) ? albumObject.images : [];

    const thumbnailImage = imagesArray.find(img => img.is_thumbnail)?.image;
    const firstImage = imagesArray.length > 0 ? imagesArray[0].image : null;
    const imageUrl = thumbnailImage || firstImage || '/static/image/default-product.jpg';

    // Lấy thương hiệu và danh mục
    const brandName = product.brand ? product.brand.name : 'Không rõ';
    const categoryName = product.specific_category ? product.specific_category.name : 'Sản phẩm';

    // Xử lý giá tiền
    // Thay đổi cách lấy và xử lý giá tiền
const originalPrice = mainVariant ? mainVariant.original_price * 1000 : null;
const discountedPrice = mainVariant ? mainVariant.discounted_price * 1000 : null;
const rating = mainVariant ? mainVariant.rating : null;
const fullStars = Math.floor(rating);
const hasHalfStar = rating % 1 >= 0.5 && rating % 1 < 1; // Điều kiện mới
// Tạo HTML cho các ngôi sao
    let starsHTML = '';
    for (let i = 0; i < fullStars; i++) {
        starsHTML += '<i class="fas fa-star"></i>';
    }

    if (hasHalfStar) {
    starsHTML += '<i class="fas fa-star-half-alt"></i>';
}
    const totalStars = fullStars + (hasHalfStar ? 1 : 0);
const emptyStars = 5 - totalStars;
for (let i = 0; i < emptyStars; i++) {
    starsHTML += '<i class="far fa-star"></i>';
}
// Đoạn code còn lại giữ nguyên
const discountRate = (originalPrice && discountedPrice) ? Math.round(((originalPrice - discountedPrice) / originalPrice) * 100) : 0;
const stockQuantity = mainVariant ? mainVariant.stock_quantity : 0;
const soldQuantity = mainVariant.sold_quantity || 0; // Sử dụng sold_quantity từ product chính

const totalStock = stockQuantity + soldQuantity;
const progressPercentage = totalStock > 0 ? (soldQuantity / totalStock) * 100 : 0;
const displayStockQuantity = stockQuantity > 99 ? '99+' : stockQuantity;
    
    // Xử lý tên sản phẩm
    const productName = product.name;

    // Tạo thẻ HTML
    const cardHTML = `
        <div class="col-lg-2 col-md-6 col-6">
            <div class="product-card card h-100 border-0 shadow-sm">
                <a href="/products/${product.id}" class="d-block text-decoration-none text-dark">
                    <div class="position-relative">
                        <img src="${imageUrl}" class="card-img-top" alt="${productName}">
                        ${discountRate > 0 ? `<div class="badge-sale">${discountRate}%</div>` : ''}
                    </div>
                </a>
                <div class="card-body">
                    <a href="/products/${product.id}" class="d-block text-decoration-none text-dark">
                        <h6 class="card-title">${productName}</h6>
                        <p class="text-muted small">${brandName}</p>
                    </a>
                    <div class="d-flex align-items-center mb-2">
                        ${originalPrice ? `<span class="text-decoration-line-through text-muted me-2 dt">${formatPrice(originalPrice)}</span>` : ''}
                        <span class="text-danger fw-bold fs-5 dt-text">${formatPrice(discountedPrice)}</span>
                    </div>
                    <div class="d-flex align-items-center mb-3">
                        <div class="stars text-warning me-2">
                            ${starsHTML}
                        </div>
                        <small class="text-muted">(${rating})</small>
                    </div>
                    <div class="stock">
                        <div class="progress">
                            <div class="progress-bar" role="progressbar" style="width: ${progressPercentage}%" aria-valuenow="${progressPercentage}" aria-valuemin="0" aria-valuemax="100"></div>
                        </div>
                        <span class="stock-text">đã bán ${soldQuantity} sản phẩm</span>
                    </div>
                    <button class="btn btn-outline-primary w-100 mt-2 add-to-cart-btn" data-product-id="${product.id}">Thêm vào giỏ</button>
                </div>
            </div>
        </div>
    `;
    return cardHTML;
}

// --- End of Dynamic Products Section ---

// Countdown Timer for Flash Sale
function initCountdownTimer() {
    const countdownElements = document.querySelectorAll('.countdown-number');
    if (countdownElements.length === 0) return;

    // Set target date (2 days from now)
    const targetDate = new Date();
    targetDate.setDate(targetDate.getDate() + 2);
    targetDate.setHours(15, 30, 45, 0);

    function updateCountdown() {
        const now = new Date().getTime();
        const distance = targetDate.getTime() - now;

        if (distance < 0) {
            // Countdown finished
            countdownElements.forEach(el => el.textContent = '00');
            return;
        }

        const days = Math.floor(distance / (1000 * 60 * 60 * 24));
        const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((distance % (1000 * 60)) / 1000);

        // Update display
        if (countdownElements[0]) countdownElements[0].textContent = days.toString().padStart(2, '0');
        if (countdownElements[1]) countdownElements[1].textContent = hours.toString().padStart(2, '0');
        if (countdownElements[2]) countdownElements[2].textContent = minutes.toString().padStart(2, '0');
        if (countdownElements[3]) countdownElements[3].textContent = seconds.toString().padStart(2, '0');
    }

    // Update countdown every second
    updateCountdown();
    setInterval(updateCountdown, 1000);
}

// Scroll to Top Button
function initScrollToTop() {
    // Create scroll to top button
    const scrollButton = document.createElement('button');
    scrollButton.className = 'scroll-to-top';
    scrollButton.innerHTML = '<i class="fas fa-arrow-up"></i>';
    document.body.appendChild(scrollButton);

    // Show/hide button based on scroll position
    window.addEventListener('scroll', function() {
        if (window.pageYOffset > 300) {
            scrollButton.classList.add('show');
        } else {
            scrollButton.classList.remove('show');
        }
    });

    // Scroll to top when clicked
    scrollButton.addEventListener('click', function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
}

// Product Cards Interactions
function initProductCards() {
    const productCards = document.querySelectorAll('.product-card');
    
    productCards.forEach(card => {
        const addToCartBtn = card.querySelector('.add-to-cart-btn');
        const productImage = card.querySelector('img');

        if (addToCartBtn) {
            addToCartBtn.addEventListener('click', function(e) {
                e.preventDefault();

                // Trigger fly-to-cart animation instead of loading text
                flyToCart(productImage, () => {
                    updateCartCount();
                });
            });
        }
    });
}

// Update Cart Count
function updateCartCount() {
    const cartBadges = document.querySelectorAll('.cart-badge');
    if (cartBadges.length === 0) return;

    cartBadges.forEach(cartBadge => {
        const currentCount = parseInt((cartBadge.textContent || '0').trim(), 10) || 0;
        cartBadge.textContent = currentCount + 1;

        // Add animation
        cartBadge.style.transform = 'scale(1.2)';
        setTimeout(() => {
            cartBadge.style.transform = 'scale(1)';
        }, 200);
    });
}

// Ensure cart badges show 0 on initial load when no items
function initCartBadgeZero() {
    const cartBadges = document.querySelectorAll('.cart-badge');
    if (cartBadges.length === 0) return;
    cartBadges.forEach(badge => {
        const current = parseInt((badge.textContent || '').trim(), 10);
        if (isNaN(current)) {
            badge.textContent = '0';
        }
    });
}

// Fly product image to cart icon
function flyToCart(sourceImageEl, onComplete) {
    // Pick the visible cart icon (desktop or mobile)
    const cartIcons = Array.from(document.querySelectorAll('.cart-icon, .fa-shopping-cart'));
    const visibleCartIcon = cartIcons.find(icon => {
        const rect = icon.getBoundingClientRect();
        const style = window.getComputedStyle(icon);
        return rect.width > 0 && rect.height > 0 && style.visibility !== 'hidden' && style.display !== 'none';
    });

    const cartIcon = visibleCartIcon || cartIcons[0];
    if (!sourceImageEl || !cartIcon) {
        if (typeof onComplete === 'function') onComplete();
        return;
    }

    const imgRect = sourceImageEl.getBoundingClientRect();
    const cartRect = cartIcon.getBoundingClientRect();

    const flying = document.createElement('img');
    flying.src = sourceImageEl.src;
    flying.className = 'flying-to-cart';
    flying.style.position = 'fixed';
    flying.style.left = imgRect.left + 'px';
    flying.style.top = imgRect.top + 'px';
    flying.style.width = Math.max(60, Math.min(imgRect.width, 120)) + 'px';
    flying.style.height = 'auto';
    flying.style.borderRadius = '8px';
    flying.style.zIndex = '9999';
    flying.style.transition = 'transform 1.25s cubic-bezier(0.22, 1, 0.36, 1), opacity 1.25s ease';
    flying.style.willChange = 'transform, opacity';
    flying.style.opacity = '0.95';

    document.body.appendChild(flying);

    // Compute translate to cart center
    const start = flying.getBoundingClientRect();
    const targetX = cartRect.left + cartRect.width / 2 - (start.left + start.width / 2);
    const targetY = cartRect.top + cartRect.height / 2 - (start.top + start.height / 2);

    // Animate on next frame
    requestAnimationFrame(() => {
        flying.style.transform = `translate(${targetX}px, ${targetY}px) scale(0.2)`;
        flying.style.opacity = '0.2';
    });

    let hasCompleted = false;
    const cleanup = () => {
        if (hasCompleted) return;
        hasCompleted = true;
        flying.remove();
        // Brief bump on cart icon
        cartIcon.style.transform = 'scale(1.2)';
        setTimeout(() => {
            cartIcon.style.transform = 'scale(1)';
        }, 200);
        if (typeof onComplete === 'function') onComplete();
    };

    flying.addEventListener('transitionend', cleanup, { once: true });
    // Fallback cleanup
    setTimeout(cleanup, 1700);
}

// Newsletter Form
function initNewsletterForm() {
    const newsletterForm = document.querySelector('.newsletter-section .input-group');
    if (!newsletterForm) return;

    const emailInput = newsletterForm.querySelector('input[type="email"]');
    const submitBtn = newsletterForm.querySelector('button');

    submitBtn.addEventListener('click', function(e) {
        e.preventDefault();
        
        const email = emailInput.value.trim();
        
        if (!email || !isValidEmail(email)) {
            showNotification('Vui lòng nhập email hợp lệ!', 'error');
            return;
        }
        
        // Add loading state
        const originalText = this.textContent;
        this.innerHTML = '<span class="loading"></span> Đang đăng ký...';
        this.disabled = true;
        
        // Simulate API call
        setTimeout(() => {
            this.innerHTML = '<i class="fas fa-check"></i> Đã đăng ký!';
            this.classList.remove('btn-light');
            this.classList.add('btn-success');
            emailInput.value = '';
            
            showNotification('Đăng ký thành công! Bạn sẽ nhận được thông báo sớm nhất.', 'success');
            
            // Reset button after 3 seconds
            setTimeout(() => {
                this.innerHTML = originalText;
                this.classList.remove('btn-success');
                this.classList.add('btn-light');
                this.disabled = false;
            }, 3000);
        }, 1500);
    });
}

// Email validation
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// Show notification
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `alert alert-${type === 'error' ? 'danger' : type === 'success' ? 'success' : 'info'} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}

// Animations on scroll
function initAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    // Observe elements for animation
    const animateElements = document.querySelectorAll('.product-card, .category-card, .testimonial-card');
    animateElements.forEach(el => {
        observer.observe(el);
    });
}

// Mobile menu enhancements
function initMobileMenu() {
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.querySelector('.navbar-collapse');
    
    if (navbarToggler && navbarCollapse) {
        // Close mobile menu when clicking on a link
        const navLinks = navbarCollapse.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', () => {
                if (window.innerWidth < 992) {
                    const bsCollapse = new bootstrap.Collapse(navbarCollapse);
                    bsCollapse.hide();
                }
            });
        });
    }
}

// Search functionality
function initSearch() {
    const searchInput = document.querySelector('input[placeholder*="Tìm kiếm"]');
    if (!searchInput) return;

    let searchTimeout;
    
    searchInput.addEventListener('input', function() {
        clearTimeout(searchTimeout);
        
        searchTimeout = setTimeout(() => {
            const query = this.value.trim();
            if (query.length >= 2) {
                // Simulate search
                console.log('Searching for:', query);
                // Here you would typically make an API call
            }
        }, 500);
    });
}

// Lazy loading for images
function initLazyLoading() {
    const images = document.querySelectorAll('img[data-src]');
    
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.remove('lazy');
                imageObserver.unobserve(img);
            }
        });
    });

    images.forEach(img => imageObserver.observe(img));
}

// Smooth scrolling for anchor links
function initSmoothScrolling() {
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    
    anchorLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);
            
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// Initialize additional features
document.addEventListener('DOMContentLoaded', function() {
    initSearch();
    initLazyLoading();
    initSmoothScrolling();
});

// Utility function to format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('vi-VN', {
        style: 'currency',
        currency: 'VND'
    }).format(amount);
}

// Utility function to debounce
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Export functions for global use
window.BeautySale = {
    formatCurrency,
    showNotification,
    updateCartCount
};

// Global scroll to top function
window.scrollToTop = function() {
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
};

// Initialize floating scroll to top button
document.addEventListener('DOMContentLoaded', function() {
    const scrollTopBtn = document.querySelector('.scroll-top-btn');
    if (scrollTopBtn) {
        scrollTopBtn.style.display = 'none';
        
        window.addEventListener('scroll', function() {
            if (window.scrollY > 300) {
                scrollTopBtn.style.display = 'flex';
            } else {
                scrollTopBtn.style.display = 'none';
            }
        });
    }
}); 

// Cart quantity controls
function initCartQuantityControls() {
    const cartTable = document.querySelector('table');
    if (!cartTable) return;

    function parseNumber(text) {
        return parseInt(String(text).replace(/[^0-9]/g, ''), 10) || 0;
    }

    function updateTotals() {
        const lineTotals = Array.from(document.querySelectorAll('.cart-line-total'));
        const subtotal = lineTotals.reduce((sum, el) => sum + parseNumber(el.textContent), 0);
        const subtotalEl = document.querySelector('.cart-subtotal');
        const shippingEl = document.querySelector('.cart-shipping');
        const totalEl = document.querySelector('.cart-total');
        const shipping = shippingEl ? parseNumber(shippingEl.textContent) : 0;
        if (subtotalEl) subtotalEl.textContent = new Intl.NumberFormat('vi-VN').format(subtotal) + 'đ';
        if (totalEl) totalEl.textContent = new Intl.NumberFormat('vi-VN').format(subtotal + shipping) + 'đ';

        // Update global cart badge with total quantity
        const totalQty = Array.from(document.querySelectorAll('.cart-qty-input'))
            .reduce((sum, input) => sum + (parseInt(input.value, 10) || 0), 0);
        document.querySelectorAll('.cart-badge').forEach(badge => {
            badge.textContent = totalQty;
        });

        // Toggle empty cart UI
        toggleCartEmptyUI(totalQty === 0);
    }

    cartTable.addEventListener('click', function(e) {
        const decreaseBtn = e.target.closest('.cart-qty-decrease');
        const increaseBtn = e.target.closest('.cart-qty-increase');
        const removeBtn = e.target.closest('.cart-remove-btn');
        if (!decreaseBtn && !increaseBtn && !removeBtn) return;

        const row = e.target.closest('tr');
        const input = row.querySelector('.cart-qty-input');
        const priceEl = row.querySelector('.cart-price');
        const lineTotalEl = row.querySelector('.cart-line-total');
        const unitPrice = parseNumber(priceEl?.dataset?.price);

        // Handle remove button explicitly (use modal)
        if (removeBtn) {
            const name = row.querySelector('td:nth-child(2) .fw-semibold')?.textContent?.trim() || 'sản phẩm này';
            showCartConfirm(`Bạn có muốn xóa ${name} khỏi giỏ hàng không?`, () => {
                row.remove();
                updateTotals();
            });
            return;
        }

        let qty = parseInt(input.value, 10) || 1;
        if (increaseBtn) {
            qty = qty + 1;
        } else if (decreaseBtn) {
            if (qty - 1 <= 0) {
                const name = row.querySelector('td:nth-child(2) .fw-semibold')?.textContent?.trim() || 'sản phẩm này';
                showCartConfirm(`Số lượng về 0. Bạn có muốn xóa ${name} khỏi giỏ hàng không?`, () => {
                    row.remove();
                    updateTotals();
                });
                return;
            } else {
                qty = qty - 1;
            }
        }
        input.value = qty;

        const newLineTotal = unitPrice * qty;
        lineTotalEl.textContent = new Intl.NumberFormat('vi-VN').format(newLineTotal) + 'đ';

        updateTotals();
    });

    // Handle typing quantity directly
    cartTable.addEventListener('input', function(e) {
        const input = e.target.closest('.cart-qty-input');
        if (!input) return;
        const row = input.closest('tr');
        const priceEl = row.querySelector('.cart-price');
        const lineTotalEl = row.querySelector('.cart-line-total');
        const unitPrice = parseNumber(priceEl?.dataset?.price);

        // Keep only digits
        const digits = input.value.replace(/[^0-9]/g, '');
        input.value = digits;
        const qty = Math.max(0, parseInt(digits || '0', 10));

        const newLineTotal = unitPrice * qty;
        lineTotalEl.textContent = new Intl.NumberFormat('vi-VN').format(newLineTotal) + 'đ';
        updateTotals();
    });

    // Enforce minimums and confirm removal on blur/change
    cartTable.addEventListener('change', function(e) {
        const input = e.target.closest('.cart-qty-input');
        if (!input) return;
        const row = input.closest('tr');
        let qty = parseInt(input.value || '0', 10) || 0;

        if (qty <= 0) {
            const name = row.querySelector('td:nth-child(2) .fw-semibold')?.textContent?.trim() || 'sản phẩm này';
            showCartConfirm(`Số lượng về 0. Bạn có muốn xóa ${name} khỏi giỏ hàng không?`, () => {
                row.remove();
                updateTotals();
            });
            // restore visual to 0 until user confirms; totals already updated
            return;
        }

        // clamp to reasonable max if needed (optional)
        if (qty > 9999) qty = 9999;
        input.value = String(qty);
        // totals already refreshed in input handler, but ensure now as well
        const priceEl = row.querySelector('.cart-price');
        const lineTotalEl = row.querySelector('.cart-line-total');
        const unitPrice = parseNumber(priceEl?.dataset?.price);
        const newLineTotal = unitPrice * qty;
        lineTotalEl.textContent = new Intl.NumberFormat('vi-VN').format(newLineTotal) + 'đ';
        updateTotals();
    });

    // Initial sync on load
    updateTotals();
}

// Toggle empty cart state UI (hide summary, show empty message, disable checkout)
function toggleCartEmptyUI(isEmpty) {
    const leftCol = document.querySelector('.row.g-4 .col-lg-8');
    const firstCard = leftCol ? leftCol.querySelector('.card.border-0.shadow-sm') : null;
    const summaryCol = document.querySelector('.row.g-4 .col-lg-4');
    const summaryCards = summaryCol ? summaryCol.querySelectorAll('.card') : [];
    const checkoutLinks = document.querySelectorAll('a[href="/checkout"]');

    // Manage summary visibility and checkout enable/disable
    checkoutLinks.forEach(a => {
        if (isEmpty) {
            a.classList.add('disabled');
            a.setAttribute('aria-disabled', 'true');
            a.setAttribute('tabindex', '-1');
        } else {
            a.classList.remove('disabled');
            a.removeAttribute('aria-disabled');
            a.removeAttribute('tabindex');
        }
    });

    summaryCards.forEach(card => {
        if (isEmpty) card.classList.add('d-none'); else card.classList.remove('d-none');
    });

    if (!leftCol || !firstCard) return;

    let emptyEl = leftCol.querySelector('#cart-empty-state');
    if (isEmpty) {
        // Hide table card
        firstCard.classList.add('d-none');
        if (!emptyEl) {
            emptyEl = document.createElement('div');
            emptyEl.id = 'cart-empty-state';
            emptyEl.className = 'card border-0 shadow-sm';
            emptyEl.innerHTML = `
                <div class="card-body text-center py-5">
                    <img src="/static/image/gif/khoc.gif" alt="empty" class="mx-auto mb-3" style="width: 120px; height: 120px; object-fit: cover; display:block;">
                    <h5 class="fw-bold mb-2">Giỏ hàng trống</h5>
                    <p class="text-muted mb-4">Bạn chưa thêm sản phẩm nào. Khám phá sản phẩm và thêm vào giỏ nhé!</p>
                    <a href="/products" class="btn btn-primary"><i class="fas fa-shopping-bag me-2"></i>Mua sắm ngay</a>
                </div>`;
            // Insert after the hidden first card
            firstCard.insertAdjacentElement('afterend', emptyEl);
        }
    } else {
        firstCard.classList.remove('d-none');
        if (emptyEl) emptyEl.remove();
    }
}

// Helper: show confirmation modal for cart actions
function showCartConfirm(message, onOk) {
    const modalEl = document.getElementById('cartConfirmModal');
    const msgEl = document.getElementById('cartConfirmMessage');
    const okBtn = document.getElementById('cartConfirmOkBtn');
    if (!modalEl || !msgEl || !okBtn) {
        if (confirm(message)) onOk && onOk();
        return;
    }
    msgEl.textContent = message;
    const modal = new bootstrap.Modal(modalEl);
    let gifRestartIntervalId = null;

    const handleOk = () => {
        cleanup();
        modal.hide();
        onOk && onOk();
    };

    const cleanup = () => {
        okBtn.removeEventListener('click', handleOk);
        modalEl.removeEventListener('hidden.bs.modal', cleanup);
        modalEl.removeEventListener('shown.bs.modal', handleShown);
        // Stop and reset GIF on close to avoid infinite loop effect
        const gif = document.getElementById('cartSadGif');
        if (gif) {
            const src = gif.getAttribute('src');
            gif.setAttribute('src', '');
            // small delay then restore to reset one-shot playback on next open
            setTimeout(() => gif.setAttribute('src', src), 0);
        }
        if (gifRestartIntervalId) {
            clearInterval(gifRestartIntervalId);
            gifRestartIntervalId = null;
        }
    };

    // When modal is shown, keep the GIF looping by restarting its src periodically
    const handleShown = () => {
        const gif = document.getElementById('cartSadGif');
        if (!gif) return;
        const restartMs = parseInt(gif.getAttribute('data-restart-ms') || '3000', 10);
        if (gifRestartIntervalId) clearInterval(gifRestartIntervalId);
        gifRestartIntervalId = setInterval(() => {
            const src = gif.getAttribute('src');
            gif.setAttribute('src', '');
            setTimeout(() => gif.setAttribute('src', src), 0);
        }, Math.max(1500, restartMs));
    };

    okBtn.addEventListener('click', handleOk);
    modalEl.addEventListener('hidden.bs.modal', cleanup);
    modalEl.addEventListener('shown.bs.modal', handleShown);
    modal.show();
}