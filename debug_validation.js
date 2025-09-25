// Debug script to test validation logic
console.log('🔍 Debug Validation Script Loaded');

// Test function to check validation logic
function debugValidation() {
    console.log('🔍 Starting validation debug...');
    
    const formRoot = document.getElementById('checkoutForm') || document;
    console.log('Form root:', formRoot);
    
    // Clear previous invalid states
    formRoot.querySelectorAll('.is-invalid').forEach(el => clearInvalidField(el));

    // Prefer explicit known fields
    const explicitIds = ['fullName','phone','shippingAddress'];
    console.log('[Checkout Debug] Explicit IDs:', explicitIds);
    let requiredEls = explicitIds
        .map(id => formRoot.querySelector(`#${id}`) || formRoot.querySelector(`[name="${id}"]`))
        .filter(Boolean);
    console.log('[Checkout Debug] Required elements found:', requiredEls.map(el => el.id || el.name));

    // Fallback to generic required markers if explicit not found
    if (requiredEls.length === 0) {
        console.log('[Checkout Debug] Using fallback - no explicit elements found');
        const fallbackEls = Array.from(formRoot.querySelectorAll('[required], .checkout-required'));
        console.log('[Checkout Debug] Fallback elements found:', fallbackEls.map(el => el.id || el.name));
        requiredEls = fallbackEls
            .filter(el => el.type !== 'email' && !/email/i.test(el.name || el.id || '') && !/ghi chu|note|message/i.test(el.name || el.id || ''));
        console.log('[Checkout Debug] Fallback elements after filter:', requiredEls.map(el => el.id || el.name));
    }

    // Check if city is included
    const cityIncluded = requiredEls.some(el => el.id === 'city');
    console.log('❌ City included in validation:', cityIncluded);
    
    if (cityIncluded) {
        console.error('🚨 BUG: City field is still being validated as required!');
    } else {
        console.log('✅ GOOD: City field is NOT being validated as required');
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

    console.log('Validation result:', hasInvalid ? 'FAILED' : 'PASSED');
    return !hasInvalid;
}

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

// Make functions globally available
window.debugValidation = debugValidation;

console.log('✅ Debug functions loaded. Run debugValidation() to test.');