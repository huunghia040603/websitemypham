// Admin Dashboard JavaScript
// Auto-detect environment and set appropriate API base  
const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' 
    ? 'http://localhost:8000' 
    : 'https://buddyskincare.vn/backend/api';
const FLASK_API_BASE = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' 
    ? 'http://localhost:8000' 
    : 'https://buddyskincare.vn'; // Remove /backend/api for Flask routes

// AdminAPI Object
const AdminAPI = {
    // Orders
    async getOrders() {
        const response = await fetch(`${FLASK_API_BASE}/orders`);
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        return await response.json();
    },
    
    async getOrder(orderId) {
        const response = await fetch(`${FLASK_API_BASE}/orders/${orderId}`);
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        return await response.json();
    },
    
    async confirmOrder(orderId) {
        const response = await fetch(`${FLASK_API_BASE}/orders/${orderId}/confirm`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        return await response.json();
    },
    
    async cancelOrder(orderId) {
        const response = await fetch(`${FLASK_API_BASE}/orders/${orderId}/cancel`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        return await response.json();
    },
    
    // Products
    async getProducts() {
        const response = await fetch(`${FLASK_API_BASE}/admin/api/products`);
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        return await response.json();
    },
    
    async updateProduct(productId, data) {
        const response = await fetch(`${FLASK_API_BASE}/admin/api/products/${productId}`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        return await response.json();
    },
    
    async deleteProduct(productId) {
        const response = await fetch(`${FLASK_API_BASE}/admin/api/products/${productId}`, {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' }
        });
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        return await response.json();
    },
    
    // Customers
    async getCustomers() {
        const response = await fetch(`${FLASK_API_BASE}/customer`);
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        return await response.json();
    },
    
    // Utility functions
    formatPrice,
    formatDate,
    showNotification,
    
    // Analytics
    async getAnalytics(period='month') {
        // Extract cache busting parameter if present
        const [basePeriod, cacheParam] = period.split('?t=');
        const actualPeriod = basePeriod || period;
        
        const response = await fetch(`${API_BASE_URL}/analytics/${actualPeriod}`);
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        return await response.json();
    },

    async computeAnalytics(period='month', start=null, end=null) {
        const payload = { period };
        if (start) payload.start = start; if (end) payload.end = end;
        const response = await fetch(`${API_BASE_URL}/analytics/compute/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        return await response.json();
    },
    
    // Alias functions for compatibility
    fetchProducts: function() { return this.getProducts(); },
    fetchOrders: function() { return this.getOrders(); },
    fetchCustomers: function() { return this.getCustomers(); },
    addProduct: function(data) { return this.updateProduct(null, data); },
    updateOrder: function(orderId, data) { return this.getOrder(orderId); },
    updateCustomer: function(customerId, data) { return this.getCustomers(); },
    showLoading: function() { return Promise.resolve(); }
};

// Utility Functions
function formatPrice(price) {
    if (typeof price === 'number') {
        return new Intl.NumberFormat('vi-VN', {
            style: 'currency',
            currency: 'VND'
        }).format(price * 1000);
    }
    if (typeof price === 'string') {
        const numPrice = parseFloat(price);
        if (!isNaN(numPrice)) {
            return new Intl.NumberFormat('vi-VN', {
                style: 'currency',
                currency: 'VND'
            }).format(numPrice * 1000);
        }
    }
    return '0đ';
}

function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('vi-VN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function showNotification(message, type = 'info') {
    const alertClass = {
        'success': 'alert-success-admin',
        'error': 'alert-danger-admin',
        'warning': 'alert-warning-admin',
        'info': 'alert-info'
    }[type] || 'alert-info';

    // Create notification element
    const notification = document.createElement('div');
    notification.className = `alert ${alertClass} alert-dismissible fade show notification-fixed`;
    notification.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'} me-2"></i>
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

function showLoading(containerId) {
    const container = document.getElementById(containerId);
    if (container) {
        container.innerHTML = `
            <div class="loading-spinner show">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p class="mt-2 text-muted">Đang tải dữ liệu...</p>
            </div>
        `;
    }
}

// Product Management Functions
async function fetchProducts(status = null, flashSale = false) {
    try {
        let url = `${FLASK_API_BASE}/admin/api/products`;
        const params = new URLSearchParams();
        
        if (status) {
            params.append('status', status);
        }
        if (flashSale) {
            params.append('discount_rate__gt', '0');
        }
        
        if (params.toString()) {
            url += `?${params.toString()}`;
        }

        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('Error fetching products:', error);
        showNotification('Lỗi khi tải danh sách sản phẩm: ' + error.message, 'error');
        return [];
    }
}

async function addProduct(data) {
    try {
        console.log('🔧 Adding new product with data:', data);
        
        const response = await fetch(`${FLASK_API_BASE}/admin/api/products`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });

        console.log(`📡 Response status: ${response.status}`);
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
            console.error('❌ API Error:', errorData);
            throw new Error(`HTTP ${response.status}: ${errorData.error || 'Unknown error'}`);
        }

        const result = await response.json();
        console.log('✅ Add successful:', result);
        return result;
    } catch (error) {
        console.error('Error adding product:', error);
        showNotification('Lỗi khi thêm sản phẩm: ' + error.message, 'error');
        throw error;
    }
}

async function updateProduct(productId, data) {
    try {
        console.log(`🔧 Updating product ${productId} with data:`, data);
        
        const response = await fetch(`${FLASK_API_BASE}/admin-products/${productId}`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });

        console.log(`📡 Response status: ${response.status}`);
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
            console.error('❌ API Error:', errorData);
            throw new Error(`HTTP ${response.status}: ${errorData.error || 'Unknown error'}`);
        }

        const result = await response.json();
        console.log('✅ Update successful:', result);
        return result;
    } catch (error) {
        console.error('Error updating product:', error);
        showNotification('Lỗi khi cập nhật sản phẩm: ' + error.message, 'error');
        throw error;
    }
}

// Order Management Functions
async function fetchOrders() {
    try {
        const response = await fetch(`${FLASK_API_BASE}/orders`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('Error fetching orders:', error);
        showNotification('Lỗi khi tải danh sách đơn hàng: ' + error.message, 'error');
        return [];
    }
}

async function updateOrder(orderId, data) {
    try {
        const response = await fetch(`${FLASK_API_BASE}/admin/api/orders/${orderId}`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error('Error updating order:', error);
        showNotification('Lỗi khi cập nhật đơn hàng: ' + error.message, 'error');
        throw error;
    }
}

async function confirmOrder(orderId) {
    try {
        const response = await fetch(`${FLASK_API_BASE}/orders/${orderId}/confirm`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            if (response.status === 503) {
                showNotification(errorData.error || 'Tính năng xác nhận đơn hàng tạm thời không khả dụng. Vui lòng liên hệ quản trị viên.', 'warning');
            } else {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return;
        }

        const result = await response.json();
        showNotification(result.message || 'Đã xác nhận đơn hàng thành công', 'success');
        
        // Reload orders to update UI
        if (typeof loadOrders === 'function') {
            await loadOrders();
        }
        
        return result;
    } catch (error) {
        console.error('Error confirming order:', error);
        showNotification('Lỗi khi xác nhận đơn hàng: ' + error.message, 'error');
        throw error;
    }
}

async function cancelOrder(orderId) {
    try {
        const response = await fetch(`${FLASK_API_BASE}/orders/${orderId}/cancel`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            if (response.status === 503) {
                showNotification(errorData.error || 'Tính năng hủy đơn hàng tạm thời không khả dụng. Vui lòng liên hệ quản trị viên.', 'warning');
            } else {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return;
        }

        const result = await response.json();
        showNotification(result.message || 'Đã hủy đơn hàng và khôi phục số lượng tồn kho', 'success');
        
        // Reload orders to update UI
        if (typeof loadOrders === 'function') {
            await loadOrders();
        }
        
        return result;
    } catch (error) {
        console.error('Error cancelling order:', error);
        showNotification('Lỗi khi hủy đơn hàng: ' + error.message, 'error');
        throw error;
    }
}

// Initialize admin dashboard
document.addEventListener('DOMContentLoaded', function() {
    // Add fade-in animation to cards
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
        card.classList.add('fade-in');
    });

    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});

// Customer Management Functions
async function fetchCustomers() {
    try {
        const response = await fetch(`${FLASK_API_BASE}/customer`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('Error fetching customers:', error);
        showNotification('Lỗi khi tải danh sách khách hàng: ' + error.message, 'error');
        return [];
    }
}

async function updateCustomer(customerId, data) {
    try {
        console.log('🔧 Updating customer', customerId, 'with data:', data);
        const response = await fetch(`${FLASK_API_BASE}/customer/${customerId}`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        console.log(`📡 Response status: ${response.status}`);
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
            console.error('❌ API Error:', errorData);
            throw new Error(`HTTP ${response.status}: ${errorData.error || 'Unknown error'}`);
        }
        const result = await response.json();
        console.log('✅ Update successful:', result);
        return result;
    } catch (error) {
        console.error('Error updating customer:', error);
        showNotification('Lỗi khi cập nhật khách hàng: ' + error.message, 'error');
        throw error;
    }
}

// Export AdminAPI to window for global access
window.AdminAPI = AdminAPI;