// Main JavaScript for BuddySkincare Website

// Generate random discount for LOVEBUDDY (5,000 - 15,000 VND)
function generateRandomDiscount() {
    // Generate random number from 5 to 15, then multiply by 1000
    const randomNumber = Math.floor(Math.random() * 11) + 5; // 5 to 15
    const discount = randomNumber * 1000; // 5,000 to 15,000
    return discount;
}

// Fetch voucher by code from backend API
async function fetchVoucherFromAPI(code){
    try{
        const res = await fetch('https://buddyskincare.pythonanywhere.com/vouchers/');
        if(!res.ok) return null;
        const list = await res.json();
        const found = (list||[]).find(v => (v.code||'').toUpperCase() === String(code||'').toUpperCase());
        return found || null;
    }catch(e){
        console.error('Voucher API error:', e);
        return null;
    }
}

// Save voucher to localStorage
function saveVoucher(voucher) {
    localStorage.setItem('appliedVoucher', JSON.stringify(voucher));
}

// Get voucher from localStorage
function getAppliedVoucher() {
    const voucher = localStorage.getItem('appliedVoucher');
    return voucher ? JSON.parse(voucher) : null;
}

// Clear voucher
function clearVoucher() {
    localStorage.removeItem('appliedVoucher');
}

// Clear voucher display
function clearVoucherDisplay(isCheckout = false) {
    const prefix = isCheckout ? 'checkout' : 'cart';
    const messageEl = document.getElementById(`${prefix}VoucherMessage`);
    const appliedEl = document.getElementById(`${prefix}VoucherApplied`);
    const voucherLineEl = document.getElementById(`${prefix}VoucherLine`);
    const codeInput = document.getElementById(`${prefix}VoucherCode`);
    
    // Clear input field
    if (codeInput) codeInput.value = '';
    
    // Hide applied voucher section
    if (appliedEl) appliedEl.classList.add('d-none');
    
    // Hide voucher line in summary and reset discount to 0đ
    if (voucherLineEl) {
        voucherLineEl.style.display = 'none';
    }
    
    // Reset voucher discount to 0đ
    const voucherDiscountEl = document.querySelector(`.${prefix}-voucher-discount`);
    if (voucherDiscountEl) {
        voucherDiscountEl.textContent = '-0đ';
    }
    
    // Clear message
    if (messageEl) messageEl.innerHTML = '';
    
    console.log('Voucher display cleared for:', prefix, 'discount reset to 0đ');
}

// Remove voucher
function removeVoucher(isCheckout = false) {
    console.log('=== REMOVING VOUCHER ===');
    
    // Clear voucher from localStorage
    clearVoucher();
    
    // Clear voucher display
    clearVoucherDisplay(isCheckout);
    
    // Update voucher line in summary to show 0đ
    const prefix = isCheckout ? 'checkout' : 'cart';
    const voucherLineEl = document.getElementById(`${prefix}VoucherLine`);
    const voucherDiscountEl = document.querySelector(`.${prefix}-voucher-discount`);
    
    if (voucherLineEl) {
        voucherLineEl.style.display = 'none';
    }
    
    if (voucherDiscountEl) {
        voucherDiscountEl.textContent = '-0đ';
    }
    
    // Update summary immediately
    if (isCheckout) {
        updateCheckoutSummary();
    } else {
        updateCartSummary();
        // Also sync to checkout
        syncVoucherToCheckout();
    }
    
    console.log('Voucher removed successfully, discount reset to 0đ');
}

// Apply voucher
async function applyVoucher(code, isCheckout = false) {
    const prefix = isCheckout ? 'checkout' : 'cart';
    const messageEl = document.getElementById(`${prefix}VoucherMessage`);
    const appliedEl = document.getElementById(`${prefix}VoucherApplied`);
    const nameEl = document.getElementById(`${prefix}VoucherName`);
    const discountEl = document.getElementById(`${prefix}VoucherDiscount`);
    const voucherLineEl = document.getElementById(`${prefix}VoucherLine`);
    
    // Clear previous messages
    messageEl.innerHTML = '';
    
    // Fetch voucher from API
    const voucher = await fetchVoucherFromAPI(code);
    if (!voucher) {
        messageEl.innerHTML = '<span class="text-danger"><i class="fas fa-times-circle me-1"></i>Mã giảm giá không hợp lệ</span>';
        return false;
    }

    // Validate voucher conditions
    const now = new Date();
    if (voucher.valid_from && now < new Date(voucher.valid_from)) {
        messageEl.innerHTML = '<span class="text-warning"><i class="fas fa-clock me-1"></i>Voucher chưa tới thời gian hiệu lực</span>';
        return false;
    }
    if (voucher.valid_to && now > new Date(voucher.valid_to)) {
        messageEl.innerHTML = '<span class="text-warning"><i class="fas fa-clock me-1"></i>Voucher đã hết hạn</span>';
        return false;
    }
    if (voucher.is_active === false) {
        messageEl.innerHTML = '<span class="text-warning"><i class="fas fa-ban me-1"></i>Voucher đang ngưng hoạt động</span>';
        return false;
    }
    
    // Check minimum order (if needed)
    const cart = JSON.parse(localStorage.getItem('cart') || '[]');
    let subtotal = 0;
    cart.forEach(item => {
        const price = parsePrice(item.price);
        subtotal += price * item.quantity;
    });
    
    const minOrder = Math.max(0, parseFloat(voucher.min_order_amount || '0')) * 1000;
    if (subtotal < minOrder) {
        messageEl.innerHTML = `<span class="text-warning"><i class="fas fa-exclamation-triangle me-1"></i>Đơn hàng tối thiểu ${minOrder.toLocaleString('vi-VN')}đ</span>`;
        return false;
    }
    // Check remaining uses
    const maxUses = parseInt(voucher.max_uses || 0, 10);
    const timesUsed = parseInt(voucher.times_used || 0, 10);
    if (maxUses && timesUsed >= maxUses) {
        messageEl.innerHTML = '<span class="text-warning"><i class="fas fa-exclamation-triangle me-1"></i>Voucher đã hết lượt sử dụng</span>';
        return false;
    }
    
    // Check if there's already a voucher applied
    const existingVoucher = getAppliedVoucher();
    if (existingVoucher) {
        console.log('Replacing existing voucher:', existingVoucher.code, 'with new voucher:', voucher.code);
        // Clear old voucher display first
        clearVoucherDisplay(isCheckout);
    }
    
    // Compute discount amount
    let discountAmount = 0;
    if ((voucher.discount_type || '').toLowerCase() === 'percentage') {
        const percent = Math.max(0, parseFloat(voucher.discount_value || '0'));
        discountAmount = Math.floor(subtotal * (percent / 100));
        const cap = Math.max(0, parseFloat(voucher.max_order_amount || '0')) * 1000;
        if (cap > 0) discountAmount = Math.min(discountAmount, cap);
    } else {
        // amount is stored in thousands
        discountAmount = Math.max(0, parseFloat(voucher.discount_value || '0')) * 1000;
    }
    const applied = {
        id: voucher.id,
        code: voucher.code,
        discount: discountAmount,
        type: (voucher.discount_type||'amount').toLowerCase(),
        minOrder: minOrder
    };
    
    // Apply voucher
    saveVoucher(applied);
    
    // Update UI
    nameEl.textContent = applied.code;
    discountEl.textContent = `-${applied.discount.toLocaleString('vi-VN')}đ`;
    appliedEl.classList.remove('d-none');
    voucherLineEl.style.display = 'flex';
    
    messageEl.innerHTML = '<span class="text-success"><i class="fas fa-check-circle me-1"></i>Áp dụng thành công!</span>';
    
    // Update summary
    if (isCheckout) {
        updateCheckoutSummary();
    } else {
        updateCartSummary();
        // Also sync to checkout if user goes there
        syncVoucherToCheckout();
    }
    
    return true;
}

// Sync voucher display to checkout
function syncVoucherToCheckout() {
    const voucher = getAppliedVoucher();
    const checkoutCodeEl = document.getElementById('checkoutVoucherCode');
    const checkoutAppliedEl = document.getElementById('checkoutVoucherApplied');
    const checkoutNameEl = document.getElementById('checkoutVoucherName');
    const checkoutDiscountEl = document.getElementById('checkoutVoucherDiscount');
    const checkoutVoucherLineEl = document.getElementById('checkoutVoucherLine');
    
    if (voucher && checkoutCodeEl) {
        checkoutCodeEl.value = voucher.code;
        if (checkoutNameEl) checkoutNameEl.textContent = voucher.code;
        if (checkoutDiscountEl) checkoutDiscountEl.textContent = `-${voucher.discount.toLocaleString('vi-VN')}đ`;
        if (checkoutAppliedEl) checkoutAppliedEl.classList.remove('d-none');
        if (checkoutVoucherLineEl) checkoutVoucherLineEl.style.display = 'flex';
    } else {
        // Clear voucher display if no voucher
        clearVoucherDisplay(true);
    }
}

// Sync voucher display to cart
function syncVoucherToCart() {
    const voucher = getAppliedVoucher();
    const cartCodeEl = document.getElementById('cartVoucherCode');
    const cartAppliedEl = document.getElementById('cartVoucherApplied');
    const cartNameEl = document.getElementById('cartVoucherName');
    const cartDiscountEl = document.getElementById('cartVoucherDiscount');
    const cartVoucherLineEl = document.getElementById('cartVoucherLine');
    
    if (voucher && cartCodeEl) {
        cartCodeEl.value = voucher.code;
        if (cartNameEl) cartNameEl.textContent = voucher.code;
        if (cartDiscountEl) cartDiscountEl.textContent = `-${voucher.discount.toLocaleString('vi-VN')}đ`;
        if (cartAppliedEl) cartAppliedEl.classList.remove('d-none');
        if (cartVoucherLineEl) cartVoucherLineEl.style.display = 'flex';
    } else {
        // Clear voucher display if no voucher
        clearVoucherDisplay(false);
    }
}

// Initialize voucher events
function initVoucherEvents() {
    // Cart voucher events
    const cartApplyBtn = document.getElementById('applyCartVoucher');
    const cartCodeInput = document.getElementById('cartVoucherCode');
    const cartRemoveBtn = document.getElementById('removeCartVoucher');
    
    if (cartApplyBtn && cartCodeInput) {
        cartApplyBtn.addEventListener('click', () => {
            const code = cartCodeInput.value.trim();
            if (code) {
                applyVoucher(code, false);
            }
        });
        
        cartCodeInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                const code = cartCodeInput.value.trim();
                if (code) {
                    applyVoucher(code, false);
                }
            }
        });
    }
    
    // Cart remove voucher button
    if (cartRemoveBtn) {
        cartRemoveBtn.addEventListener('click', () => {
            removeVoucher(false);
        });
    }
    
    // Checkout voucher events
    const checkoutApplyBtn = document.getElementById('applyCheckoutVoucher');
    const checkoutCodeInput = document.getElementById('checkoutVoucherCode');
    const checkoutRemoveBtn = document.getElementById('removeCheckoutVoucher');
    
    if (checkoutApplyBtn && checkoutCodeInput) {
        checkoutApplyBtn.addEventListener('click', () => {
            const code = checkoutCodeInput.value.trim();
            if (code) {
                applyVoucher(code, true);
            }
        });
        
        checkoutCodeInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                const code = checkoutCodeInput.value.trim();
                if (code) {
                    applyVoucher(code, true);
                }
            }
        });
    }
    
    // Checkout remove voucher button
    if (checkoutRemoveBtn) {
        checkoutRemoveBtn.addEventListener('click', () => {
            removeVoucher(true);
        });
    }
    
    // Load saved voucher on page load
    syncVoucherToCart();
    syncVoucherToCheckout();
}

// Helper function to parse price accurately
function parsePrice(priceString) {
    if (!priceString) return 0;
    
    // If it's already a number, return it
    if (typeof priceString === 'number') {
        return priceString;
    }
    
    // If it's not a string, convert to string first
    const priceStr = String(priceString);
    
    // Remove all non-numeric characters except dots and commas, then remove dots and commas
    const cleanPrice = priceStr.replace(/[^\d,.]/g, '').replace(/[,.]/g, '');
    const result = parseInt(cleanPrice, 10) || 0;
    console.log(`parsePrice: "${priceString}" -> "${cleanPrice}" -> ${result}`);
    return result;
}

// Initialize cart when page loads
function initCart() {
    console.log('=== INITIALIZING CART ===');
    
    // Detect current page
    const cartPaymentInputs = document.querySelectorAll('input[name="paymentMethod"]');
    const checkoutPaymentInputs = document.querySelectorAll('input[name="pay"]');
    
    const isCartPage = cartPaymentInputs.length > 0;
    const isCheckoutPage = checkoutPaymentInputs.length > 0;
    
    console.log('Page detection:');
    console.log('- Is Cart Page:', isCartPage);
    console.log('- Is Checkout Page:', isCheckoutPage);
    console.log('Found elements:');
    console.log('- Cart payment inputs:', cartPaymentInputs.length);
    console.log('- Checkout payment inputs:', checkoutPaymentInputs.length);
    
    if (cartPaymentInputs.length > 0) {
        console.log('Cart payment input values:', Array.from(cartPaymentInputs).map(input => input.value));
        console.log('Cart payment input checked states:', Array.from(cartPaymentInputs).map(input => input.checked));
    }
    if (checkoutPaymentInputs.length > 0) {
        console.log('Checkout payment input values:', Array.from(checkoutPaymentInputs).map(input => input.value));
        console.log('Checkout payment input checked states:', Array.from(checkoutPaymentInputs).map(input => input.checked));
    }
    
    // Update cart count badges
    updateCartCount();
    
    if (isCartPage) {
        console.log('Initializing cart page...');
        
        // Debug: Check if cart elements are actually visible
        const cartContainer = document.querySelector('#cart-items-container');
        const cartSummary = document.querySelector('.col-lg-4');
        console.log('Cart elements found:');
        console.log('- Cart items container:', !!cartContainer);
        console.log('- Cart summary column:', !!cartSummary);
        
        // Update cart display if on cart page
        updateCartDisplay();
        
        // Add event listeners for cart payment methods
        initCartPaymentEvents();
    }
    
    if (isCheckoutPage) {
        console.log('Initializing checkout page...');
        
        // Debug: Check if checkout elements are actually visible
        const checkoutContainer = document.querySelector('#checkout-items-container');
        const checkoutSummary = document.querySelector('.col-lg-4');
        console.log('Checkout elements found:');
        console.log('- Checkout items container:', !!checkoutContainer);
        console.log('- Checkout summary column:', !!checkoutSummary);
        
        // Update checkout display if on checkout page
        updateCheckoutDisplay();
        
        // Add event listeners for checkout page
        initCheckoutEvents();
    }
    
    // Initialize voucher events (works on both pages)
    initVoucherEvents();
    
    // Debug: Check current payment method status
    const currentPaymentMethod = getPaymentMethod();
    console.log('Current payment method from localStorage:', currentPaymentMethod);
    
    // Sync payment method from cart to checkout with delay to ensure DOM is ready
    setTimeout(() => {
        console.log('First sync attempt...');
        syncPaymentMethod();
        // Retry after a longer delay to ensure everything is loaded
        setTimeout(() => {
            console.log('Retrying payment method sync in cart...');
            syncPaymentMethod();
        }, 500);
    }, 200);
}

// Initialize checkout page events
function initCheckoutEvents() {
    console.log('=== INITIALIZING CHECKOUT EVENTS ===');
    
    // Handle shipping method change
    const shippingRadios = document.querySelectorAll('input[name="ship"]');
    console.log('Found shipping radios:', shippingRadios.length);
    shippingRadios.forEach(radio => {
        radio.addEventListener('change', updateCheckoutSummary);
    });
    
    // Handle payment method change
    const paymentRadios = document.querySelectorAll('input[name="pay"]');
    console.log('Found payment radios:', paymentRadios.length);
    paymentRadios.forEach(radio => {
        radio.addEventListener('change', handlePaymentMethodChange);
    });
    
    // Handle place order button
    const placeOrderBtn = document.getElementById('place-order-btn');
    if (placeOrderBtn) {
        placeOrderBtn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            handlePlaceOrder();
        });
    }
    // Also handle form submit if there's a checkout form
    const checkoutForm = document.getElementById('checkoutForm');
    if (checkoutForm) {
        checkoutForm.addEventListener('submit', function(e) {
            e.preventDefault();
            e.stopPropagation();
            // Only call if not already processing
            if (!isOrderBeingProcessed) {
            handlePlaceOrder();
            }
        });
    }
    
    // Initialize payment method display
    handlePaymentMethodChange();
    
    // Auto-select saved payment method
    const savedPaymentMethod = getPaymentMethod();
    console.log('Saved payment method in checkout:', savedPaymentMethod);
    
    // Debug: Check all available payment radios
    const allPaymentRadios = document.querySelectorAll('input[name="pay"]');
    console.log('All payment radios found:', allPaymentRadios.length);
    allPaymentRadios.forEach((radio, index) => {
        console.log(`Radio ${index}: value="${radio.value}", checked=${radio.checked}`);
    });
    
    const paymentRadio = document.querySelector(`input[name="pay"][value="${savedPaymentMethod}"]`);
    if (paymentRadio) {
        console.log('Auto-selecting payment method:', savedPaymentMethod);
        console.log('Found radio button:', paymentRadio.outerHTML);
        
        // Force uncheck all first
        console.log('Unchecking all radios...');
        document.querySelectorAll('input[name="pay"]').forEach(radio => {
            radio.checked = false;
            console.log(`Unchecked radio ${radio.value}:`, radio.checked);
        });
        
        // Then check the correct one
        paymentRadio.checked = true;
        console.log('Radio button checked:', paymentRadio.checked);
        console.log('Radio button HTML after check:', paymentRadio.outerHTML);
        
        // Verify the selection
        const verifiedRadio = document.querySelector(`input[name="pay"][value="${savedPaymentMethod}"]`);
        console.log('Verification - Radio still checked:', verifiedRadio?.checked);
        
        // Force trigger change event after a small delay
        setTimeout(() => {
            console.log('Force triggering change event...');
            paymentRadio.dispatchEvent(new Event('change', { bubbles: true }));
        }, 100);
        
        handlePaymentMethodChange();
    } else {
        console.log('Payment radio not found for:', savedPaymentMethod);
        console.log('Available values:', Array.from(allPaymentRadios).map(r => r.value));
    }
    
    // Initialize checkout summary with current values
    updateCheckoutSummary();
    
    // Sync payment method from cart with delay to ensure DOM is ready
    setTimeout(() => {
        console.log('First checkout sync attempt...');
        syncPaymentMethod();
        // Retry after a longer delay to ensure everything is loaded
        setTimeout(() => {
            console.log('Retrying payment method sync in checkout...');
            syncPaymentMethod();
        }, 500);
    }, 200);
    
    // Force sync one more time after everything is initialized
    setTimeout(() => {
        console.log('Final force sync attempt...');
        syncPaymentMethod();
    }, 1000);
    
    // Initialize suggested products
    initCheckoutSuggestedProducts();
}

