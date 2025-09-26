// API Configuration
const API_CONFIG = {
    BASE_URL: (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') 
        ? 'http://localhost:8000' 
        : 'https://buddyskincare.vn/backend/api',
    ENDPOINTS: {
        collaborators: '/collaborators/',
        customer: '/customer/',
        brands: '/brands/',
        category: '/category/',
        tags: '/tags/',
        gifts: '/gifts/',
        products: '/products/',
        adminProducts: '/admin/api/products',
        vouchers: '/vouchers/',
        orders: '/orders/',
        orderItems: '/order-items/',
        latestProducts: '/latest-products/',
        carts: '/carts/',
        blog: '/blog/',
        admin: '/admin/',
        analytics: '/analytics/',
        luckyEvents: '/lucky-events/',
        luckyParticipants: '/lucky-participants/',
        luckyWinners: '/lucky-winners/',
        ctvApplications: '/ctv-applications/',
        ctvLevels: '/ctv-levels/',
        ctvs: '/ctvs/',
        ctvWithdrawals: '/ctv-withdrawals/',
        customerLeads: '/customer-leads/',
        marketingResources: '/marketing-resources/'
    }
};

// Helper function to get full API URL
function getApiUrl(endpoint) {
    return API_CONFIG.BASE_URL + API_CONFIG.ENDPOINTS[endpoint];
}

// Helper function to get full API URL with custom path
function getApiUrlWithPath(endpoint, path = '') {
    return API_CONFIG.BASE_URL + API_CONFIG.ENDPOINTS[endpoint] + path;
}
// Helper function to get base API URL
function getApiBaseUrl() {
    return API_CONFIG.BASE_URL;
}