// Handle payment method change
function handlePaymentMethodChange() {
    console.log('=== CHECKOUT PAYMENT METHOD CHANGED ===');
    
    const selectedPayment = document.querySelector('input[name="pay"]:checked');
    const bankTransferSection = document.getElementById('bankTransferSection');
    
    console.log('Selected payment method:', selectedPayment?.value);
    console.log('Bank transfer section element found:', !!bankTransferSection);
    console.log('Bank transfer section current display:', bankTransferSection?.style.display);
    
    if (selectedPayment && selectedPayment.value === 'bankTransfer') {
        console.log('Showing bank transfer section');
        bankTransferSection.classList.remove('d-none');
        console.log('Bank transfer section display after show:', bankTransferSection?.style.display);
        console.log('Bank transfer section classes after show:', bankTransferSection?.className);
    } else {
        console.log('Hiding bank transfer section');
        bankTransferSection.classList.add('d-none');
        console.log('Bank transfer section display after hide:', bankTransferSection?.style.display);
    }
    
    // Save selected payment method
    if (selectedPayment) {
        savePaymentMethod(selectedPayment.value);
        console.log('Payment method saved to localStorage:', selectedPayment.value);
    } else {
        console.log('No payment method selected, cannot save');
    }
    
    // Update checkout summary when payment method changes
    updateCheckoutSummary();
    
    console.log('=== CHECKOUT PAYMENT METHOD CHANGE COMPLETED ===');
}

// Initialize cart payment method events
function initCartPaymentEvents() {
    console.log('=== INITIALIZING CART PAYMENT EVENTS ===');
    
    const paymentRadios = document.querySelectorAll('input[name="paymentMethod"]');
    console.log('Found cart payment radios:', paymentRadios.length);
    
    if (paymentRadios.length === 0) {
        console.error('No cart payment radios found! This should not happen on cart page.');
        return;
    }
    
    paymentRadios.forEach((radio, index) => {
        console.log(`Adding event listener to radio ${index}:`, radio.value, radio.checked);
        radio.addEventListener('change', handleCartPaymentChange);
    });
    
    // Initialize bank transfer info display
    console.log('Calling handleCartPaymentChange to initialize display...');
    handleCartPaymentChange();
    
    // Add event listener to checkout button to sync payment method
    const checkoutBtn = document.getElementById('checkoutBtn');
    if (checkoutBtn) {
        console.log('Checkout button found, adding event listener');
        checkoutBtn.addEventListener('click', function(e) {
            console.log('=== CHECKOUT BUTTON CLICKED ===');
            // Force save current payment method
            const selectedPayment = document.querySelector('input[name="paymentMethod"]:checked');
            if (selectedPayment) {
                console.log('Force saving payment method:', selectedPayment.value);
                savePaymentMethod(selectedPayment.value);
            } else {
                console.log('No payment method selected in cart');
            }
            // Sync payment method before navigation
            syncPaymentMethod();
            console.log('Payment method synced, proceeding to checkout...');
        });
    } else {
        console.log('Checkout button not found');
    }
}

// Sync payment method between cart and checkout
function syncPaymentMethod() {
    console.log('=== SYNCING PAYMENT METHOD ===');
    
    // Auto-sync from cart to checkout
    const savedPaymentMethod = getPaymentMethod();
    console.log('Saved payment method:', savedPaymentMethod);
    
    // Debug: Check all available radio buttons
    const allCartRadios = document.querySelectorAll('input[name="paymentMethod"]');
    const allCheckoutRadios = document.querySelectorAll('input[name="pay"]');
    console.log('Found cart radios:', allCartRadios.length);
    console.log('Found checkout radios:', allCheckoutRadios.length);
    
    // Update cart payment method
    const cartPaymentRadio = document.querySelector(`input[name="paymentMethod"][value="${savedPaymentMethod}"]`);
    if (cartPaymentRadio) {
        console.log('Updating cart payment method to:', savedPaymentMethod);
        cartPaymentRadio.checked = true;
        handleCartPaymentChange();
    } else {
        console.log('Cart payment radio not found for:', savedPaymentMethod);
        console.log('Available cart values:', Array.from(allCartRadios).map(r => r.value));
    }
    
    // Update checkout payment method
    const checkoutPaymentRadio = document.querySelector(`input[name="pay"][value="${savedPaymentMethod}"]`);
    if (checkoutPaymentRadio) {
        console.log('Updating checkout payment method to:', savedPaymentMethod);
        console.log('Found checkout radio button:', checkoutPaymentRadio.outerHTML);
        
        // Force uncheck all first
        const allCheckoutRadios = document.querySelectorAll('input[name="pay"]');
        console.log('Unchecking all checkout radios...');
        allCheckoutRadios.forEach(radio => {
            radio.checked = false;
        });
        
        // Then check the correct one
        checkoutPaymentRadio.checked = true;
        console.log('Checkout radio button checked:', checkoutPaymentRadio.checked);
        
        handlePaymentMethodChange();
    } else {
        console.log('Checkout payment radio not found for:', savedPaymentMethod);
        console.log('Available checkout values:', Array.from(checkoutPaymentInputs).map(input => input.value));
    }
    
    console.log('=== PAYMENT METHOD SYNCED ===');
}

// Handle cart payment method change
// Handle place order
// Global flag to prevent multiple order submissions
let isOrderBeingProcessed = false;

async function handlePlaceOrder() {
    console.log('[Checkout] handlePlaceOrder invoked');
    
    // Prevent multiple submissions
    if (isOrderBeingProcessed) {
        console.log('[Checkout] Blocked: order already being processed');
        return;
    }
    
    const cart = JSON.parse(localStorage.getItem('cart') || '[]');
    
    if (cart.length === 0) {
        console.log('[Checkout] Blocked: cart is empty');
        return;
    }
    
    // Get button reference but don't set loading yet
    const placeOrderBtn = document.getElementById('place-order-btn');

    const isCheckoutPage = document.querySelector('input[name="pay"]') !== null;
    if (isCheckoutPage) {
        const formRoot = document.getElementById('checkoutForm') || document;
        // Clear previous invalid states
        formRoot.querySelectorAll('.is-invalid').forEach(el => clearInvalidField(el));

        // Prefer explicit known fields
        const explicitIds = ['fullName','phone','city','shippingAddress'];
        let requiredEls = explicitIds
            .map(id => formRoot.querySelector(`#${id}`) || formRoot.querySelector(`[name="${id}"]`))
            .filter(Boolean);

        // Fallback to generic required markers if explicit not found
        if (requiredEls.length === 0) {
            requiredEls = Array.from(formRoot.querySelectorAll('[required], .checkout-required'))
                .filter(el => el.type !== 'email' && !/email/i.test(el.name || el.id || '') && !/ghi chu|note|message/i.test(el.name || el.id || ''));
        }

        let hasInvalid = false;
        let firstInvalid = null;
        requiredEls.forEach(el => {
            const val = (el.value || '').toString().trim();
            if (!val) {
                hasInvalid = true;
                if (!firstInvalid) firstInvalid = el;
                console.log('[Checkout] Missing field:', el.id || el.name || el.placeholder || el.outerHTML);
                markInvalidField(el);
                const handler = () => clearInvalidField(el);
                el.addEventListener('input', handler, { once: true });
                el.addEventListener('change', handler, { once: true });
            }
        });

        // Bank transfer proof only if element exists and method is bankTransfer
        const selectedPay = document.querySelector('input[name="pay"]:checked');
        let bankTransferImageUrl = null;
        
        if (selectedPay && selectedPay.value === 'bankTransfer') {
            const proofInput = document.getElementById('transferProof')
                || document.getElementById('bankTransferProof')
                || document.querySelector('#bankTransferSection input[type="file"]')
                || null; // do not search too wide; if null, don't block
            if (proofInput) {
                const hasFile = proofInput.files && proofInput.files.length > 0;
                if (!hasFile) {
                    hasInvalid = true;
                    if (!firstInvalid) firstInvalid = proofInput;
                    console.log('[Checkout] Missing bank transfer proof file');
                    markInvalidField(proofInput, 'Vui lòng tải ảnh/bằng chứng chuyển khoản', { marginLeft: '20px', marginBottom: '5px' });
                    proofInput.addEventListener('change', () => clearInvalidField(proofInput), { once: true });
                } else {
                    // Upload bank transfer image to Cloudinary
                    try {
                        console.log('[Checkout] Uploading bank transfer image...');
                        const uploadFormData = new FormData();
                        uploadFormData.append('file', proofInput.files[0]);
                        
                        const uploadResponse = await fetch('/api/upload-bank-transfer', {
                            method: 'POST',
                            body: uploadFormData
                        });
                        
                        if (uploadResponse.ok) {
                            const uploadResult = await uploadResponse.json();
                            bankTransferImageUrl = uploadResult.url;
                            console.log('[Checkout] Bank transfer image uploaded successfully:', bankTransferImageUrl);
                        } else {
                            const errorResult = await uploadResponse.json();
                            console.error('[Checkout] Failed to upload bank transfer image:', errorResult);
                            showNotification('Lỗi upload ảnh chuyển khoản: ' + (errorResult.error || 'Unknown error'), 'error');
                            return;
                        }
                    } catch (uploadError) {
                        console.error('[Checkout] Error uploading bank transfer image:', uploadError);
                        showNotification('Lỗi upload ảnh chuyển khoản: ' + uploadError.message, 'error');
                        return;
                    }
                }
            }
        }

        if (hasInvalid) {
            console.log('[Checkout] Blocked: has invalid fields');
            firstInvalid && firstInvalid.scrollIntoView({ behavior: 'smooth', block: 'center' });
            return;
        }

        // Collect form data for API
        const shippingAddress = (document.getElementById('shippingAddress')?.value || '').trim();
        const orderNote = (document.getElementById('orderNote')?.value || '').trim();
        
        const appliedVoucher = getAppliedVoucher();
        const formData = {
            customer_name: (document.getElementById('fullName')?.value || '').trim(),
            phone_number: (document.getElementById('phone')?.value || '').trim(),
            email: (document.getElementById('email')?.value || '').trim(),
            street: shippingAddress, // Full address including ward/district info
            ward: '', // Not available in current form - could be parsed from shippingAddress if needed
            district: '', // Not available in current form - could be parsed from shippingAddress if needed  
            province: (document.getElementById('city')?.value || '').trim(),
            payment_method: selectedPay?.value === 'bankTransfer' ? 'bank' : (selectedPay?.value || 'cod')
        };

        // Only add optional fields if they have values
        if (appliedVoucher && appliedVoucher.code) {
            formData.voucher_code = appliedVoucher.code;
        }
        if (orderNote && orderNote.trim()) {
            formData.notes = orderNote.trim();
        }

        // Prepare items data
        const items_data = cart.map(item => ({
            product: item.id,
            quantity: item.quantity
        }));

        // Get shipping fee from checkout-shipping field
        const shippingFeeInput = formRoot.querySelector('#checkout-shipping') || formRoot.querySelector('[name="checkout-shipping"]');
        const shipping_fee = shippingFeeInput ? parseFloat(shippingFeeInput.value) || 0 : 0;

        const orderData = {
            ...formData,
            items_data: items_data,
            shipping_fee: shipping_fee
        };

        // Add bank transfer image URL if available
        if (bankTransferImageUrl) {
            orderData.bank_transfer_image = bankTransferImageUrl;
        }

        // Validate required fields before sending
        if (!formData.customer_name || !formData.phone_number || !formData.street || !formData.province) {
            showNotification('Vui lòng điền đầy đủ thông tin bắt buộc.', 'error');
            return;
        }

        // Validate items data
        if (!items_data || items_data.length === 0) {
            showNotification('Giỏ hàng trống. Vui lòng thêm sản phẩm trước khi đặt hàng.', 'error');
            return;
        }

        console.log('[Checkout] Sending order data:', orderData);
        console.log('[Checkout] Items count:', items_data.length);
        console.log('[Checkout] Customer:', formData.customer_name);
        console.log('[Checkout] Phone:', formData.phone_number);
        console.log('[Checkout] Payment method:', formData.payment_method);
        console.log('[Checkout] Shipping fee:', shipping_fee);
        console.log('[Checkout] Voucher applied:', appliedVoucher ? appliedVoucher.code : 'None');
        console.log('[Checkout] Order note:', orderNote || 'None');

        // Set processing flag and disable button only when data is valid
        isOrderBeingProcessed = true;
        if (placeOrderBtn) {
            placeOrderBtn.disabled = true;
            placeOrderBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Đang xử lý...';
        }

        try {

            // Send order to API
            const response = await fetch('https://buddyskincare.pythonanywhere.com/orders/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(orderData)
            });

            if (response.ok) {
                const result = await response.json();
                console.log('[Checkout] Order created successfully:', result);
    
                // Send email notification to admin
                try {
                    await notifyAdminNewOrder(result.id);
                } catch (e) {
                    console.warn('Failed to send order notification email:', e);
                }
    
    // Success flow: show pretty modal, then clear and redirect on OK
    showOrderSuccessModal(() => {
        // Clear cart
        localStorage.removeItem('cart');
        localStorage.setItem('cartCount', '0');

        // Clear voucher and its UI
        try {
            clearVoucher();
            clearVoucherDisplay(false);
            clearVoucherDisplay(true);
        } catch (e) {}

        // Redirect
        window.location.href = '/';
    });
                // After success: update voucher usage if applied
                try {
                    const appliedVoucher = getAppliedVoucher();
                    if (appliedVoucher && appliedVoucher.id) {
                        const usageRes = await fetch(`https://buddyskincare.pythonanywhere.com/vouchers/${appliedVoucher.id}/`, {
                            method: 'PATCH',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                max_uses: undefined, // backend ignores undefined
                                times_used: (appliedVoucher.times_used || 0) + 1
                            })
                        });
                        console.log('Voucher usage update status:', usageRes.status);
                    }
                } catch (e) {
                    console.warn('Voucher usage update failed:', e);
                }
            } else {
                const errorData = await response.json();
                console.error('[Checkout] Order creation failed:', errorData);
                console.error('[Checkout] Response status:', response.status);
                
                // Show specific error message if available
                
                if (response.status === 400) {
                    // Handle validation errors
                    if (errorData.voucher_code) {
                        errorMessage = 'Mã voucher không hợp lệ. Vui lòng kiểm tra lại.';
                    } else if (errorData.items_data) {
                        errorMessage = 'Thông tin sản phẩm không hợp lệ. Vui lòng thử lại.';
                    } else if (errorData.customer_name) {
                        errorMessage = 'Tên khách hàng không hợp lệ.';
                    } else if (errorData.phone_number) {
                        errorMessage = 'Số điện thoại không hợp lệ.';
                    } else if (errorData.email) {
                        errorMessage = 'Email không hợp lệ.';
                    } 
                } else if (errorData.detail) {
                    errorMessage = errorData.detail;
                } else if (errorData.message) {
                    errorMessage = errorData.message;
                } else if (errorData.error) {
                    errorMessage = errorData.error;
                }
                
                showNotification(errorMessage, 'error');
            }
        } catch (error) {
            console.error('[Checkout] Network error:', error);
        } finally {
            // Reset button state and processing flag
            if (placeOrderBtn) {
                placeOrderBtn.disabled = false;
                placeOrderBtn.innerHTML = 'Đặt hàng';
            }
            isOrderBeingProcessed = false;
        }
    } else {
        // For non-checkout pages, just show success modal
        showOrderSuccessModal(() => {
            // Clear cart
            localStorage.removeItem('cart');
            localStorage.setItem('cartCount', '0');

            // Clear voucher and its UI
            try {
                clearVoucher();
                clearVoucherDisplay(false);
                clearVoucherDisplay(true);
            } catch (e) {}

            // Redirect
            window.location.href = '/';
        });
    }
}

// Initialize additional features
document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components
    initCountdownTimer();
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
    initFeaturedProducts(); // Khởi tạo sản phẩm nổi bật
    initCart(); // Khởi tạo giỏ hàng
    initProductsPage(); // Khởi tạo trang danh sách sản phẩm động
    (typeof defineProductDetailInit === 'function' ? defineProductDetailInit : () => {})(); // Khởi tạo trang chi tiết nếu có
    initRelatedProducts(); // Khởi tạo sản phẩm liên quan

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

    // SAFETY: allow normal anchor navigation (avoid accidental preventDefault from other handlers)
    document.addEventListener('click', function(e) {
        const anchor = e.target.closest('a[href]');
        if (!anchor) return;
        const href = anchor.getAttribute('href') || '';
        // Only interfere for real navigations (absolute/relative paths), not hash or JS links
        const isHash = href.startsWith('#') || href.startsWith('javascript:');
        if (!isHash) {
            // Stop other handlers that might call preventDefault; do NOT prevent default here
            e.stopImmediatePropagation();
        }
    }, true);

    // SAFETY: if any full-screen overlay accidentally remains, disable pointer events after 5s
    setTimeout(() => {
        document.querySelectorAll('.overlay, .loading, .loader, [data-overlay]')
            .forEach(el => { el.style.pointerEvents = 'none'; el.style.opacity = '0.001'; });
    }, 5000);
    
    // Force sync payment method after page is fully loaded
    window.addEventListener('load', function() {
        console.log('=== PAGE FULLY LOADED ===');
        setTimeout(() => {
            console.log('Force syncing payment method after page load...');
            syncPaymentMethod();
        }, 300);
    });
});

// --- Dynamic Products Section ---

// Hàm chung để fetch và render sản phẩm
async function fetchAndRenderProducts(apiUrl, containerSelector, cardFunction = createProductCard, viewAllButton = null) {
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

        // Tạo wrapper cho carousel
        const carouselWrapper = document.createElement('div');
        carouselWrapper.className = 'position-relative';
        carouselWrapper.style.overflow = 'hidden';
        carouselWrapper.style.padding = '10px 40px'; // Giảm padding dọc từ 30px xuống 5px để tránh cắt nút
        
        // Tạo container cho sản phẩm (1 hàng, không xuống dòng)
        const productsContainer = document.createElement('div');
        productsContainer.className = 'homepage-products';
        productsContainer.style.display = 'flex';
        productsContainer.style.flexWrap = 'nowrap';
        productsContainer.style.gap = '16px';
        productsContainer.style.transition = 'transform 0.4s ease';
        productsContainer.style.willChange = 'transform';
        productsContainer.id = `${containerSelector.replace('#', '')}-products`;
        productsContainer.dataset.currentIndex = '0';
        productsContainer.dataset.totalProducts = String(products.length);
        productsContainer.dataset.productsPerView = '5';

        const productsPerView = 5;
        // Tạo tất cả sản phẩm; width sẽ được tính theo pixel trong layoutSlider()
        products.forEach(product => {
            const item = document.createElement('div');
            item.className = 'slider-item';
            item.style.flex = '0 0 auto';
            item.style.minWidth = '0';
            item.innerHTML = cardFunction(product);
            productsContainer.appendChild(item);
        });

        carouselWrapper.appendChild(productsContainer);
        container.appendChild(carouselWrapper);

        // Thêm nút điều hướng nếu có nhiều hơn productsPerView sản phẩm
        if (products.length > productsPerView) {
            // Nút trái
            const leftBtn = document.createElement('button');
            leftBtn.className = 'btn btn-light position-absolute carousel-nav-btn carousel-left-btn';
            leftBtn.style.cssText = 'z-index: 10; border-radius: 50%; width: 40px; height: 40px; box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2); top: calc(40% - 10px); left: 20px; transform: translateY(-50%); background-color: #fff;';
            leftBtn.innerHTML = '<i class="fas fa-chevron-left"></i>';
            leftBtn.onclick = () => navigateProducts(containerSelector, 'left');
            
            // Nút phải
            const rightBtn = document.createElement('button');
            rightBtn.className = 'btn btn-light position-absolute carousel-nav-btn carousel-right-btn';
            rightBtn.style.cssText = 'z-index: 10; border-radius: 50%; width: 40px; height: 40px; box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2); top: calc(40% - 10px); right: 20px; transform: translateY(-50%); background-color: #fff;';
            rightBtn.innerHTML = '<i class="fas fa-chevron-right"></i>';
            rightBtn.onclick = () => navigateProducts(containerSelector, 'right');
            
            carouselWrapper.appendChild(leftBtn);
            carouselWrapper.appendChild(rightBtn);

            // Thêm nút "Xem tất cả" ở cuối
            const defaultButton = `
                <div class="col-12 text-center mt-4">
                    <a href="/products" class="btn btn-outline-primary">
                        <i class="fas fa-eye me-2"></i>Xem tất cả sản phẩm
                    </a>
                </div>
            `;
            const buttonHTML = viewAllButton || defaultButton;
            container.insertAdjacentHTML('beforeend', buttonHTML);

            // Cập nhật trạng thái ban đầu
            updateNavigationButtons(containerSelector, 0);
        }

        // Tính layout theo kích thước wrapper hiện tại
        layoutSlider(containerSelector);
        // Re-layout on resize (debounced)
        window.addEventListener('resize', debounce(() => layoutSlider(containerSelector), 150));

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
    const flashSaleButton = `
        
    `;
    fetchAndRenderProducts(flashSaleApiUrl, containerSelector, createFlashSaleProductCard, flashSaleButton);
}

// Hàm khởi tạo cho sản phẩm mới
function initNewProducts() {
    const newProductsApiUrl = 'https://buddyskincare.pythonanywhere.com/latest-products/';
    const containerSelector = '#new-product-products';
    fetchAndRenderProducts(newProductsApiUrl, containerSelector, createProductCard);
}

// Hàm khởi tạo cho sản phẩm nổi bật
function initFeaturedProducts() {
    const featuredProductsApiUrl = 'https://buddyskincare.pythonanywhere.com/products/?sort=sales';
    const containerSelector = '#featured-products-container';
    fetchAndRenderProducts(featuredProductsApiUrl, containerSelector, createProductCard);
}

// Hàm điều hướng sản phẩm (trượt theo trang, responsive)
function navigateProducts(containerSelector, direction) {
    const container = document.querySelector(containerSelector);
    const productsContainer = container.querySelector('.homepage-products');
    if (!productsContainer) return;
    const wrapper = productsContainer.parentElement; // carouselWrapper

    const currentIndex = parseInt(productsContainer.dataset.currentIndex || '0', 10);
    const totalProducts = parseInt(productsContainer.dataset.totalProducts || '0', 10);
    const productsPerView = parseInt(productsContainer.dataset.productsPerView || '5', 10);

    // Tính step theo chiều rộng 1 item + gap
    const firstItem = productsContainer.querySelector('.slider-item');
    const gap = 16; // Fixed gap
    const paddingX = productsPerView === 2 ? 32 : productsPerView === 3 ? 40 : 80; // Responsive padding
    const availableWidth = wrapper.clientWidth - paddingX;
    const totalGapWidth = gap * (productsPerView - 1);
    const itemWidth = firstItem ? firstItem.offsetWidth : Math.floor((availableWidth - totalGapWidth) / productsPerView);
    const step = itemWidth + gap;

    // Chỉ số bắt đầu tối đa sao cho vẫn đủ productsPerView sản phẩm trong khung nhìn
    const maxStartIndex = Math.max(0, totalProducts - productsPerView);

    let newIndex = currentIndex;
    if (direction === 'left') {
        newIndex = Math.max(0, currentIndex - 1);
    } else {
        newIndex = Math.min(maxStartIndex, currentIndex + 1);
    }

    if (newIndex !== currentIndex) {
        productsContainer.dataset.currentIndex = String(newIndex);
        const translatePx = -newIndex * step;
        productsContainer.style.transform = `translateX(${translatePx}px)`;
        updateNavigationButtons(containerSelector, newIndex);
    }
}

// Cập nhật trạng thái nút điều hướng
function updateNavigationButtons(containerSelector, currentIndex) {
    const container = document.querySelector(containerSelector);
    if (!container) return;

    const productsContainer = container.querySelector('.homepage-products');
    const totalProducts = parseInt(productsContainer?.dataset?.totalProducts || '0', 10);
    const productsPerView = parseInt(productsContainer?.dataset?.productsPerView || '5', 10);
    const maxStartIndex = Math.max(0, totalProducts - productsPerView);

    const leftBtn = container.querySelector('.carousel-left-btn');
    const rightBtn = container.querySelector('.carousel-right-btn');

    if (leftBtn) {
        leftBtn.disabled = currentIndex === 0;
        leftBtn.style.opacity = currentIndex === 0 ? '0.5' : '1';
    }
    if (rightBtn) {
        rightBtn.disabled = currentIndex >= maxStartIndex;
        rightBtn.style.opacity = currentIndex >= maxStartIndex ? '0.5' : '1';
    }
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

// Hàm tạo HTML cho một sản phẩm (không bọc cột)
// Helper function to check if product has FlashSale tag
function isFlashSaleProduct(product) {
    try {
        const tags = product?.tags || [];
        if (Array.isArray(tags)) {
            return tags.some(t => {
                if (typeof t === 'string') return t.toLowerCase() === 'flashsale';
                if (t && typeof t === 'object') return (t.name || '').toLowerCase() === 'flashsale';
                return false;
            });
        }
        return false;
    } catch (error) {
        return false;
    }
}

function createProductCard(product) {
    // Map to backend Product model (no variants/album)
    const imageUrl = (product.image && String(product.image).trim()) || '/static/image/default-product.jpg';
    const brandName = product.brand_name || (product.brand ? product.brand.name : 'Không rõ');
    
    // Check if product has FlashSale tag
    const isFlashSale = isFlashSaleProduct(product);

    // Determine if product is new by status; otherwise it's used
    const statusText = (product.status || '').toString().toLowerCase();
    const isNewByStatus = statusText.includes('new') || statusText.includes('chiet');
    let remainingPercent = null;
    if (!isNewByStatus) {
        const m = statusText.match(/(\d{2})/);
        remainingPercent = m ? m[1] : null;
    }
    const usedLabel = !isNewByStatus
        ? (statusText.includes('test') ? 'Test 1-2 lần' : (remainingPercent ? `Còn ${remainingPercent}%` : null))
        : null;
    const newLabel = isNewByStatus ? (function(){
        if (statusText.includes('chiet')) return 'Chiết';
        if (statusText === 'new') return 'New đẹp';
        if (statusText.includes('newmh')) return 'New mất hộp';
        if (statusText.includes('newm')) return 'New móp hộp';
        if (statusText.includes('newrt')) return 'New rách tem';
        if (statusText.includes('newmn')) return 'New móp nhẹ';
        if (statusText.includes('newx')) return 'New xước nhẹ';
        if (statusText.includes('newspx')) return 'New xước';
        return 'New';
    })() : null;
    const infoLabel = isNewByStatus ? newLabel : usedLabel;

    const originalPrice = typeof product.original_price === 'number' ? product.original_price * 1000 : null;
    const discountedPrice = typeof product.discounted_price === 'number' ? product.discounted_price * 1000 : null;
    const rating = typeof product.rating === 'number' ? product.rating : (parseFloat(product.rating) || 0);
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 >= 0.5 && rating % 1 < 1;

    let starsHTML = '';
    for (let i = 0; i < fullStars; i++) starsHTML += '<i class="fas fa-star"></i>';
    if (hasHalfStar) starsHTML += '<i class="fas fa-star-half-alt"></i>';
    for (let i = fullStars + (hasHalfStar ? 1 : 0); i < 5; i++) starsHTML += '<i class="far fa-star"></i>';

    const discountRate = (typeof product.discount_rate === 'number')
        ? Math.round(product.discount_rate)
        : ((originalPrice && discountedPrice) ? Math.round(((originalPrice - discountedPrice) / originalPrice) * 100) : 0);
    const stockQuantity = typeof product.stock_quantity === 'number' ? product.stock_quantity : 0;

    const productName = product.name;

    // Check if product is out of stock
    const isOutOfStock = stockQuantity <= 0;

    const cardHTML = `
        <div class="product-card card h-100 border-0 shadow-sm ${isFlashSale ? 'flash-sale-card' : ''}" style="${isFlashSale ? 'border: 1px solid #ffc107 !important;' : ''}">
            <div class="position-relative">
                <a href="/product/${product.id}" class="text-decoration-none">
                    <img src="${imageUrl}" class="card-img-top" alt="${productName}" style="height: 220px; object-fit: cover; ${isOutOfStock ? 'filter: grayscale(100%);' : ''}">
                </a>
                ${isOutOfStock ? `
                <!-- Out of Stock Overlay -->
                <div class="position-absolute top-0 start-0 w-100 h-100 d-flex align-items-center justify-content-center" 
                     style="background-color: rgba(0,0,0,0.7); border-radius: 6px;">
                    <div class="text-center text-white">
                        <i class="fas fa-times-circle fa-2x mb-1"></i>
                        <h6 class="fw-bold mb-0">HẾT HÀNG</h6>
                    </div>
                </div>
                ` : ''}
                <button class="fav-toggle position-absolute top-0 end-0 m-2" 
                        title="Thêm vào yêu thích" 
                        data-id="${product.id}"
                        data-name="${String(productName).replace(/\"/g,'\\\"')}"
                        data-image="${imageUrl}"
                        data-brand="${String(brandName).replace(/\"/g,'\\\"')}"
                        data-price="${discountedPrice || 0}"
                        style="border:none;background:transparent;cursor:pointer;">
                    <i class="far fa-heart" style="font-size: 18px; color:#fff; text-shadow: 0 1px 3px rgba(0,0,0,0.5);"></i>
                </button>
                <div class="position-absolute bottom-0 start-0 m-1">
                    <img src="/static/image/logo.png" alt="Logo" class="product-logo" style="width: 28px; height: 28px; object-fit: contain; border-radius: 50%; background: white; padding: 2px; display: block; z-index: 10; box-shadow: 0 1px 3px rgba(0,0,0,0.2);" onerror="this.style.display='none';">
                </div>
                <div class="product-badges-row position-absolute" style="top:8px;left:10px;display:flex;gap:6px;align-items:center;z-index:2;">
                    ${isFlashSale ? 
                        `<div class="badge bg-warning text-dark flash-sale-badge" style="font-size: 10px; padding: 4px 6px;"><i class="fas fa-bolt me-1"></i>FLASH SALE</div>` : 
                        (discountRate > 0 ? `<div class=\"badge bg-danger discount-badge-left\" style=\"font-size: 11px; padding: 4px 8px;\">-${discountRate}%</div>` : '')
                    }
                    ${infoLabel ? `<div class=\"product-info-badge\" style=\"font-size: 10px; padding: 1px 6px; background:#eaf4ff; border:1px solid #b8d4ff; color:#1e56a0; border-radius:6px;\"><i class="fas fa-circle-info me-1"></i>${infoLabel}</div>` : ''}
                </div>
            </div>
            <div class="card-body d-flex flex-column">
                <h6 class="card-title fw-bold" style="font-size: 12px; line-height: 1.3; display: -webkit-box; -webkit-line-clamp: 1; -webkit-box-orient: vertical; overflow: hidden; height: 16px;">
                    <a href="/product/${product.id}" class="text-decoration-none text-dark">${productName}</a>
                </h6>
                <p class="text-muted small mb-2" style="font-size: 10px;">${brandName}${infoLabel ? ` • ${infoLabel}` : ''}</p>
                <div class="d-flex align-items-center mb-1">
                    ${originalPrice ? `<span class="text-decoration-line-through text-muted me-1" style="font-size: 11px;">${formatPrice(originalPrice)}</span>` : ''}
                    <span class="text-danger fw-bold" style="font-size: 15px;">${formatPrice(discountedPrice)}</span>
                </div>
                <div class="d-flex align-items-center mb-3">
                    <div class="stars text-warning me-2" style="font-size: 12px;">
                        ${starsHTML}
                    </div>
                    <small class="text-muted" style="font-size: 11px;">(${rating})</small>
                    <span class="badge ${isOutOfStock ? 'bg-danger' : 'bg-success'}" style="font-size: 10px; padding: 4px 8px; margin-left: 10px;">${isOutOfStock ? 'Hết hàng' : `Còn ${stockQuantity}`}</span>
                </div>
                <button class="btn w-100 add-to-cart-btn ${isOutOfStock ? 'btn-secondary' : (isFlashSale ? 'btn-warning text-dark' : 'btn-light text-dark border')}" 
                        data-product-id="${product.id}" 
                        style="font-size: 13px; padding: 8px;" 
                        ${isOutOfStock ? 'disabled' : ''}>
                    ${isOutOfStock ? 'Hết hàng' : 'Thêm vào giỏ'}
                </button>
            </div>
        </div>
    `;
    return cardHTML;
}

// Hàm tạo HTML cho Flash Sale (không bọc cột)
function createFlashSaleProductCard(product) {
    const imageUrl = (product.image && String(product.image).trim()) || '/static/image/default-product.jpg';
    const brandName = product.brand_name ? (product.brand_name || 'Không rõ') : 'Không rõ';

    const originalPrice = typeof product.original_price === 'number' ? product.original_price * 1000 : null;
    const discountedPrice = typeof product.discounted_price === 'number' ? product.discounted_price * 1000 : null;
    const rating = typeof product.rating === 'number' ? product.rating : (parseFloat(product.rating) || 0);
    const reviews = typeof product.rating !== 'undefined' ? rating : 0;

    // Map status to info label (new/used like regular cards)
    const statusText = (product.status || '').toString().toLowerCase();
    const isNewByStatus = statusText.includes('new') || statusText.includes('chiet');
    let remainingPercentFS = null;
    if (!isNewByStatus) {
        const m = statusText.match(/(\d{2})/);
        remainingPercentFS = m ? m[1] : null;
    }
    const usedLabelFS = !isNewByStatus
        ? (statusText.includes('test') ? 'Test 1-2 lần' : (remainingPercentFS ? `Còn ${remainingPercentFS}%` : null))
        : null;
    const newLabelFS = isNewByStatus ? (function(){
        if (statusText.includes('chiet')) return 'Chiết';
        if (statusText === 'new') return 'New nguyên';
        if (statusText.includes('newmh')) return 'New mất hộp';
        if (statusText.includes('newm')) return 'New móp hộp';
        if (statusText.includes('newrt')) return 'New rách tem';
        if (statusText.includes('newmn')) return 'New móp nhẹ';
        if (statusText.includes('newx')) return 'New xước nhẹ';
        if (statusText.includes('newspx')) return 'New xước';
        return 'New';
    })() : null;
    const infoLabelFS = isNewByStatus ? newLabelFS : usedLabelFS;

    let starsHTML = '';
    for (let i = 0; i < Math.floor(rating); i++) starsHTML += '<i class="fas fa-star"></i>';
    if (rating % 1 >= 0.5) starsHTML += '<i class="fas fa-star-half-alt"></i>';
    for (let i = Math.ceil(rating); i < 5; i++) starsHTML += '<i class="far fa-star"></i>';

    const discountRate = (typeof product.discount_rate === 'number')
        ? Math.round(product.discount_rate)
        : ((originalPrice && discountedPrice) ? Math.round(((originalPrice - discountedPrice) / originalPrice) * 100) : 0);
    const stockQuantity = typeof product.stock_quantity === 'number' ? product.stock_quantity : 0;
    const soldQuantity = typeof product.sold_quantity === 'number' ? product.sold_quantity : 0;
    const totalStock = stockQuantity + soldQuantity;
    const progressPercentage = totalStock > 0 ? (soldQuantity / totalStock) * 100 : 0;

    const productName = product.name;
    
    // Check if product is out of stock
    const isOutOfStock = stockQuantity <= 0;

    const cardHTML = `
        <div class="product-card card h-100 border-0 shadow-sm flash-sale-container-card">
            <div class="position-relative">
                <a href="/product/${product.id}" class="text-decoration-none">
                    <img src="${imageUrl}" class="card-img-top" alt="${productName}" style="height: 220px; object-fit: cover; ${isOutOfStock ? 'filter: grayscale(100%);' : ''}">
                </a>
                ${isOutOfStock ? `
                <!-- Out of Stock Overlay -->
                <div class="position-absolute top-0 start-0 w-100 h-100 d-flex align-items-center justify-content-center" 
                     style="background-color: rgba(0,0,0,0.7); border-radius: 6px;">
                    <div class="text-center text-white">
                        <i class="fas fa-times-circle fa-2x mb-1"></i>
                        <h6 class="fw-bold mb-0">HẾT HÀNG</h6>
                    </div>
                </div>
                ` : ''}
                <button class="fav-toggle position-absolute top-0 end-0 m-2" 
                        title="Thêm vào yêu thích" 
                        data-id="${product.id}"
                        data-name="${String(productName).replace(/\"/g,'\\\"')}"
                        data-image="${imageUrl}"
                        data-brand="${String(brandName).replace(/\"/g,'\\\"')}"
                        data-price="${discountedPrice || 0}"
                        style="border:none;background:transparent;cursor:pointer;">
                    <i class="far fa-heart" style="font-size: 18px; color:#fff; text-shadow: 0 1px 3px rgba(0,0,0,0.5);"></i>
                </button>
                <div class="position-absolute bottom-0 start-0 m-1">
                    <img src="/static/image/logo.png" alt="Logo" class="product-logo" style="width: 28px; height: 28px; object-fit: contain; border-radius: 50%; background: white; padding: 2px; display: block; z-index: 10; box-shadow: 0 1px 3px rgba(0,0,0,0.2);" onerror="this.style.display='none';">
                </div>
                <div>
                <div class="product-badges-row position-absolute" style="top: 8px; left: 10px; display:flex; gap:6px; align-items:center; z-index:2;">
                    <div class="badge bg-warning text-dark discount-badge-left" style="font-size: 10px; padding: 4px 6px;"><i class="fas fa-bolt me-1"></i>FLASH SALE</div>
                    ${infoLabelFS ? `<div class="product-info-badge" style="font-size: 10px; padding: 1px 6px; background:#eaf4ff; border:1px solid #b8d4ff; color:#1e56a0; border-radius:6px;"><i class="fas fa-circle-info me-1"></i>${infoLabelFS}</div>` : ''}
                </div>
                </div>
            </div>
            <div class="card-body d-flex flex-column">
                <h6 class="card-title fw-bold" style="font-size: 12px; line-height: 1.3; display: -webkit-box; -webkit-line-clamp: 1; -webkit-box-orient: vertical; overflow: hidden; height: 16px;">
                    <a href="/product/${product.id}" class="text-decoration-none text-dark">${productName}</a>
                </h6>
                <p class="text-muted small mb-1" style="font-size: 12px;">${brandName} <span class="text-success ms-1"><i class="fas fa-badge-check"></i> Chính hãng</span></p>
                <div class="d-flex align-items-center mb-1">
                    ${originalPrice ? `<span class="text-decoration-line-through text-muted me-1" style="font-size: 9px;">${formatPrice(originalPrice)}</span>` : ''}
                    <span class="text-danger fw-bold" style="font-size: 13px;">${formatPrice(discountedPrice)}</span>
                </div>
                <div class="d-flex align-items-center mb-1">
                    <div class="stars text-warning me-2" style="font-size: 12px;">${starsHTML}</div>
                    <small class="text-muted" style="font-size: 11px;">(${reviews})</small> 
                     ${discountRate > 0 ? `<div class="badge bg-danger position-absolute" style=" right: 20%; font-size: 11px; padding: 4px 8px;">-${discountRate}%</div>` : ''}

                </div>

                <div class="stock mb-2">
                    <div class="progress" style="height: 6px;">
                        <div class="progress-bar bg-success" role="progressbar" style="width: ${progressPercentage}%" aria-valuenow="${progressPercentage}" aria-valuemin="0" aria-valuemax="100"></div>
                    </div>
                    <div class="d-flex justify-content-between mt-1">
                        <span class="text-success" style="font-size: 11px;">Đã bán ${soldQuantity}</span>
                        <span class="${isOutOfStock ? 'text-danger' : 'text-muted'}" style="font-size: 11px;">${isOutOfStock ? 'Hết hàng' : `Còn ${stockQuantity}`}</span>
                    </div>
                </div>
                <ul class="list-unstyled mb-1" style="font-size: 11px;">
                    <li class="text-muted small"><i class="fas fa-shield-alt text-success me-1"></i>Đảm bảo chính hãng</li>
                    <li class="text-muted small"><i class="fas fa-rotate text-primary me-1"></i>Đổi trả trong 5 ngày</li>
                    <li class="text-muted small"><i class="fas fa-truck-fast text-warning me-1"></i>Giao nhanh TP.HCM</li>
                </ul>
                <button class="btn w-100 ${isOutOfStock ? 'btn-secondary' : 'btn-light text-dark border'} add-to-cart-btn" 
                        data-product-id="${product.id}" 
                        style="font-size: 13px; padding: 8px;" 
                        ${isOutOfStock ? 'disabled' : ''}>
                    ${isOutOfStock ? 'Hết hàng' : 'Thêm vào giỏ'}
                </button>
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


// Product Cards Interactions
function initProductCards() {
    // Handle both regular product cards and suggested product cards
    const productCards = document.querySelectorAll('.product-card, .suggested-product-card');
    
    productCards.forEach(card => {
        const addToCartBtn = card.querySelector('.add-to-cart-btn');
        const productImage = card.querySelector('img');
        const favBtn = card.querySelector('.fav-toggle');

        if (addToCartBtn) {
            addToCartBtn.addEventListener('click', function(e) {
                e.preventDefault();
                
                // Prevent multiple clicks
                if (this.disabled) return;
                this.disabled = true;
                
                // Get product ID
                const productId = this.getAttribute('data-product-id');
                
                // Check if this product was already added recently (within 2 seconds)
                const lastAddedKey = `lastAdded_${productId}`;
                const lastAdded = sessionStorage.getItem(lastAddedKey);
                const now = Date.now();
                
                if (lastAdded && (now - parseInt(lastAdded)) < 2000) {
                    // Product was added recently, don't add again
                    this.disabled = false;
                    return;
                }
                
                // Store the current time for this product
                sessionStorage.setItem(lastAddedKey, now.toString());

                // Get product details from the card
                let productName, productPrice, productImg, originalPrice;
                
                if (card.classList.contains('suggested-product-card')) {
                    // For suggested product cards
                    productName = card.querySelector('.card-title')?.textContent || 'Sản phẩm';
                    productPrice = card.querySelector('.text-danger')?.textContent || '0đ';
                    productImg = card.querySelector('.card-img-top')?.src || '';
                    originalPrice = card.querySelector('.text-decoration-line-through')?.textContent || null;
                } else {
                    // For regular product cards
                    productName = card.querySelector('.card-title a')?.textContent || 'Sản phẩm';
                    productPrice = card.querySelector('.text-danger')?.textContent || '0đ';
                    productImg = card.querySelector('.card-img-top')?.src || '';
                    originalPrice = card.querySelector('.text-decoration-line-through')?.textContent || null;
                }
                
                // Add product to cart
                addProductToCart(productId, productName, productPrice, productImg, originalPrice);

                // Show success notification with cart count
                const cart = JSON.parse(localStorage.getItem('cart') || '[]');
                const totalQuantity = cart.reduce((sum, item) => sum + item.quantity, 0);
                // showNotification(`Đã thêm "${productName}" vào giỏ hàng! (Tổng: ${totalQuantity} sản phẩm)`, 'success');

                // Trigger fly-to-cart animation
                flyToCart(productImage, () => {
                    // Re-enable button after animation
                    setTimeout(() => {
                        this.disabled = false;
                    }, 1000);
                });
            });
        }

        // Wishlist toggle
        if (favBtn) {
            const icon = favBtn.querySelector('i');
            const pid = String(favBtn.getAttribute('data-id'));
            const currentFavs = getWishlist();
            if (currentFavs[pid]) {
                icon.classList.remove('far');
                icon.classList.add('fas');
                icon.style.color = '#ff4d6d';
            }
            // Prevent duplicate bindings across re-renders
            if (favBtn.dataset.bound === '1') return;
            favBtn.dataset.bound = '1';
            favBtn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                const item = {
                    id: pid,
                    name: favBtn.getAttribute('data-name') || '',
                    image: favBtn.getAttribute('data-image') || '',
                    brand: favBtn.getAttribute('data-brand') || '',
                    price: parseFloat(favBtn.getAttribute('data-price') || '0') || 0
                };
                const added = toggleWishlist(item);
                if (added) {
                    icon.classList.remove('far');
                    icon.classList.add('fas');
                    icon.style.color = '#ff4d6d';
                    showNotification('Đã thêm vào yêu thích', 'success');
                } else {
                    icon.classList.remove('fas');
                    icon.classList.add('far');
                    icon.style.color = '#fff';
                    showNotification('Đã bỏ khỏi yêu thích', 'info');
                }
                renderWishlistDrawer();
            });
        }
    });
}

// --- Wishlist (Favorites) ---
function getWishlist() {
    try {
        const raw = localStorage.getItem('wishlist_v1');
        const parsed = raw ? JSON.parse(raw) : {};
        // Normalize to map shape if older data was an array
        if (Array.isArray(parsed)) {
            const map = {};
            parsed.forEach(it => {
                if (it && (it.id !== undefined && it.id !== null)) {
                    map[String(it.id)] = it;
                }
            });
            return map;
        }
        return parsed && typeof parsed === 'object' ? parsed : {};
    } catch (e) {
        return {};
    }
}

function setWishlist(map) {
    try {
        localStorage.setItem('wishlist_v1', JSON.stringify(map));
    } catch (e) {}
}

function toggleWishlist(item) {
    const map = getWishlist();
    const key = String(item.id);
    const existed = Boolean(map[key]);
    if (existed) {
        delete map[key];
    } else {
        map[key] = item;
    }
    setWishlist(map);
    updateFavBadgeCount();
    return !existed; // true if added, false if removed
}

function updateFavBadgeCount() {
    const map = getWishlist();
    const count = Object.keys(map).length;
    const fab = document.getElementById('favFab');
    if (!fab) return;
    let badge = fab.querySelector('.fav-count-badge');
    if (!badge) {
        badge = document.createElement('span');
        badge.className = 'fav-count-badge';
        badge.style.cssText = 'position:absolute;top:-6px;right:-6px;background:#fff;color:#dc3545;border:1px solid rgba(0,0,0,.05);border-radius:999px;padding:0 6px;font-size:10px;font-weight:700;line-height:18px;min-width:18px;text-align:center;';
        fab.style.position = 'relative';
        fab.appendChild(badge);
    }
    badge.textContent = String(count);
}

function renderWishlistDrawer() {
    const listEl = document.getElementById('wishlistList');
    if (!listEl) return;
    const map = getWishlist();
    const items = Object.values(map);
    if (items.length === 0) {
        listEl.innerHTML = '<div class="p-3 text-center text-muted">Chưa có sản phẩm yêu thích</div>';
        updateFavBadgeCount();
        return;
    }
    listEl.innerHTML = items.map(p => `
        <div class="d-flex align-items-center p-2 border-bottom">
            <a href="/product/${p.id}" class="me-2" style="flex:0 0 56px;">
                <img src="${p.image}" alt="${p.name}" style="width:56px;height:56px;object-fit:cover;border-radius:8px;">
            </a>
            <div class="flex-grow-1">
                <a href="/product/${p.id}" class="text-decoration-none text-dark" style="font-weight:600; display:block; line-height:1.2;">${p.name}</a>
                <div class="text-muted" style="font-size:12px;">${p.brand || ''}</div>
                <div class="text-danger" style="font-size:13px;font-weight:700;">${formatPrice(parseFloat(p.price) || 0)}</div>
            </div>
            <button class="btn btn-sm btn-outline-danger ms-2" data-remove-fav="${p.id}"><i class="fas fa-trash"></i></button>
        </div>
    `).join('');

    // Bind remove buttons
    listEl.querySelectorAll('[data-remove-fav]').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const id = btn.getAttribute('data-remove-fav');
            const map = getWishlist();
            delete map[id];
            setWishlist(map);
            showNotification('Đã xóa khỏi yêu thích', 'info');
            renderWishlistDrawer();
            // Also update any heart icon on page
            document.querySelectorAll(`.fav-toggle[data-id="${id}"] i`).forEach(ic => {
                ic.classList.remove('fas');
                ic.classList.add('far');
                ic.style.color = '#fff';
            });
        });
    });
    updateFavBadgeCount();
}

function initWishlistUI() {
    const fab = document.getElementById('favFab');
    const modalEl = document.getElementById('wishlistModal');
    const clearBtn = document.getElementById('favClearBtn');
    if (!fab || !modalEl) return;

    const bsModal = () => (window.bootstrap ? new bootstrap.Modal(modalEl) : null);

    fab.addEventListener('click', (e) => {
        e.preventDefault();
        renderWishlistDrawer();
        const inst = bsModal();
        if (inst) inst.show(); else modalEl.style.display = 'block';
    });

    clearBtn && clearBtn.addEventListener('click', () => {
        setWishlist({});
        renderWishlistDrawer();
        // reset all heart icons
        document.querySelectorAll('.fav-toggle i').forEach(ic => {
            ic.classList.remove('fas');
            ic.classList.add('far');
            ic.style.color = '#fff';
        });
        showNotification('Đã xóa danh sách yêu thích', 'info');
    });

    updateFavBadgeCount();
}

document.addEventListener('DOMContentLoaded', () => {
    try { initWishlistUI(); } catch(e) {}
});

// Update Cart Count - Use actual cart items count
function updateCartCount() {
    const cartBadges = document.querySelectorAll('.cart-badge');
    if (cartBadges.length === 0) return;

    // Get cart from localStorage
    const cart = JSON.parse(localStorage.getItem('cart') || '[]');
    
    // Calculate total quantity
    const totalQuantity = cart.reduce((sum, item) => sum + item.quantity, 0);
    
    // Store total count
    localStorage.setItem('cartCount', totalQuantity.toString());

    // Update all cart badges
    cartBadges.forEach(cartBadge => {
        cartBadge.textContent = totalQuantity;

        // Add animation
        cartBadge.style.transform = 'scale(1.2)';
        setTimeout(() => {
            cartBadge.style.transform = 'scale(1)';
        }, 200);
    });
}

// Ensure cart badges show correct count on initial load
function initCartBadgeZero() {
    const cartBadges = document.querySelectorAll('.cart-badge');
    if (cartBadges.length === 0) return;
    
    // Get cart count from localStorage or default to 0
    const cartCount = parseInt(localStorage.getItem('cartCount') || '0', 10);
    
    cartBadges.forEach(badge => {
        badge.textContent = cartCount.toString();
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
    notification.className = `alert alert-${type === 'error' ? 'danger' : type === 'success' ? 'success' : 'info'} alert-dismissible fade show notification-fixed`;
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto remove after 2 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 1500);
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
// Smooth scrolling for anchor links
function initSmoothScrolling() {
    const anchorLinks = document.querySelectorAll('a[href^="#"]');

    anchorLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            // Lấy href của thẻ <a>
            const targetId = this.getAttribute('href');

            // --- Cải thiện xử lý lỗi ---
            // 1. Kiểm tra nếu href chỉ là "#"
            // 2. Kiểm tra nếu href là chuỗi rỗng
            if (targetId === '#' || targetId === '') {
                // Nếu chỉ có "#", ngăn chặn hành vi mặc định và trở về đầu trang
                e.preventDefault();
                window.scrollTo({
                    top: 0,
                    behavior: 'smooth'
                });
                return; // Ngừng thực thi
            }

            // Ngăn chặn hành vi mặc định
            e.preventDefault();

            // Lấy element từ ID
            const targetElement = document.querySelector(targetId);

            // Kiểm tra xem element có tồn tại không
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            } else {
                console.error('Không tìm thấy phần tử với selector:', targetId);
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
        if (subtotalEl) subtotalEl.textContent = formatPrice(subtotal);
        if (totalEl) totalEl.textContent = formatPrice(subtotal + shipping );

        // Update global cart badge with total quantity
        const totalQty = Array.from(document.querySelectorAll('.cart-qty-input'))
            .reduce((sum, input) => sum + (parseInt(input.value, 10) || 0), 0);
        document.querySelectorAll('.cart-badge').forEach(badge => {
            badge.textContent = totalQty;
        });

        // Toggle empty cart UI
        toggleCartEmptyUI(totalQty === 0);
    }

    // Function to remove product from localStorage and update UI
    function removeProductFromCart(productId) {
        let cart = JSON.parse(localStorage.getItem('cart') || '[]');
        cart = cart.filter(item => item.id !== productId);
        localStorage.setItem('cart', JSON.stringify(cart));
        
        // Update cart count
        const totalQuantity = cart.reduce((sum, item) => sum + item.quantity, 0);
        localStorage.setItem('cartCount', totalQuantity.toString());
        
        // Update cart display
        updateCartDisplay();
        updateCartCount();
        
        // Toggle empty cart UI if cart is now empty
        toggleCartEmptyUI(totalQuantity === 0);
        
        // Update checkout button state
        updateCheckoutButtonState();
    }

    // Function to check stock and update quantity
    async function checkStockAndUpdateQuantity(productId, newQuantity, input, lineTotalEl, unitPrice) {
        try {
            const response = await fetch(`/api/product-stock/${productId}`);
            let stockQuantity = 999; // Default fallback
            
            if (response.ok) {
                const productData = await response.json();
                stockQuantity = productData.stock_quantity || 0;
            }
            
            // Check if new quantity exceeds stock
            if (newQuantity > stockQuantity) {
                showNotification(`Chỉ còn ${stockQuantity} sản phẩm trong kho!`, 'warning');
                newQuantity = stockQuantity;
            }
            
            // Update UI
            input.value = newQuantity;
            const newLineTotal = unitPrice * newQuantity;
            lineTotalEl.textContent = formatPrice(newLineTotal);
            
            // Update quantity in localStorage
            await updateProductQuantity(productId, newQuantity);
            
        } catch (error) {
            console.error('Error checking stock:', error);
            showNotification('Lỗi khi kiểm tra số lượng tồn kho!', 'error');
        }
    }

    // Function to update product quantity in localStorage
    async function updateProductQuantity(productId, newQuantity) {
        try {
        let cart = JSON.parse(localStorage.getItem('cart') || '[]');
        const productIndex = cart.findIndex(item => item.id === productId);
        
        if (productIndex !== -1) {
            if (newQuantity <= 0) {
                // Do not remove here while user is typing; defer to change/confirm handler
                return;
                }
                
                // Check stock availability before updating
                const response = await fetch(`/api/product-stock/${productId}`);
                let stockQuantity = 999; // Default fallback
                
                if (response.ok) {
                    const productData = await response.json();
                    stockQuantity = productData.stock_quantity || 0;
                }
                
                // Check if new quantity exceeds stock
                if (newQuantity > stockQuantity) {
                    showNotification(`Chỉ còn ${stockQuantity} sản phẩm trong kho!`, 'warning');
                    // Reset to stock quantity
                    newQuantity = stockQuantity;
                }
                
                // Update quantity
                cart[productIndex].quantity = newQuantity;
            
            localStorage.setItem('cart', JSON.stringify(cart));
            
            // Update cart count
            const totalQuantity = cart.reduce((sum, item) => sum + item.quantity, 0);
            localStorage.setItem('cartCount', totalQuantity.toString());
            
            // Update cart display
            updateCartDisplay();
            updateCartCount();
            
            // Toggle empty cart UI if cart is now empty
            toggleCartEmptyUI(totalQuantity === 0);
                
                // Update checkout button state
                updateCheckoutButtonState();
            }
        } catch (error) {
            console.error('Error updating product quantity:', error);
            showNotification('Lỗi khi cập nhật số lượng sản phẩm!', 'error');
        }
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
            const productId = removeBtn.getAttribute('data-product-id');
            const name = row.querySelector('td:nth-child(2) .fw-semibold')?.textContent?.trim() || 'sản phẩm này';
            showCartConfirm(`Bạn có muốn xóa ${name} khỏi giỏ hàng không?`, () => {
                removeProductFromCart(productId);
            });
            return;
        }

        let qty = parseInt(input.value, 10) || 1;
        const productId = input.getAttribute('data-product-id');
        
        if (increaseBtn) {
            // Check stock before increasing
            checkStockAndUpdateQuantity(productId, qty + 1, input, lineTotalEl, unitPrice);
            return;
        } else if (decreaseBtn) {
            if (qty - 1 <= 0) {
                const name = row.querySelector('td:nth-child(2) .fw-semibold')?.textContent?.trim() || 'sản phẩm này';
                showCartConfirm(`Số lượng về 0. Bạn có muốn xóa ${name} khỏi giỏ hàng không?`, () => {
                    removeProductFromCart(productId);
                });
                return;
            } else {
                qty = qty - 1;
            }
        }

        input.value = qty;
        const newLineTotal = unitPrice * qty;
            lineTotalEl.textContent = formatPrice(newLineTotal);

        // Update quantity in localStorage
        updateProductQuantity(productId, qty);
    });

    // Handle typing quantity directly
    cartTable.addEventListener('input', function(e) {
        const input = e.target.closest('.cart-qty-input');
        if (!input) return;
        const row = input.closest('tr');
        const priceEl = row.querySelector('.cart-price');
        const lineTotalEl = row.querySelector('.cart-line-total');
        const unitPrice = parseNumber(priceEl?.dataset?.price);

        // Keep only digits but allow temporary empty while typing
        const digits = input.value.replace(/[^0-9]/g, '');
        input.value = digits;
        const qty = digits === '' ? null : Math.max(0, parseInt(digits, 10));

        const newLineTotal = (qty === null ? 0 : unitPrice * qty);
            lineTotalEl.textContent = formatPrice(newLineTotal);
        
        // Do not persist while empty; wait for change/blur
        if (qty !== null) {
            const productId = input.getAttribute('data-product-id');
            // Check stock before updating
            checkStockAndUpdateQuantity(productId, qty, input, lineTotalEl, unitPrice);
        }
    });

    // Enforce minimums and confirm removal on blur/change
    cartTable.addEventListener('change', function(e) {
        const input = e.target.closest('.cart-qty-input');
        if (!input) return;
        const row = input.closest('tr');
        let digits = input.value.replace(/[^0-9]/g, '');
        if (digits === '') digits = '0';
        let qty = Math.max(0, parseInt(digits || '0', 10));

        if (qty <= 0) {
            const productId = input.getAttribute('data-product-id');
            const name = row.querySelector('td:nth-child(2) .fw-semibold')?.textContent?.trim() || 'sản phẩm này';
            showCartConfirm(`Số lượng về 0. Bạn có muốn xóa ${name} khỏi giỏ hàng không?`, () => {
                removeProductFromCart(productId);
            });
            // keep input showing 0 until user confirms; totals already updated
            return;
        }

        if (qty > 9999) qty = 9999;
        input.value = String(qty);
        
        const productId = input.getAttribute('data-product-id');
        updateProductQuantity(productId, qty);
        
        const priceEl = row.querySelector('.cart-price');
        const lineTotalEl = row.querySelector('.cart-line-total');
        const unitPrice = parseNumber(priceEl?.dataset?.price);
        const newLineTotal = unitPrice * qty;
            lineTotalEl.textContent = formatPrice(newLineTotal);
    });

    // Initial sync on load
    updateTotals();
}

// Add product to cart
async function addProductToCart(productId, productName, productPrice, productImg, originalPrice = null, quantity = 1) {
    try {
    // Get current cart from localStorage
    let cart = JSON.parse(localStorage.getItem('cart') || '[]');
    
    // Normalize quantity
    const qty = Math.max(1, parseInt(quantity, 10) || 1);
        
        // Fetch product stock information from API
        const response = await fetch(`/api/product-stock/${productId}`);
        let stockQuantity = 999; // Default fallback
        
        if (response.ok) {
            const productData = await response.json();
            stockQuantity = productData.stock_quantity || 0;
        }
    
    // Check if product already exists in cart
    const existingProductIndex = cart.findIndex(item => item.id === productId);
    
        let newTotalQuantity = qty;
        if (existingProductIndex !== -1) {
            // Product exists, calculate new total quantity
            newTotalQuantity = cart[existingProductIndex].quantity + qty;
        }
        
        // Check stock availability
        if (newTotalQuantity > stockQuantity) {
            const availableQuantity = stockQuantity - (existingProductIndex !== -1 ? cart[existingProductIndex].quantity : 0);
            
            if (availableQuantity <= 0) {
                showNotification(`Sản phẩm "${productName}" đã hết hàng!`, 'error');
                return false;
            } else {
                showNotification(`Chỉ còn ${availableQuantity} sản phẩm "${productName}" trong kho!`, 'warning');
                return false;
            }
        }
        
        // Add/update product in cart
    if (existingProductIndex !== -1) {
        // Product exists, increment quantity
        cart[existingProductIndex].quantity += qty;
    } else {
        // Product doesn't exist, add new item
        cart.push({
            id: productId,
            name: productName,
            price: productPrice,
            image: productImg,
            originalPrice: originalPrice, // Lưu giá gốc để tính tiết kiệm
            quantity: qty
        });
    }
    
    // Save updated cart to localStorage
    localStorage.setItem('cart', JSON.stringify(cart));
    
    // Update all cart-related displays automatically
    updateAllCartDisplays();
    
        // Update checkout button state
        updateCheckoutButtonState();
        
        showNotification(`Đã thêm ${qty} x "${productName}" vào giỏ hàng!`, 'success');
    console.log(`Đã thêm ${qty} x "${productName}" vào giỏ. Tổng mặt hàng: ${cart.length}`);
        return true;
        
    } catch (error) {
        console.error('Error adding product to cart:', error);
        showNotification('Lỗi khi thêm sản phẩm vào giỏ hàng!', 'error');
        return false;
    }
}

// Update cart display
function updateCartDisplay() {
    const cartContainer = document.querySelector('#cart-items-container');
    if (!cartContainer) {
        console.log('Cart container not found - user is not on cart page');
        return;
    }
    
    const cart = JSON.parse(localStorage.getItem('cart') || '[]');
    
    if (cart.length === 0) {
        cartContainer.innerHTML = `
            <div class="card border-0 shadow-sm">
                <div class="card-body text-center py-5">
                    <img src="/static/image/gif/khoc.gif" alt="empty" class="mx-auto mb-3" style="width: 120px; height: 120px; object-fit: cover;">
                    <h5 class="fw-bold mb-2">Giỏ hàng trống</h5>
                    <p class="text-muted mb-4">Bạn chưa thêm sản phẩm nào. Khám phá sản phẩm và thêm vào giỏ nhé!</p>
                    <a href="/products" class="btn btn-primary"><i class="fas fa-shopping-bag me-2"></i>Mua sắm ngay</a>
                </div>
            </div>
        `;
        return;
    }
    
    let cartHTML = `
        <div class="card border-0 shadow-sm">
            <div class="card-body p-0">
                <div class="table-responsive">
                    <table class="table align-middle mb-0">
                        <thead class="table-light">
                            <tr>
                                <th style="width: 70px;"></th>
                                <th>Sản phẩm</th>
                                <th class="text-center" style="width: 120px;">Số lượng</th>
                                <th class="text-end" style="width: 150px;">Đơn giá</th>
                                <th class="text-end" style="width: 150px;">Thành tiền</th>
                                <th class="text-end" style="width: 60px;"></th>
                            </tr>
                        </thead>
                        <tbody>
    `;
    
    cart.forEach(item => {
        const price = parsePrice(item.price);
        const itemTotal = price * item.quantity;
        
        cartHTML += `
            <tr>
                <td>
                    <img src="${item.image}" alt="${item.name}" class="img-fluid rounded" style="width:60px;height:60px;object-fit:cover;">
                </td>
                <td>
                    <div class="fw-semibold"><a href="/product/${item.id}" class="text-decoration-none">${item.name}</a></div>
                    <div class="text-muted small">ID: ${item.id}</div>
                </td>
                <td class="text-center">
                    <div class="d-inline-flex align-items-center justify-content-center gap-2 cart-qty" style="max-width:160px;">
                        <button class="btn btn-outline-secondary btn-sm cart-qty-decrease" type="button" aria-label="Giảm">-</button>
                        <input type="text" class="form-control form-control-sm text-center cart-qty-input" value="${item.quantity}" style="width:64px;" data-product-id="${item.id}">
                        <button class="btn btn-outline-secondary btn-sm cart-qty-increase" type="button" aria-label="Tăng">+</button>
                    </div>
                </td>
                <td class="text-end cart-price" data-price="${price}">${formatPrice(price)}</td>
                <td class="text-end fw-semibold cart-line-total">${formatPrice(itemTotal)}</td>
                <td class="text-end">
                    <button class="btn btn-sm btn-outline-danger cart-remove-btn" aria-label="Xóa sản phẩm" data-product-id="${item.id}">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            </tr>
        `;
    });
    
    cartHTML += `
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        <div class="mt-3 d-flex gap-2">
            <a href="/products" class="btn btn-outline-secondary" style="padding: 10px 20px;">
                <i class="fas fa-arrow-left me-2"></i>Tiếp tục mua sắm
            </a>
            <a href="/checkout" class="btn btn-primary">
                <i class="fas fa-credit-card me-2"></i>Thanh toán
            </a>
        </div>
    `;
    
    cartContainer.innerHTML = cartHTML;
    
    // Update cart summary
    updateCartSummary();
    
    // Re-initialize cart controls
    initCartQuantityControls();
    
    console.log('Cart display updated successfully');
}

// Update checkout display
function updateCheckoutDisplay() {
    const cart = JSON.parse(localStorage.getItem('cart') || '[]');
    const container = document.querySelector('#checkout-items-container');
    
    if (!container) {
        console.log('Checkout container not found - user is not on checkout page');
        return;
    }
    
    if (cart.length === 0) {
        container.innerHTML = `
            <div class="text-center py-3">
                <i class="fas fa-shopping-cart text-muted" style="font-size: 2rem;"></i>
                <p class="text-muted mt-2">Giỏ hàng trống</p>
                <a href="/products" class="btn btn-sm btn-primary">Mua sắm ngay</a>
            </div>
        `;
        return;
    }
    
    let itemsHTML = '';
    cart.forEach(item => {
        const price = parsePrice(item.price);
        const itemTotal = price * item.quantity;
        
        itemsHTML += `
            <div class="d-flex align-items-center mb-3">
                <img src="${item.image}" alt="${item.name}" class="rounded me-3" style="width:56px;height:56px;object-fit:cover;">
                <div class="flex-grow-1">
                    <div class="small fw-semibold"><a href="/product/${item.id}" class="text-decoration-none">${item.name}</a></div>
                    <div class="text-muted small">x${item.quantity}</div>
                </div>
                <div class="fw-semibold">${itemTotal.toLocaleString('vi-VN')}đ</div>
            </div>
        `;
    });
    
    container.innerHTML = itemsHTML;
    
    // Update checkout summary
    updateCheckoutSummary();
    
    console.log('Checkout display updated successfully');
}

// Update checkout summary
function updateCheckoutSummary() {
    const cart = JSON.parse(localStorage.getItem('cart') || '[]');
    const subtotalEl = document.querySelector('.checkout-subtotal');
    const shippingEl = document.querySelector('.checkout-shipping');
    const totalEl = document.querySelector('.checkout-total');
    const savingsEl = document.querySelector('.checkout-savings');
    
    console.log('=== UPDATE CHECKOUT SUMMARY ===');
    console.log('Cart items:', cart.length);
    console.log('Subtotal element found:', !!subtotalEl);
    console.log('Shipping element found:', !!shippingEl);
    console.log('Total element found:', !!totalEl);
    console.log('Savings element found:', !!savingsEl);
    
    if (!subtotalEl || !shippingEl || !totalEl) {
        console.error('Required elements not found on checkout page');
        console.error('Subtotal element:', subtotalEl);
        console.error('Shipping element:', shippingEl);
        console.error('Total element:', totalEl);
        return; // Not on checkout page
    }
    
    // Additional check: verify elements are actually in the DOM
    if (!document.contains(subtotalEl) || !document.contains(shippingEl) || !document.contains(totalEl)) {
        console.error('Elements found but not in DOM');
        return;
    }
    
    if (cart.length === 0) {
        subtotalEl.textContent = '0đ';
        shippingEl.textContent = '0đ';
        totalEl.textContent = '0đ';
        if (savingsEl) savingsEl.textContent = '0đ';
        return;
    }
    
    let subtotal = 0;
    let totalOriginalPrice = 0;
    let totalDiscountedPrice = 0;
    
    cart.forEach(item => {
        // Parse price more accurately using helper function
        const price = parsePrice(item.price);
        subtotal += price * item.quantity;
        
        // Debug: Log thông tin để kiểm tra
        console.log('=== DEBUG ITEM ===');
        console.log('Item name:', item.name);
        console.log('Item price (discounted):', item.price, '-> parsed:', price);
        console.log('Item originalPrice:', item.originalPrice);
        console.log('Item quantity:', item.quantity);
        
        // Tính toán phần tiết kiệm dựa trên giá gốc thực tế
        if (item.originalPrice) {
            const originalPrice = parsePrice(item.originalPrice);
            totalOriginalPrice += originalPrice * item.quantity;
            console.log('Using ACTUAL original price:', originalPrice, '-> total:', totalOriginalPrice);
        } else {
            // Fallback: ước tính giá gốc nếu không có thông tin
            // Giả sử giảm trung bình 40% (thực tế hơn cho sản phẩm thanh lý)
            const estimatedOriginalPrice = Math.round(price / 0.6); // Giả sử giảm 40%
            totalOriginalPrice += estimatedOriginalPrice * item.quantity;
            console.log('Using ESTIMATED original price:', estimatedOriginalPrice, '-> total:', totalOriginalPrice);
        }
        totalDiscountedPrice += price * item.quantity;
        console.log('Total discounted price so far:', totalDiscountedPrice);
        console.log('=== END DEBUG ===');
    });
    
    // Tính phần tiết kiệm (đảm bảo không âm)
    const productSavings = Math.max(0, totalOriginalPrice - totalDiscountedPrice);
    
    console.log('=== FINAL CALCULATION ===');
    console.log('Total Original Price:', totalOriginalPrice);
    console.log('Total Discounted Price:', totalDiscountedPrice);
    console.log('Total Savings:', productSavings);
    console.log('=== END FINAL ===');
    
    // Get selected shipping method
    const selectedShip = document.querySelector('input[name="ship"]:checked');
    let shipping = 30000; // Default standard shipping
    
    if (selectedShip && selectedShip.id === 'ship2') {
        shipping = 40000; // Express shipping for TP.HCM (4h-8h)
    }
    
    // Apply 50% discount if bank transfer is selected
    const selectedPayment = document.querySelector('input[name="pay"]:checked');
    if (selectedPayment && selectedPayment.value === 'bankTransfer') {
        shipping = Math.round(shipping * 0.5); // Giảm 50% khi chuyển khoản
    }
    
    // Apply voucher discount
    const appliedVoucher = getAppliedVoucher();
    let voucherDiscount = 0;
    if (appliedVoucher) {
        voucherDiscount = appliedVoucher.discount;
        // Update voucher line display
        const voucherLineEl = document.getElementById('checkoutVoucherLine');
        const voucherDiscountEl = document.querySelector('.checkout-voucher-discount');
        if (voucherLineEl && voucherDiscountEl) {
            voucherLineEl.style.display = 'flex';
            voucherDiscountEl.textContent = `-${voucherDiscount.toLocaleString('vi-VN')}đ`;
        }
    } else {
        // Hide voucher line if no voucher and reset to 0đ
        const voucherLineEl = document.getElementById('checkoutVoucherLine');
        const voucherDiscountEl = document.querySelector('.checkout-voucher-discount');
        if (voucherLineEl) {
            voucherLineEl.style.display = 'none';
        }
        if (voucherDiscountEl) {
            voucherDiscountEl.textContent = '-0đ';
        }
    }
    
    // Tính phí vận chuyển gốc (không giảm giá)
    const originalShipping = selectedShip && selectedShip.id === 'ship2' ? 40000 : 30000;
    
    // Tính tổng tiền tiết kiệm
    const totalSavings = productSavings + voucherDiscount + (originalShipping - shipping);
    
    const total = subtotal + shipping - voucherDiscount;
    
    console.log('=== FINAL CHECKOUT CALCULATION ===');
    console.log('Subtotal:', subtotal);
    console.log('Shipping:', shipping);
    console.log('Voucher Discount:', voucherDiscount);
    console.log('Product Savings (price difference):', productSavings);
    console.log('Shipping Savings (50% off):', originalShipping - shipping);
    console.log('Total Savings:', totalSavings);
    console.log('Total:', total);
    console.log('=== END CHECKOUT CALCULATION ===');
    
    subtotalEl.textContent = formatPrice(subtotal);
    shippingEl.textContent = formatPrice(shipping );
    totalEl.textContent = formatPrice(total);
    
    // Update hidden shipping fee input (send original value to API)
    const shippingInput = document.getElementById('checkout-shipping');
    if (shippingInput) {
        shippingInput.value = shipping / 1000;
        console.log('Updated shipping input value to:', shipping / 1000);
    }
    
    // Debug: Log what we're setting
    console.log('Setting subtotal to:', subtotal.toLocaleString('vi-VN') + 'đ');
    console.log('Setting shipping to:', shipping.toLocaleString('vi-VN') + 'đ');
    console.log('Setting total to:', total.toLocaleString('vi-VN') + 'đ');
    
    // Also try to update the transfer amount if it exists
    const transferAmountEl = document.querySelector('.transfer-amount');
    if (transferAmountEl) {
        transferAmountEl.textContent = formatPrice(total);
        console.log('Setting transfer amount to:', total.toLocaleString('vi-VN') + 'đ');
    }
    
    // Hiển thị phần tiết kiệm
    if (savingsEl && totalSavings > 0) {
        savingsEl.textContent = formatPrice(totalSavings );
    } else if (savingsEl) {
        savingsEl.textContent = '0đ';
    }
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
            a.style.pointerEvents = 'none';
            a.style.opacity = '0.6';
        } else {
            a.classList.remove('disabled');
            a.removeAttribute('aria-disabled');
            a.removeAttribute('tabindex');
            a.style.pointerEvents = 'auto';
            a.style.opacity = '1';
        }
    });

    summaryCards.forEach(card => {
        if (isEmpty) {
            // Cập nhật tất cả giá trị về 0đ khi giỏ hàng trống
            const subtotalEl = card.querySelector('.cart-subtotal');
            const savingsEl = card.querySelector('.cart-savings');
            const shippingEl = card.querySelector('.cart-shipping');
            const totalEl = card.querySelector('.cart-total');
            
            if (subtotalEl) subtotalEl.textContent = '0đ';
            if (savingsEl) savingsEl.textContent = '0đ';
            if (shippingEl) shippingEl.textContent = '0đ';
            if (totalEl) totalEl.textContent = '0đ';
        }
        // Không cần ẩn/hiện card, chỉ cập nhật giá trị
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

// Tính lại chiều rộng item/container dựa vào viewport (responsive)
function layoutSlider(containerSelector) {
    const container = document.querySelector(containerSelector);
    if (!container) return;
    const productsContainer = container.querySelector('.homepage-products');
    const wrapper = productsContainer?.parentElement;
    if (!productsContainer || !wrapper) return;

    const totalProducts = parseInt(productsContainer.dataset.totalProducts || '0', 10);
    const gap = 16; // Fixed gap 16px
    
    // Responsive products per view
    let productsPerView, paddingX;
    if (window.innerWidth <= 576) {
        // Mobile: 2 products
        productsPerView = 2;
        paddingX = 32; // 16px left + 16px right padding
    } else if (window.innerWidth <= 768) {
        // Tablet: 3 products  
        productsPerView = 3;
        paddingX = 40; // 20px left + 20px right padding
    } else {
        // Desktop: 5 products
        productsPerView = 5;
        paddingX = 80; // 40px left + 40px right padding
    }
    
    // Cập nhật dataset để navigateProducts biết số lượng hiện tại
    productsContainer.dataset.productsPerView = String(productsPerView);
    
    // Tính toán chính xác để đảm bảo productsPerView sản phẩm hiển thị đầy đủ
    const availableWidth = wrapper.clientWidth - paddingX;
    const totalGapWidth = gap * (productsPerView - 1);
    const itemWidth = Math.floor((availableWidth - totalGapWidth) / productsPerView);

    // Set width cho tất cả items
    const items = productsContainer.querySelectorAll('.slider-item');
    items.forEach(el => {
        el.style.width = `${itemWidth}px`;
        el.style.flex = '0 0 auto';
    });
    
    // Set tổng chiều rộng container
    const totalContainerWidth = itemWidth * totalProducts + gap * Math.max(0, totalProducts - 1);
    productsContainer.style.width = `${totalContainerWidth}px`;

    // Reposition current index by item step
    const currentIndex = parseInt(productsContainer.dataset.currentIndex || '0', 10);
    const step = itemWidth + gap;
    const translatePx = -currentIndex * step;
    productsContainer.style.transform = `translateX(${translatePx}px)`;
    updateNavigationButtons(containerSelector, currentIndex);
}

// Update cart summary
function updateCartSummary() {
    const cart = JSON.parse(localStorage.getItem('cart') || '[]');
    const subtotalEl = document.querySelector('.cart-subtotal');
    const shippingEl = document.querySelector('.cart-shipping');
    const totalEl = document.querySelector('.cart-total');
    const savingsEl = document.querySelector('.cart-savings');
    const checkoutBtn = document.getElementById('checkoutBtn');
    
    if (cart.length === 0) {
        if (subtotalEl) subtotalEl.textContent = '0đ';
        if (shippingEl) shippingEl.textContent = '0đ';
        if (totalEl) totalEl.textContent = '0đ';
        if (savingsEl) savingsEl.textContent = '0đ';
        
        // Disable checkout button when cart is empty
        if (checkoutBtn) {
            checkoutBtn.classList.add('disabled');
            checkoutBtn.setAttribute('aria-disabled', 'true');
            checkoutBtn.setAttribute('tabindex', '-1');
            checkoutBtn.style.pointerEvents = 'none';
            checkoutBtn.style.opacity = '0.6';
        }
        return;
    }
    
    // Enable checkout button when cart has items
    if (checkoutBtn) {
        checkoutBtn.classList.remove('disabled');
        checkoutBtn.removeAttribute('aria-disabled');
        checkoutBtn.removeAttribute('tabindex');
        checkoutBtn.style.pointerEvents = 'auto';
        checkoutBtn.style.opacity = '1';
    }
    
    let subtotal = 0;
    let totalOriginalPrice = 0;
    let totalDiscountedPrice = 0;
    
    cart.forEach(item => {
        // Parse price more accurately using helper function
        const price = parsePrice(item.price);
        subtotal += price * item.quantity;
        
        // Tính toán phần tiết kiệm dựa trên giá gốc thực tế
        if (item.originalPrice) {
            const originalPrice = parsePrice(item.originalPrice);
            totalOriginalPrice += originalPrice * item.quantity;
        } else {
            // Fallback: ước tính giá gốc nếu không có thông tin
            // Giả sử giảm trung bình 40% (thực tế hơn cho sản phẩm thanh lý)
            const estimatedOriginalPrice = Math.round(price / 0.6); // Giả sử giảm 40%
            totalOriginalPrice += estimatedOriginalPrice * item.quantity;
        }
        totalDiscountedPrice += price * item.quantity;
    });
    
    // Tính phần tiết kiệm từ giá sản phẩm (đảm bảo không âm)
    const productSavings = Math.max(0, totalOriginalPrice - totalDiscountedPrice);
    
    // Tính phí vận chuyển dựa trên phương thức thanh toán
    let shipping = 30000; // Default shipping cost
    const selectedPayment = document.querySelector('input[name="paymentMethod"]:checked');
    if (selectedPayment && selectedPayment.value === 'bankTransfer') {
        shipping = Math.round(shipping * 0.5); // Giảm 50% khi chuyển khoản
    }
    
    // Apply voucher discount
    const appliedVoucher = getAppliedVoucher();
    let voucherDiscount = 0;
    if (appliedVoucher) {
        voucherDiscount = appliedVoucher.discount;
        // Update voucher line display
        const voucherLineEl = document.getElementById('cartVoucherLine');
        const voucherDiscountEl = document.querySelector('.cart-voucher-discount');
        if (voucherLineEl && voucherDiscountEl) {
            voucherLineEl.style.display = 'flex';
            voucherDiscountEl.textContent = `-${voucherDiscount.toLocaleString('vi-VN')}đ`;
        }
    } else {
        // Hide voucher line if no voucher and reset to 0đ
        const voucherLineEl = document.getElementById('cartVoucherLine');
        const voucherDiscountEl = document.querySelector('.cart-voucher-discount');
        if (voucherLineEl) {
            voucherLineEl.style.display = 'none';
        }
        if (voucherDiscountEl) {
            voucherDiscountEl.textContent = '-0đ';
        }
    }
    
    // Tính phí vận chuyển gốc (không giảm giá)
    const originalShipping = 30000;
    
    // Tính tổng tiền tiết kiệm
    const totalSavings = productSavings + voucherDiscount + (originalShipping - shipping);
    
    const total = subtotal + shipping - voucherDiscount;
    
    if (subtotalEl) subtotalEl.textContent = formatPrice(subtotal);
    if (shippingEl) shippingEl.textContent = formatPrice(shipping );
    if (totalEl) totalEl.textContent = formatPrice(total);
    
    // Hiển thị tổng tiền tiết kiệm
    if (savingsEl && totalSavings > 0) {
        savingsEl.textContent = formatPrice(totalSavings );
    } else if (savingsEl) {
        savingsEl.textContent = '0đ';
    }
    
    // Debug logging
    console.log('=== CART SUMMARY CALCULATION ===');
    console.log('Product savings (price difference):', productSavings);
    console.log('Voucher discount:', voucherDiscount);
    console.log('Shipping savings (50% off):', originalShipping - shipping);
    console.log('Total savings:', totalSavings);
    console.log('=== END CART SUMMARY ===');
}

// Update checkout button state based on cart content
function updateCheckoutButtonState() {
    const cart = JSON.parse(localStorage.getItem('cart') || '[]');
    const checkoutBtn = document.getElementById('checkoutBtn');
    
    if (!checkoutBtn) return;
    
    if (cart.length === 0) {
        // Disable checkout button when cart is empty
        checkoutBtn.classList.add('disabled');
        checkoutBtn.setAttribute('aria-disabled', 'true');
        checkoutBtn.setAttribute('tabindex', '-1');
        checkoutBtn.style.pointerEvents = 'none';
        checkoutBtn.style.opacity = '0.6';
        console.log('Checkout button disabled - cart is empty');
    } else {
        // Enable checkout button when cart has items
        checkoutBtn.classList.remove('disabled');
        checkoutBtn.removeAttribute('aria-disabled');
        checkoutBtn.removeAttribute('tabindex');
        checkoutBtn.style.pointerEvents = 'auto';
        checkoutBtn.style.opacity = '1';
        console.log('Checkout button enabled - cart has items');
    }
}

// Save payment method to localStorage
function savePaymentMethod(method) {
    console.log('Saving payment method to localStorage:', method);
    localStorage.setItem('selectedPaymentMethod', method);
}

// Get payment method from localStorage
function getPaymentMethod() {
    const method = localStorage.getItem('selectedPaymentMethod') || 'cod';
    console.log('Getting payment method from localStorage:', method);
    return method;
}

// Handle cart payment method change
function handleCartPaymentChange() {
    console.log('=== CART PAYMENT METHOD CHANGED ===');
    
    const selectedPayment = document.querySelector('input[name="paymentMethod"]:checked');
    const bankTransferInfo = document.getElementById('bankTransferInfo');
    
    console.log('Selected payment method:', selectedPayment?.value);
    console.log('Bank transfer info element found:', !!bankTransferInfo);
    
    if (selectedPayment && selectedPayment.value === 'bankTransfer') {
        console.log('Showing bank transfer info');
        bankTransferInfo.classList.remove('d-none');
    } else {
        console.log('Hiding bank transfer info');
        bankTransferInfo.classList.add('d-none');
    }
    
    // Save selected payment method
    if (selectedPayment) {
        savePaymentMethod(selectedPayment.value);
        console.log('Payment method saved to localStorage:', selectedPayment.value);
    } else {
        console.log('No payment method selected, cannot save');
    }
    
    // Update cart summary when payment method changes
    updateCartSummary();
    
    console.log('=== CART PAYMENT METHOD CHANGE COMPLETED ===');
}

// Manual trigger for testing payment method sync
window.manualSyncPayment = function() {
    console.log('=== MANUAL PAYMENT SYNC TRIGGERED ===');
    syncPaymentMethod();
};

// Manual trigger for testing voucher sync
window.manualSyncVoucher = function() {
    console.log('=== MANUAL VOUCHER SYNC TRIGGERED ===');
    syncVoucherToCart();
    syncVoucherToCheckout();
};

// Manual trigger for testing payment method selection
window.manualSelectPayment = function(method = 'bankTransfer') {
    console.log('=== MANUAL PAYMENT SELECTION TRIGGERED ===');
    console.log('Selecting payment method:', method);
    
    const radio = document.querySelector(`input[name="pay"][value="${method}"]`);
    if (radio) {
        console.log('Found radio button:', radio.outerHTML);
        
        // Uncheck all first
        document.querySelectorAll('input[name="pay"]').forEach(r => r.checked = false);
        
        // Check the selected one
        radio.checked = true;
        console.log('Radio button checked:', radio.checked);
        
        // Trigger change event
        radio.dispatchEvent(new Event('change', { bubbles: true }));
        
        console.log('Payment method manually selected:', method);
    } else {
        console.log('Radio button not found for:', method);
    }
};

console.log('Manual functions available:');
console.log('- manualSyncPayment() - Force sync payment method');
console.log('- manualSyncVoucher() - Force sync voucher');
console.log('- manualSelectPayment("bankTransfer") - Manually select bank transfer');

// Hàm khởi tạo cho sản phẩm gợi ý trong checkout
function initCheckoutSuggestedProducts() {
    const suggestedProductsApiUrl = 'https://buddyskincare.pythonanywhere.com/products/?tags=FlashSale&limit=10';
    const containerSelector = '#checkout-suggested-products';
    fetchAndRenderSuggestedProducts(suggestedProductsApiUrl, containerSelector);
    
    // Re-render when window is resized to handle responsive layout
    let resizeTimeout;
    window.addEventListener('resize', () => {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(() => {
            fetchAndRenderSuggestedProducts(suggestedProductsApiUrl, containerSelector);
        }, 250);
    });
}

// Hàm render sản phẩm gợi ý cho checkout (layout nhỏ gọn)
async function fetchAndRenderSuggestedProducts(apiUrl, containerSelector) {
    const container = document.querySelector(containerSelector);
    if (!container) {
        console.error(`Không tìm thấy container với selector: ${containerSelector}`);
        return;
    }

    try {
        const response = await fetch(apiUrl);
        if (!response.ok) {
            throw new Error('Lỗi khi lấy dữ liệu từ API');
        }
        const products = await response.json();
        
        if (products.length === 0) {
            container.innerHTML = '<p class="text-muted text-center py-4">Không có sản phẩm flash-sale nào để hiển thị.</p>';
            return;
        }

        // Tạo grid layout cho sản phẩm gợi ý (2 hàng, mỗi hàng 5 sản phẩm)
        let productsHTML = '';
        
        // Xác định số lượng tối đa theo thiết bị
        const isMobile = window.innerWidth <= 767;
        const maxItems = isMobile ? 6 : 10; // Mobile: 6 sản phẩm, Desktop: 10 sản phẩm
        const count = Math.min(products.length, maxItems);
        
        // Tạo layout responsive: Mobile 2 cột, Desktop 5 cột
        const itemsPerRow = isMobile ? 2 : 5;
        const rows = Math.ceil(count / itemsPerRow);
        
        for (let row = 0; row < rows; row++) {
            productsHTML += '<div class="row g-2" style="margin-bottom: 10px !important;">';
            
            const startIndex = row * itemsPerRow;
            const endIndex = Math.min(startIndex + itemsPerRow, count);
            
            for (let i = startIndex; i < endIndex; i++) {
            const product = products[i];
            
            if (product) {
                // Map sang Product model (không dùng variants/album)
                const imageUrl = (product.image && String(product.image).trim()) || '/static/image/default-product.jpg';
                const brandName = product.brand_name || (product.brand ? product.brand.name : '');
                const originalPrice = typeof product.original_price === 'number' ? product.original_price * 1000 : null;
                const discountedPrice = typeof product.discounted_price === 'number' ? product.discounted_price * 1000 : null;
                const discountRate = (typeof product.discount_rate === 'number')
                    ? Math.round(product.discount_rate)
                    : ((originalPrice && discountedPrice) ? Math.round(((originalPrice - discountedPrice) / originalPrice) * 100) : 0);
                const stockQuantity = typeof product.stock_quantity === 'number' ? product.stock_quantity : 0;

                productsHTML += `
                    <div class="col-6 col-lg" style="flex: 0 0 ${isMobile ? '50%' : '20%'}; max-width: ${isMobile ? '50%' : '20%'};">
                        <div class="card suggested-product-card h-100 border-0 shadow-sm">
                            <div class="position-relative">
                                <div class="suggested-product-image" data-product-id="${product.id}" style="cursor: pointer;">
                                    <img src="${imageUrl}" class="card-img-top" alt="${product.name}" style="height: 150px; object-fit: cover; border-radius: 4px;">
                                </div>
                                <div class="flash-sale-badge">-${discountRate}%</div>
                                <div class="position-absolute bottom-0 start-0 m-1">
                                    <img src="/static/image/logo.png" alt="Logo" class="product-logo" style="width: 28px !important; height: 28px !important; object-fit: contain; border-radius: 50%; background: white; padding: 2px; display: block; z-index: 10; box-shadow: 0 1px 3px rgba(0,0,0,0.2);" onerror="this.style.display='none';">
                                </div>
                            </div>
                            <div class="card-body p-1 position-relative">
                                <h6 class="card-title small fw-bold mb-1" style="font-size: 9px; line-height: 1.2; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;">
                                    <span class="suggested-product-name text-decoration-none text-dark" data-product-id="${product.id}" style="cursor: pointer;">${product.name}</span>
                                </h6>
                                <div class="d-flex align-items-center mb-1">
                                    ${originalPrice ? `<span class="text-decoration-line-through text-muted me-1" style="font-size: 8px;">${formatPrice(originalPrice)}</span>` : ''}
                                    <span class="text-danger fw-bold" style="font-size: 10px;">${formatPrice(discountedPrice)}</span>
                                </div>
                                <div class="d-flex align-items-center justify-content-between">
                                    <small class="text-muted" style="font-size: 8px;">Còn ${stockQuantity}</small>
                                    <button class="btn btn-sm btn-outline-primary add-to-cart-btn" data-product-id="${product.id}" style="font-size: 8px; padding: 1px 10px;">
                                        <i class="fas fa-plus"></i>
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            }
        }
        
            productsHTML += '</div>'; // Đóng row
        }
        
        container.innerHTML = productsHTML;

        // Add event handlers for suggested products
        initSuggestedProductHandlers();

        // Re-initialize Product Cards with new DOM elements
        initProductCards();

    } catch (error) {
        console.error(`Đã xảy ra lỗi khi tải dữ liệu sản phẩm gợi ý:`, error);
        container.innerHTML = '<p class="text-danger text-center py-4">Không thể tải sản phẩm gợi ý. Vui lòng thử lại sau.</p>';
    }
}

// Initialize event handlers for suggested products
function initSuggestedProductHandlers() {
    const container = document.querySelector('#checkout-suggested-products');
    if (!container) return;
    
    // Handle clicks on suggested product images and names
    container.addEventListener('click', function(e) {
        console.log('Click detected on:', e.target);
        
        // Check if clicked on product image or name
        const productImage = e.target.closest('.suggested-product-image');
        const productName = e.target.closest('.suggested-product-name');
        
        if (productImage) {
            e.preventDefault();
            e.stopPropagation();
            e.stopImmediatePropagation();
            
            const productId = productImage.getAttribute('data-product-id');
            console.log('Navigating to product:', productId);
            
            // Force navigation
            window.location.href = `/product/${productId}`;
            return false;
        }
        
        if (productName) {
            e.preventDefault();
            e.stopPropagation();
            e.stopImmediatePropagation();
            
            const productId = productName.getAttribute('data-product-id');
            console.log('Navigating to product:', productId);
            
            // Force navigation
            window.location.href = `/product/${productId}`;
            return false;
        }
        
        // Handle add to cart button clicks
        const addToCartBtn = e.target.closest('.add-to-cart-btn');
        if (addToCartBtn) {
            e.preventDefault();
            e.stopPropagation();
            e.stopImmediatePropagation();
            
            const productId = addToCartBtn.getAttribute('data-product-id');
            if (productId) {
                console.log('Adding product to cart:', productId);
                addToCart(productId, 1);
            }
            return false;
        }
    });
}

// Helper function to update all cart-related displays
function updateAllCartDisplays() {
    console.log('=== UPDATING ALL CART DISPLAYS ===');
    
    // Update cart count badge (works on all pages)
    updateCartCount();
    
    // Update cart page if user is on it
    updateCartDisplay();
    
    // Update checkout page if user is on it
    updateCheckoutDisplay();
    
    // Update summaries if they exist
    updateCartSummary();
    updateCheckoutSummary();
    
    // Update checkout button state
    updateCheckoutButtonState();
    
    console.log('=== ALL CART DISPLAYS UPDATED ===');
}

// Initialize Products page (dynamic grid like "Sản Phẩm Mới Về")
function initProductsPage() {
    const grid = document.getElementById('products-page-grid');
    if (!grid) return; // Not on products page

    const urlParams = new URLSearchParams(window.location.search);
    const query = urlParams.get('query') || urlParams.get('q') || urlParams.get('search') || '';
    let condition = urlParams.get('condition') || '';
    const categoryName = urlParams.get('category_name') || urlParams.get('category') || '';
    const brandsName = urlParams.get('brands_name') || urlParams.get('brand') || '';
    const priceRange = urlParams.get('price_range') || urlParams.get('price') || '';
    const discountRange = urlParams.get('discount_range') || urlParams.get('discount') || '';
    const tagsFilter = urlParams.get('tags') || '';
    
    // Pagination parameters
    const currentPage = parseInt(urlParams.get('page')) || 1;
    const perPage = parseInt(urlParams.get('per_page')) || 12;
    // Infer condition from pathname if not provided via query string
    if (!condition) {
        const path = window.location.pathname || '';
        if (path.includes('/products/new')) condition = 'new';
        else if (path.includes('/products/used')) condition = 'used';
    }

    let apiUrl = 'https://buddyskincare.pythonanywhere.com/products/';
    const qs = [];
    if (query) qs.push(`search=${encodeURIComponent(query)}`);
    if (condition) qs.push(`condition=${encodeURIComponent(condition)}`);
    if (qs.length) apiUrl += (apiUrl.includes('?') ? '&' : '?') + qs.join('&');

    grid.innerHTML = `
        <div class="col-12 text-center py-4">
            <div class="spinner-border text-primary" role="status"><span class="visually-hidden">Đang tải...</span></div>
            <p class="text-muted mt-2 mb-0">Đang tải sản phẩm...</p>
        </div>
    `;

    fetch(apiUrl)
        .then(r => r.ok ? r.json() : Promise.reject(new Error('API error')))
        .then(products => {
            if (!Array.isArray(products) || products.length === 0) {
                grid.innerHTML = '<div class="col-12"><p class="text-center text-muted py-4 mb-0">Không có sản phẩm để hiển thị.</p></div>';
                return;
            }

            // Client-side filter by condition (new/used) using status
            if (condition) {
                const isNewStatus = s => {
                    if (!s) return false;
                    const x = String(s).toLowerCase();
                    return x.includes('new') || x.includes('chiet');
                };
                if (condition === 'new') {
                    products = products.filter(p => isNewStatus(p.status));
                } else if (condition === 'used') {
                    products = products.filter(p => !isNewStatus(p.status));
                }
            }

            // Filter by category and brand names
            const getCategoryName = (p) => {
                if (p && typeof p === 'object') {
                    if (p.category && typeof p.category === 'object') {
                        return (p.category.name || p.category.title || '').toString().trim();
                    }
                    return (p.category_name || p.category || '').toString().trim();
                }
                return '';
            };
            if (categoryName) {
                const target = categoryName.toString().trim().toLowerCase();
                products = products.filter(p => getCategoryName(p).toLowerCase() === target);
            }
            if (brandsName) {
                const getBrandName = (p) => (p.brand_name || (p.brand && p.brand.name) || '').toString().trim();
                const btarget = brandsName.toString().trim();
                products = products.filter(p => getBrandName(p) === btarget);
            }

            // Helpers
                const priceVnd = p => (p.discounted_price || 0);
            const rate = p => parseFloat(p.discount_rate || 0) || 0;

            // Price ranges
            switch (priceRange) {
                case 'under_200k':
                    products = products.filter(p => priceVnd(p) < 200000); break;
                case '200_500':
                    products = products.filter(p => 200000 <= priceVnd(p) && priceVnd(p) < 500000); break;
                case '500_1m':
                    products = products.filter(p => 500000 <= priceVnd(p) && priceVnd(p) < 1000000); break;
                case 'over_1m':
                    products = products.filter(p => priceVnd(p) >= 1000000); break;
                // Backward compatibility
                case 'under_500k':
                    products = products.filter(p => priceVnd(p) < 500000); break;
                case '500k_1m':
                    products = products.filter(p => 500000 <= priceVnd(p) && priceVnd(p) < 1000000); break;
                case '1m_2m':
                    products = products.filter(p => 1000000 <= priceVnd(p) && priceVnd(p) < 2000000); break;
                case 'over_2m':
                    products = products.filter(p => priceVnd(p) >= 2000000); break;
            }

            // Discount ranges
            switch (discountRange) {
                case 'under_30':
                    products = products.filter(p => rate(p) < 30); break;
                case '50_70':
                    products = products.filter(p => rate(p) >= 50 && rate(p) <= 70); break;
                case 'over_70':
                    products = products.filter(p => rate(p) > 70); break;
                // Backward compatibility
                case 'over_50':
                    products = products.filter(p => rate(p) >= 50); break;
                case '30_50':
                    products = products.filter(p => rate(p) >= 30 && rate(p) < 50); break;
            }

            // Tags filter
            if (tagsFilter) {
                console.log(`🔍 JavaScript filtering by tag: ${tagsFilter}`);
                const hasTag = (product, targetTag) => {
                    try {
                        const tags = product?.tags || [];
                        if (!Array.isArray(tags)) return false;
                        return tags.some(t => {
                            if (typeof t === 'string') return t.toLowerCase() === targetTag.toLowerCase();
                            if (t && typeof t === 'object') return (t.name || '').toLowerCase() === targetTag.toLowerCase();
                            return false;
                        });
                    } catch (error) {
                        return false;
                    }
                };
                const beforeCount = products.length;
                products = products.filter(p => hasTag(p, tagsFilter));
                const afterCount = products.length;
                console.log(`📊 JavaScript tags filter: ${beforeCount} -> ${afterCount} products`);
            }

            function render(list) {
                // Calculate pagination
                const totalPages = Math.ceil(list.length / perPage);
                const startIndex = (currentPage - 1) * perPage;
                const endIndex = startIndex + perPage;
                const paginatedProducts = list.slice(startIndex, endIndex);
                
                // Render products
                const fragments = document.createDocumentFragment();
                paginatedProducts.forEach(product => {
                    const col = document.createElement('div');
                    col.className = 'col-6 col-md-4 col-lg-3';
                    col.innerHTML = createProductCard(product);
                    fragments.appendChild(col);
                });
                grid.innerHTML = '';
                grid.appendChild(fragments);
                initProductCards();
                initAnimations();
                
                // Update products info
                updateProductsInfo(startIndex + 1, Math.min(endIndex, list.length), list.length);
                
                // Render pagination
                renderPagination(currentPage, totalPages, list.length);
            }

            // Attach sorting and render first time
            attachProductsSorting(products, render);
            
            // Attach per-page filter
            attachPerPageFilter(products, render);
        })
        .catch(() => {
            grid.innerHTML = '<div class="col-12"><p class="text-center text-danger py-4 mb-0">Không thể tải sản phẩm. Vui lòng thử lại sau.</p></div>';
        });
}

// Render pagination
function renderPagination(currentPage, totalPages, totalProducts) {
    const paginationContainer = document.getElementById('products-pagination');
    if (!paginationContainer) return;
    
    if (totalPages <= 1) {
        paginationContainer.innerHTML = '';
        return;
    }
    
    let paginationHTML = '';
    
    // Previous button
    if (currentPage > 1) {
        paginationHTML += `<li class="page-item">
            <a class="page-link" href="#" data-page="${currentPage - 1}">Trước</a>
        </li>`;
    } else {
        paginationHTML += `<li class="page-item disabled">
            <a class="page-link" href="#" tabindex="-1">Trước</a>
        </li>`;
    }
    
    // Page numbers
    const startPage = Math.max(1, currentPage - 2);
    const endPage = Math.min(totalPages, currentPage + 2);
    
    if (startPage > 1) {
        paginationHTML += `<li class="page-item"><a class="page-link" href="#" data-page="1">1</a></li>`;
        if (startPage > 2) {
            paginationHTML += `<li class="page-item disabled"><span class="page-link">...</span></li>`;
        }
    }
    
    for (let i = startPage; i <= endPage; i++) {
        if (i === currentPage) {
            paginationHTML += `<li class="page-item active"><a class="page-link" href="#">${i}</a></li>`;
        } else {
            paginationHTML += `<li class="page-item"><a class="page-link" href="#" data-page="${i}">${i}</a></li>`;
        }
    }
    
    if (endPage < totalPages) {
        if (endPage < totalPages - 1) {
            paginationHTML += `<li class="page-item disabled"><span class="page-link">...</span></li>`;
        }
        paginationHTML += `<li class="page-item"><a class="page-link" href="#" data-page="${totalPages}">${totalPages}</a></li>`;
    }
    
    // Next button
    if (currentPage < totalPages) {
        paginationHTML += `<li class="page-item">
            <a class="page-link" href="#" data-page="${currentPage + 1}">Sau</a>
        </li>`;
    } else {
        paginationHTML += `<li class="page-item disabled">
            <a class="page-link" href="#" tabindex="-1">Sau</a>
        </li>`;
    }
    
    paginationContainer.innerHTML = paginationHTML;
    
    // Add click event listeners
    paginationContainer.addEventListener('click', function(e) {
        e.preventDefault();
        const pageLink = e.target.closest('a[data-page]');
        if (pageLink) {
            const page = parseInt(pageLink.dataset.page);
            updateURL({ page: page });
        }
    });
}

// Attach per-page filter
function attachPerPageFilter(products, renderCallback) {
    const perPageSelect = document.getElementById('products-per-page');
    const perPageSelectMobile = document.getElementById('products-per-page-mobile');
    
    // Set current value
    const urlParams = new URLSearchParams(window.location.search);
    const currentPerPage = parseInt(urlParams.get('per_page')) || 12;
    
    if (perPageSelect) {
        perPageSelect.value = currentPerPage;
        perPageSelect.addEventListener('change', function() {
            const newPerPage = parseInt(this.value);
            updateURL({ per_page: newPerPage, page: 1 }); // Reset to page 1
        });
    }
    
    if (perPageSelectMobile) {
        perPageSelectMobile.value = currentPerPage;
        perPageSelectMobile.addEventListener('change', function() {
            const newPerPage = parseInt(this.value);
            updateURL({ per_page: newPerPage, page: 1 }); // Reset to page 1
        });
    }
}

// Update products info display
function updateProductsInfo(showing, total) {
    const showingElement = document.getElementById('products-showing');
    const totalElement = document.getElementById('products-total');
    
    if (showingElement) showingElement.textContent = showing;
    if (totalElement) totalElement.textContent = total;
}

// Update URL with new parameters
function updateURL(params) {
    const url = new URL(window.location);
    Object.keys(params).forEach(key => {
        if (params[key]) {
            url.searchParams.set(key, params[key]);
        } else {
            url.searchParams.delete(key);
        }
    });
    window.location.href = url.toString();
}

// Sorting logic for products page
function attachProductsSorting(products, renderCallback) {
    const sortSelect = document.getElementById('products-sort');
    const sortSelectMobile = document.getElementById('products-sort-mobile');
    
    if (!sortSelect && !sortSelectMobile) return;

    const getOriginal = (p) => {
        const v = typeof p.original_price === 'number' ? p.original_price : parseFloat(p.original_price || '0');
        return isNaN(v) ? 0 : v;
    };
    const getDiscounted = (p) => {
        const v = typeof p.discounted_price === 'number' ? p.discounted_price : parseFloat(p.discounted_price || '0');
        return isNaN(v) ? 0 : v;
    };
    const getRating = (p) => {
        const v = typeof p.rating === 'number' ? p.rating : parseFloat(p.rating || '0');
        return isNaN(v) ? 0 : v;
    };
    const getSold = (p) => {
        const v = typeof p.sold_quantity === 'number' ? p.sold_quantity : parseFloat(p.sold_quantity || '0');
        return isNaN(v) ? 0 : v;
    };
    const getDiscountRate = (p) => {
        const r = typeof p.discount_rate === 'number' ? p.discount_rate : parseFloat(p.discount_rate || '0');
        if (!isNaN(r) && r > 0) return r;
        const o = getOriginal(p), d = getDiscounted(p);
        if (o > 0 && d >= 0 && d <= o) return ((o - d) / o) * 100;
        return 0;
    };

    function applySort() {
        const mode = (sortSelect && sortSelect.value) || (sortSelectMobile && sortSelectMobile.value) || 'newest';
        const sorted = [...products];
        sorted.sort((a, b) => {
            switch (mode) {
                case 'price_asc':
                    return getDiscounted(a) - getDiscounted(b);
                case 'price_desc':
                    return getDiscounted(b) - getDiscounted(a);
                case 'sales':
                    return getSold(b) - getSold(a);
                case 'discount':
                    return getDiscountRate(b) - getDiscountRate(a);
                case 'newest':
                default:
                    return (Number(b.id) || 0) - (Number(a.id) || 0);
            }
        });
        renderCallback(sorted);
    }

    if (sortSelect) {
    sortSelect.addEventListener('change', applySort);
    }
    if (sortSelectMobile) {
        sortSelectMobile.addEventListener('change', applySort);
    }
    
    // First run
    applySort();
}

// Init product detail page
defineProductDetailInit = (function(){
    function parseProductIdFromPath() {
        // Expect /product/<id>
        const parts = location.pathname.split('/').filter(Boolean);
        const idx = parts.indexOf('product');
        if (idx !== -1 && parts[idx+1]) return parts[idx+1];
        return null;
    }

    function setStars(container, rating) {
        if (!container) return;
        let html = '';
        const full = Math.floor(rating || 0);
        const half = (rating || 0) % 1 >= 0.5;
        for (let i=0;i<full;i++) html += '<i class="fas fa-star"></i>';
        if (half) html += '<i class="fas fa-star-half-alt"></i>';
        for (let i=full + (half?1:0); i<5; i++) html += '<i class="far fa-star"></i>';
        container.innerHTML = html;
    }

    // Fetch brand information from API
    async function fetchBrandInfo(brandName, descEl, description) {
        try {
            console.log('🔍 Fetching brand info for:', brandName);
            const response = await fetch('https://buddyskincare.pythonanywhere.com/brands/');
            if (response.ok) {
                const brands = await response.json();
                console.log('📦 Total brands found:', brands.length);
                
                // Try exact match first
                let brand = brands.find(b => b.name === brandName);
                
                // If not found, try case-insensitive match
                if (!brand) {
                    brand = brands.find(b => b.name.toLowerCase() === brandName.toLowerCase());
                }
                
                // If still not found, try partial match
                if (!brand) {
                    brand = brands.find(b => b.name.toLowerCase().includes(brandName.toLowerCase()) || 
                                           brandName.toLowerCase().includes(b.name.toLowerCase()));
                }
                
                console.log('🎯 Brand found:', brand);
                
                let brandInfo = '';
                if (brand) {
                    brandInfo += `<div class="alert alert-info mb-3">
                        <h6 class="fw-bold mb-2"><i class="fas fa-award me-2"></i>Thông tin thương hiệu</h6>
                        <p class="mb-1"><strong>Thương hiệu:</strong> ${brand.name}</p>`;
                    if (brand.country) brandInfo += `<p class="mb-1"><strong>Xuất xứ:</strong> ${brand.country}</p>`;
                    if (brand.introduction) {
                        brandInfo += `<p class="mb-0"><strong>Giới thiệu:</strong><br>${brand.introduction}</p>`;
                    }
                    brandInfo += `</div>`;
                } else {
                    console.log('❌ Brand not found:', brandName);
                    // Fallback if brand not found
                    brandInfo += `<div class="alert alert-info mb-3">
                        <h6 class="fw-bold mb-2"><i class="fas fa-award me-2"></i>Thông tin thương hiệu</h6>
                        <p class="mb-0"><strong>Thương hiệu:</strong> ${brandName}</p>
                    </div>`;
                }
                
                // Format description with line breaks for better readability
                if (description && description.length > 0) {
                    description = formatDescription(description);
                }
                
                descEl.innerHTML = brandInfo + description;
            } else {
                console.error('❌ API response not ok:', response.status);
                // Fallback if API fails
                let brandInfo = `<div class="alert alert-info mb-3">
                    <h6 class="fw-bold mb-2"><i class="fas fa-award me-2"></i>Thông tin thương hiệu</h6>
                    <p class="mb-0"><strong>Thương hiệu:</strong> ${brandName}</p>
                </div>`;
                
                if (description && description.length > 0) {
                    description = formatDescription(description);
                }
                
                descEl.innerHTML = brandInfo + description;
            }
        } catch (error) {
            console.error('❌ Error fetching brand info:', error);
            // Fallback if API fails
            let brandInfo = `<div class="alert alert-info mb-3">
                <h6 class="fw-bold mb-2"><i class="fas fa-award me-2"></i>Thông tin thương hiệu</h6>
                <p class="mb-0"><strong>Thương hiệu:</strong> ${brandName}</p>
            </div>`;
            
            if (description && description.length > 0) {
                description = formatDescription(description);
            }
            
            descEl.innerHTML = brandInfo + description;
        }
    }

    // Format description with line breaks
    function formatDescription(description) {
        if (!description || description.length === 0) return description;
        
        // Add line breaks after sentences ending with . ! ?
        description = description.replace(/([.!?])\s+/g, '$1<br><br>');
        
        // Add line breaks after commas in long sentences
        description = description.replace(/(,)\s+(?=\w{20,})/g, '$1<br>');
        
        // Add line breaks for bullet points or lists
        description = description.replace(/(\d+\.\s)/g, '<br>$1');
        description = description.replace(/([•·▪▫])\s/g, '<br>$1 ');
        
        // Clean up multiple line breaks
        description = description.replace(/(<br>){3,}/g, '<br><br>');
        
        return description;
    }

    function populateDetail(p) {
        console.log('🎯 populateDetail called with data:', p);
        console.log('📦 Product name:', p.name);
        console.log('💰 Product price:', p.sale_price || p.discounted_price);
        console.log('📊 Stock quantity:', p.stock_quantity);
        
        // Xử lý cả dữ liệu cũ (Flask demo) và mới (API)
        let imageUrl, brandName, original, discounted, rating, stock, soldQuantity;
        
        if (p.image && p.image.startsWith('http')) {
            // Dữ liệu mới từ API
            imageUrl = (p.image && String(p.image).trim()) || '/static/image/default-product.jpg';
            brandName = p.brand_name || (p.brand ? p.brand.name : '');
            original = typeof p.original_price === 'number' ? p.original_price * 1000 : null;
            discounted = typeof p.discounted_price === 'number' ? p.discounted_price * 1000 : null;
            rating = typeof p.rating === 'number' ? p.rating : (parseFloat(p.rating) || 0);
            stock = typeof p.stock_quantity === 'number' ? p.stock_quantity : 0;
            soldQuantity = typeof p.sold_quantity === 'number' ? p.sold_quantity : 0;
        } else {
            // Dữ liệu từ API PythonAnywhere
            imageUrl = (p.image && String(p.image).trim()) || '/static/image/default-product.jpg';
            brandName = p.brand_name || (p.brand ? p.brand.name : '');
            original = typeof p.original_price === 'number' ? p.original_price * 1000 : null;
            discounted = typeof p.discounted_price === 'number' ? p.discounted_price * 1000 : null;
            rating = typeof p.rating === 'number' ? p.rating : (parseFloat(p.rating) || 0);
            stock = typeof p.stock_quantity === 'number' ? p.stock_quantity : 0;
            soldQuantity = typeof p.sold_quantity === 'number' ? p.sold_quantity : 0;
        }

        console.log('🖼️ Setting image URL:', imageUrl);
        const mainImage = document.getElementById('mainImage');
        if (mainImage) {
            mainImage.src = imageUrl;
            console.log('✅ Main image updated');
        } else {
            console.log('❌ Main image element not found');
        }

        const thumbnailContainer = document.getElementById('thumbnailContainer');
        if (thumbnailContainer) {
            thumbnailContainer.innerHTML = '';
            // For now, just show the main image as thumbnail since we don't have album
                const el = document.createElement('img');
            el.src = imageUrl;
                el.alt = 'Thumbnail';
                el.className = 'img-thumbnail cursor-pointer';
                el.style.width = '80px';
                el.style.height = '80px';
                el.style.objectFit = 'cover';
            el.addEventListener('click', () => changeMainImage(imageUrl));
                thumbnailContainer.appendChild(el);
        }

        const nameEl = document.getElementById('detailName'); 
        if (nameEl) {
            nameEl.textContent = p.name || 'Sản phẩm';
            console.log('✅ Product name updated:', p.name);
        } else {
            console.log('❌ Product name element not found');
        }
        const brandEl = document.getElementById('detailBrand'); if (brandEl) brandEl.textContent = brandName;
        const brandFeatureEl = document.getElementById('detailBrandFeature'); if (brandFeatureEl) brandFeatureEl.textContent = brandName;
        setStars(document.getElementById('detailStars'), rating);
        const ratingEl = document.getElementById('detailRating'); if (ratingEl) ratingEl.textContent = (rating || 0).toFixed(1);
        const reviewsEl = document.getElementById('detailReviews'); if (reviewsEl) reviewsEl.textContent = `(${soldQuantity} đã bán)`;
        const stockEl = document.getElementById('detailStock'); if (stockEl) stockEl.textContent = stock > 0 ? `Còn ${stock} sản phẩm` : 'Hết hàng';
        
        // Handle out of stock state
        const isOutOfStock = stock <= 0;
        console.log('🔍 Stock check:', { stock, isOutOfStock });
        
        // Show/hide out of stock overlay
        const outOfStockOverlay = document.getElementById('outOfStockOverlay');
        console.log('🔍 Overlay element:', outOfStockOverlay);
        if (outOfStockOverlay) {
            outOfStockOverlay.style.setProperty('display', isOutOfStock ? 'flex' : 'none', 'important');
            console.log('🔍 Overlay display set to:', outOfStockOverlay.style.display);
        }
        
        // Apply grayscale filter to main image when out of stock
        if (mainImage) {
            mainImage.style.filter = isOutOfStock ? 'grayscale(100%)' : 'none';
        }
        
        // Update quantity input max attribute based on stock
        const quantityInput = document.getElementById('quantity');
        if (quantityInput) {
            quantityInput.max = stock > 0 ? stock : 1;
            if (parseInt(quantityInput.value) > stock && stock > 0) {
                quantityInput.value = stock;
            }
            // Disable quantity input when out of stock
            quantityInput.disabled = isOutOfStock;
        }
        
        // Disable quantity buttons when out of stock
        const quantityButtons = document.querySelectorAll('.quantity-section button');
        quantityButtons.forEach(btn => {
            btn.disabled = isOutOfStock;
        });
        
        // Disable add to cart button when out of stock
        const addToCartBtn = document.getElementById('detailAddToCartBtn');
        if (addToCartBtn) {
            addToCartBtn.disabled = isOutOfStock;
            if (isOutOfStock) {
                addToCartBtn.innerHTML = '<i class="fas fa-times me-2"></i>Hết hàng';
                addToCartBtn.classList.remove('btn-primary');
                addToCartBtn.classList.add('btn-secondary');
            } else {
                addToCartBtn.innerHTML = '<i class="fas fa-shopping-cart me-2"></i>Thêm vào giỏ hàng';
                addToCartBtn.classList.remove('btn-secondary');
                addToCartBtn.classList.add('btn-primary');
            }
            
            // Handle Buy Now button
            const buyNowBtn = document.getElementById('detailBuyNowBtn');
            if (buyNowBtn) {
                buyNowBtn.disabled = isOutOfStock;
                if (isOutOfStock) {
                    buyNowBtn.innerHTML = '<i class="fas fa-times me-2"></i>Hết hàng';
                    buyNowBtn.classList.remove('btn-success');
                    buyNowBtn.classList.add('btn-secondary');
                } else {
                    buyNowBtn.innerHTML = '<i class="fas fa-bolt me-2"></i>Mua ngay';
                    buyNowBtn.classList.remove('btn-secondary');
                    buyNowBtn.classList.add('btn-success');
                }
            }
        }

        const oEl = document.getElementById('detailOriginalPrice'); if (oEl && original) oEl.textContent = formatPrice(original);
        const dEl = document.getElementById('detailDiscountedPrice'); if (dEl && discounted) dEl.textContent = formatPrice(discounted);
        const badge = document.getElementById('detailDiscountBadge');
        if (badge && original && discounted && original > discounted) {
            // Check if product is flash sale
            const isFlashSale = isFlashSaleProduct(p);
            if (isFlashSale) {
            badge.style.display = '';
                badge.className = 'badge bg-warning text-dark';
                badge.innerHTML = '<i class="fas fa-bolt me-1"></i>FLASH SALE';
            } else {
                const rate = typeof p.discount_rate === 'number' 
                    ? Math.round(p.discount_rate) 
                    : Math.round(((original - discounted) / original) * 100);
                badge.style.display = '';
                badge.className = 'badge bg-danger';
            badge.textContent = `-${rate}%`;
            }
        }
        const saveEl = document.getElementById('detailSavings');
        if (saveEl && original && discounted) {
            const savings = original - discounted;
            saveEl.textContent = `Tiết kiệm: ${formatPrice(savings)}`;
        }

        const descEl = document.getElementById('detailDescription'); 
        if (descEl) {
            let description = p.description || 'Chưa có mô tả.';
            
            // Fetch brand information from API
            if (p.brand || p.brand_name) {
                const brandName = p.brand || p.brand_name;
                fetchBrandInfo(brandName, descEl, description);
            } else {
                // Format description with line breaks for better readability
                if (description && description.length > 0) {
                    description = formatDescription(description);
                }
                descEl.innerHTML = description;
            }
        }
        
        const specEl = document.getElementById('detailSpecifications'); 
        if (specEl) {
            // Create specifications from API data
            let specsHTML = '<div class="row">';
            
            // Xử lý dữ liệu từ API PythonAnywhere
            // Thông tin hãng
            if (p.brand) specsHTML += `<div class="col-md-6"><strong>Thương hiệu:</strong> ${p.brand}</div>`;
            if (p.origin) specsHTML += `<div class="col-md-6"><strong>Xuất xứ:</strong> ${p.origin}</div>`;
            if (p.manufacturer) specsHTML += `<div class="col-md-6"><strong>Nhà sản xuất:</strong> ${p.manufacturer}</div>`;
            if (p.sku) specsHTML += `<div class="col-md-6"><strong>Mã sản phẩm:</strong> ${p.sku}</div>`;
            
            // Thông tin sản phẩm
            if (p.volume) specsHTML += `<div class="col-md-6"><strong>Dung tích:</strong> ${p.volume}</div>`;
            if (p.unit) specsHTML += `<div class="col-md-6"><strong>Đơn vị:</strong> ${p.unit}</div>`;
            if (p.weight) specsHTML += `<div class="col-md-6"><strong>Trọng lượng:</strong> ${p.weight}</div>`;
            if (p.dimensions) specsHTML += `<div class="col-md-6"><strong>Kích thước:</strong> ${p.dimensions}</div>`;
            if (p.status) {
                const statusText = {
                    'new': 'Mới 100%',
                    'test': 'Đã test 1-2 lần',
                    '30': 'Còn 30%',
                    '50': 'Còn 50%',
                    '70': 'Còn 70%',
                    '80': 'Còn 80%',
                    '90': 'Còn 90%',
                    '95': 'Còn 95%',
                    'newmh': 'Mới nhưng mất hộp',
                    'newrt': 'Mới nhưng rách tem',
                    'newx': 'Mới nhưng hộp bị xước',
                    'chiet': 'Sản phẩm chiết'
                }[p.status] || p.status;
                specsHTML += `<div class="col-md-6"><strong>Tình trạng:</strong> ${statusText}</div>`;
            }
            if (p.ingredients) specsHTML += `<div class="col-12"><strong>Thành phần:</strong><br>${p.ingredients}</div>`;
            
            specsHTML += '</div>';
            specEl.innerHTML = specsHTML || 'Chưa có thông số.';
        }

        const crumb = document.getElementById('detailBreadcrumb'); if (crumb) crumb.textContent = p.name || '';
        const catEl = document.getElementById('detailCategory'); if (catEl) catEl.textContent = p.category?.name || 'Danh mục';

        // Display tags
        const tagsContainer = document.getElementById('detailTags');
        const tagsList = document.getElementById('detailTagsList');
        if (tagsContainer && tagsList && p.tags && p.tags.length > 0) {
            tagsContainer.style.display = '';
            tagsList.innerHTML = p.tags.map(tag => 
                `<span class="badge bg-primary me-2 mb-2">${tag.name || tag}</span>`
            ).join('');
        }

        // Display gifts
        const giftsContainer = document.getElementById('detailGifts');
        const giftsList = document.getElementById('detailGiftsList');
        if (giftsContainer && giftsList && p.gifts && p.gifts.length > 0) {
            giftsContainer.style.display = '';
            giftsList.innerHTML = p.gifts.map(gift => 
                `<div class="d-flex align-items-center mb-2">
                    <img src="${gift.image || '/static/image/default-product.jpg'}" 
                         alt="${gift.name}" 
                         class="me-2" 
                         style="width: 40px; height: 40px; object-fit: cover; border-radius: 4px;">
                    <div>
                        <div class="fw-semibold">${gift.name}</div>
                        <small class="text-muted">${gift.description || ''}</small>
                    </div>
                </div>`
            ).join('');
        }

        // Wire add to cart
        const addBtn = document.getElementById('detailAddToCartBtn');
        if (addBtn) {
            addBtn.addEventListener('click', () => {
                const qty = Math.max(1, parseInt(document.getElementById('quantity')?.value || '1', 10) || 1);
                const productPriceText = formatPrice(discounted || original || 0);
                addProductToCart(String(p.id), p.name, productPriceText, imageUrl, original ? formatPrice(original) : null, qty);
                const imgEl = document.getElementById('mainImage');
                flyToCart(imgEl, () => {
                    updateCartCount();
                });
            });
        }

        // Wishlist on detail page
        const favBtn = document.getElementById('detailFavBtn');
        if (favBtn) {
            // Prepare item payload
            const item = {
                id: String(p.id),
                name: p.name || '',
                image: imageUrl || '',
                brand: brandName || '',
                // Store price in VND for wishlist so drawer doesn't need to multiply
                price: (typeof p.discounted_price === 'number' ? p.discounted_price : (parseFloat(p.discounted_price || '0') || 0)) * 1000
            };
            const icon = favBtn.querySelector('i');
            const textEl = favBtn.querySelector('.fav-text');
            const syncState = () => {
                const map = getWishlist();
                const isFav = Boolean(map[item.id]);
                if (isFav) {
                    icon.classList.remove('far');
                    icon.classList.add('fas');
                    icon.style.color = '#ff4d6d';
                    favBtn.classList.remove('btn-outline-secondary');
                    favBtn.classList.add('btn-danger');
                    if (textEl) textEl.textContent = 'Đã trong yêu thích';
                } else {
                    icon.classList.remove('fas');
                    icon.classList.add('far');
                    icon.style.color = '';
                    favBtn.classList.remove('btn-danger');
                    favBtn.classList.add('btn-outline-secondary');
                    if (textEl) textEl.textContent = 'Thêm vào yêu thích';
                }
            };
            // Init state
            syncState();
            // Click handler (guard against duplicate binding)
            if (favBtn.dataset.bound !== '1') {
                favBtn.dataset.bound = '1';
                favBtn.addEventListener('click', (e) => {
                    e.preventDefault();
                    const added = toggleWishlist(item);
                    syncState();
                    if (added) {
                        showNotification('Đã thêm vào yêu thích', 'success');
                    } else {
                        showNotification('Đã bỏ khỏi yêu thích', 'info');
                    }
                });
            }
        }

        const buyBtn = document.getElementById('detailBuyNowBtn');
        if (buyBtn) {
            buyBtn.addEventListener('click', () => {
                const qty = parseInt(document.getElementById('quantity')?.value || '1', 10) || 1;
                const productPriceText = formatPrice(discounted || original || 0);
                addProductToCart(String(p.id), p.name, productPriceText, imageUrl, original ? formatPrice(original) : null);
                window.location.href = '/checkout';
            });
        }

        // Status bar if low stock
        if (stock <= 5 && stock >= 0) {
            const statusWrap = document.getElementById('detailStatus');
            const statusText = document.getElementById('detailStatusText');
            if (statusWrap && statusText) {
                statusWrap.style.display = '';
                statusText.innerHTML = `<strong>Chỉ còn ${stock} sản phẩm!</strong> Đặt hàng ngay để không bỏ lỡ.`;
            }
        }
    }

    function initProductDetailPage() {
        if (!document.getElementById('product-detail-page')) return;
        const id = parseProductIdFromPath();
        if (!id) return;
        
        // Kiểm tra xem có dữ liệu từ Flask template không
        const productData = window.productData;
        if (productData) {
            console.log('Using product data from Flask template:', productData);
            populateDetail(productData);
            return;
        }
        
        // Fallback: fetch từ API PythonAnywhere
        const apiUrl = `https://buddyskincare.pythonanywhere.com/products/${id}/`;
        console.log('Fetching product from API:', apiUrl);
        fetch(apiUrl)
            .then(r => r.ok ? r.json() : Promise.reject(new Error('Not found')))
            .then(populateDetail)
            .catch((error) => {
                console.error('API fetch failed:', error);
                showNotification('Không tìm thấy sản phẩm hoặc xảy ra lỗi khi tải dữ liệu.', 'error');
            });
    }

    return initProductDetailPage;
})();

// Helpers to mark required fields visually without alert
function markInvalidField(fieldEl, message = 'Vui lòng điền thông tin này', styles) {
    if (!fieldEl) return;
    fieldEl.classList.add('is-invalid');
    // Ensure feedback node exists
    let feedback = fieldEl.parentElement?.querySelector('.invalid-feedback');
    if (!feedback) {
        feedback = document.createElement('div');
        feedback.className = 'invalid-feedback';
        fieldEl.parentElement && fieldEl.parentElement.appendChild(feedback);
    }
    feedback.textContent = message;
    if (styles && typeof styles === 'object') {
        Object.assign(feedback.style, styles);
    }
}
function clearInvalidField(fieldEl) {
    if (!fieldEl) return;
    fieldEl.classList.remove('is-invalid');
    const feedback = fieldEl.parentElement?.querySelector('.invalid-feedback');
    if (feedback) feedback.textContent = '';
}

// Global delegated handler as a fallback to ensure place order always fires on checkout
document.addEventListener('click', function(e) {
    const btn = e.target.closest('#place-order-btn, [data-place-order], button[name="place-order"]');
    if (!btn) return;
    if (document.querySelector('input[name="pay"]')) {
        e.preventDefault();
        console.log('[Checkout] Place order click captured (delegated).');
        handlePlaceOrder();
    }
});

// Helper: show success order modal
function showOrderSuccessModal(onOk) {
    let modalEl = document.getElementById('orderSuccessModal');
    if (!modalEl) {
        modalEl = document.createElement('div');
        modalEl.id = 'orderSuccessModal';
        modalEl.className = 'modal fade';
        modalEl.tabIndex = -1;
        // Prevent closing by backdrop/ESC
        modalEl.setAttribute('data-bs-backdrop', 'static');
        modalEl.setAttribute('data-bs-keyboard', 'false');
        modalEl.innerHTML = `
        <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content border-0 shadow-lg">
                <div class="modal-header border-0">
                    <h5 class="modal-title fw-bold">
                        <i class="fas fa-check-circle text-success me-2"></i>
                        Đơn hàng đã được đặt thành công
                    </h5>
                </div>
                <div class="modal-body pt-0">
                    <div class="text-center py-2">
                        <div class="display-6 text-success mb-2"><i class="fas fa-bag-shopping"></i></div>
                        <p class="mb-0"> Vui lòng chờ nhân viên xác nhận đơn hàng.</p>
                        <p class="text-muted mb-0">Cảm ơn bạn đã luôn tin tưởng chúng tôi!</p>
                    </div>
                </div>
                <div class="modal-footer border-0">
                    <button type="button" class="btn btn-light text-dark border border-success" id="orderSuccessOkBtn" style="padding: 8px 16px;">Quay lại trang chủ</button>
                </div>
            </div>
        </div>`;
        document.body.appendChild(modalEl);
    } else {
        // Ensure attributes are applied if modal already exists
        modalEl.setAttribute('data-bs-backdrop', 'static');
        modalEl.setAttribute('data-bs-keyboard', 'false');
    }
    const okBtn = modalEl.querySelector('#orderSuccessOkBtn');
    const modal = bootstrap.Modal.getOrCreateInstance(modalEl, { backdrop: 'static', keyboard: false });
    const cleanup = () => {
        okBtn && okBtn.removeEventListener('click', handleOk);
        modalEl && modalEl.removeEventListener('hidden.bs.modal', cleanup);
    };
    const handleOk = () => {
        cleanup();
        modal.hide();
        if (typeof onOk === 'function') onOk();
    };
    okBtn && okBtn.addEventListener('click', handleOk);
    modalEl && modalEl.addEventListener('hidden.bs.modal', cleanup);
    modal.show();
}

// Initialize related products on product detail page
function initRelatedProducts() {
    if (!document.getElementById('product-detail-page')) return;
    const container = document.getElementById('related-products-container');
    if (!container) return;

    // Build API: fetch a list (we'll randomize client-side) then slice 10
    const apiUrl = 'https://buddyskincare.pythonanywhere.com/products/';

    fetch(apiUrl)
        .then(r => r.ok ? r.json() : Promise.reject(new Error('API error')))
        .then(list => {
            if (!Array.isArray(list) || list.length === 0) {
                container.innerHTML = '<p class="text-center text-muted">Không có sản phẩm liên quan.</p>';
                return;
            }
            // Shuffle and take up to 10
            const shuffled = list.sort(() => Math.random() - 0.5).slice(0, 10);

            // Create carousel like homepage
            const wrapper = document.createElement('div');
            wrapper.className = 'position-relative';
            wrapper.style.overflow = 'hidden';
            wrapper.style.padding = '10px 40px';

            const track = document.createElement('div');
            track.className = 'related-track d-flex';
            track.style.gap = '16px';
            track.style.transition = 'transform .4s ease';
            track.dataset.index = '0';
            track.dataset.perView = '5';

            shuffled.forEach(p => {
                const item = document.createElement('div');
                item.className = 'slider-item';
                item.style.flex = '0 0 auto';
                item.innerHTML = createProductCard(p);
                track.appendChild(item);
            });

            wrapper.appendChild(track);
            container.innerHTML = '';
            container.appendChild(wrapper);

            // Nav buttons
            if (shuffled.length > 5) {
                const left = document.createElement('button');
                left.className = 'btn btn-light position-absolute';
                left.style.cssText = 'z-index:10;border-radius:50%;width:40px;height:40px;box-shadow:0 4px 10px rgba(0,0,0,.2);top:40%;left:10px;transform:translateY(-50%);';
                left.innerHTML = '<i class="fas fa-chevron-left"></i>';
                const right = document.createElement('button');
                right.className = 'btn btn-light position-absolute';
                right.style.cssText = 'z-index:10;border-radius:50%;width:40px;height:40px;box-shadow:0 4px 10px rgba(0,0,0,.2);top:40%;right:10px;transform:translateY(-50%);';
                right.innerHTML = '<i class="fas fa-chevron-right"></i>';
                wrapper.appendChild(left);
                wrapper.appendChild(right);

                const relayout = () => {
                    const per = window.innerWidth <= 576 ? 2 : (window.innerWidth <= 768 ? 3 : 5);
                    track.dataset.perView = String(per);
                    const containerWidth = wrapper.clientWidth - 20 * 2; // approximate side paddings
                    const gap = 16;
                    const itemWidth = Math.floor((containerWidth - gap * (per - 1)) / per);
                    track.querySelectorAll('.slider-item').forEach(it => { it.style.width = itemWidth + 'px'; });
                };
                const navigate = dir => {
                    const per = parseInt(track.dataset.perView || '5', 10);
                    const current = parseInt(track.dataset.index || '0', 10);
                    const maxIndex = Math.max(0, shuffled.length - per);
                    const next = Math.max(0, Math.min(maxIndex, current + (dir === 'left' ? -1 : 1)));
                    if (next === current) return;
                    track.dataset.index = String(next);
                    const first = track.querySelector('.slider-item');
                    const step = (first ? first.offsetWidth : 0) + 16;
                    track.style.transform = `translateX(${-next * step}px)`;
                };
                left.addEventListener('click', () => navigate('left'));
                right.addEventListener('click', () => navigate('right'));
                window.addEventListener('resize', () => { relayout(); navigate('left'); navigate('right'); });
                relayout();
            }

            // Re-init for newly added cards
            initProductCards();
            initAnimations();
        })
        .catch(() => {
            container.innerHTML = '<p class="text-center text-danger">Không thể tải sản phẩm liên quan.</p>';
        });
}

// Global function to initialize product detail page
window.initProductDetailPageGlobal = function() {
    console.log('🔍 initProductDetailPageGlobal called');
    
    if (!document.getElementById('product-detail-page')) {
        console.log('❌ product-detail-page element not found');
        return;
    }
    
    const id = parseProductIdFromPath();
    if (!id) {
        console.log('❌ Product ID not found in URL');
        return;
    }
    
    console.log('✅ Product ID found:', id);
    
    // Kiểm tra xem có dữ liệu từ Flask template không
    const productData = window.productData;
    if (productData) {
        console.log('✅ Using product data from Flask template:', productData);
        console.log('📦 Product name:', productData.name);
        console.log('💰 Product price:', productData.sale_price);
        
        try {
            populateDetail(productData);
            console.log('✅ populateDetail called successfully');
        } catch (error) {
            console.error('❌ Error in populateDetail:', error);
        }
        return;
    }
    
    console.log('⚠️ No product data from Flask template, trying API...');
    
    // Fallback: fetch từ API PythonAnywhere
    const apiUrl = `https://buddyskincare.pythonanywhere.com/products/${id}/`;
    console.log('Fetching product from API:', apiUrl);
    fetch(apiUrl)
        .then(r => r.ok ? r.json() : Promise.reject(new Error('Not found')))
        .then(populateDetail)
        .catch((error) => {
            console.error('API fetch failed:', error);
            showNotification('Không tìm thấy sản phẩm hoặc xảy ra lỗi khi tải dữ liệu.', 'error');
        });
};

// Initialize product detail page when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Initialize product detail page if we're on a product detail page
    if (document.getElementById('product-detail-page')) {
        console.log('Initializing product detail page...');
        window.initProductDetailPageGlobal();
    }
});

// Cache bust: 1757233662

// Function to send new order notification to admin
async function notifyAdminNewOrder(orderId) {
    try {
        console.log(`[Order Notification] Sending notification for order ${orderId}`);
        
        const response = await fetch('/api/send-new-order-notification', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ order_id: orderId })
        });
        
        if (response.ok) {
            const result = await response.json();
            console.log('[Order Notification] Email sent successfully:', result);
            return result;
        } else {
            const errorData = await response.json();
            console.error('[Order Notification] Failed to send email:', errorData);
            throw new Error(errorData.message || 'Failed to send notification email');
        }
    } catch (error) {
        console.error('[Order Notification] Error:', error);
        throw error;
    }
}
