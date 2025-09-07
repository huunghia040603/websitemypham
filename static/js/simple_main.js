// Simple version of main.js for testing
console.log('🚀 Simple main.js loaded');

// Test function
function initFlashSaleProducts() {
    console.log('🚀 Initializing Flash Sale products...');
    const flashSaleApiUrl = '/api/products?tags=FlashSale';
    const containerSelector = '#flash-sale-products';
    
    console.log('📡 Flash Sale API URL:', flashSaleApiUrl);
    console.log('🎯 Container selector:', containerSelector);
    
    const container = document.querySelector(containerSelector);
    if (!container) {
        console.error('❌ Container not found:', containerSelector);
        return;
    }
    console.log('✅ Container found:', container);

    fetch(flashSaleApiUrl)
        .then(response => {
            console.log('📡 Response status:', response.status);
            return response.json();
        })
        .then(products => {
            console.log(`✅ Loaded ${products.length} products:`, products.slice(0, 2));
            
            if (products.length === 0) {
                container.innerHTML = '<p>No products found</p>';
                return;
            }

            container.innerHTML = products.slice(0, 6).map(product => `
                <div class="col-lg-2 col-md-4 col-sm-6 mb-4">
                    <div class="card h-100 product-card">
                        <img src="${product.image}" class="card-img-top" alt="${product.name}" style="height: 200px; object-fit: cover;">
                        <div class="card-body d-flex flex-column">
                            <h6 class="card-title">${product.name}</h6>
                            <p class="card-text text-danger fw-bold">${product.discounted_price}đ</p>
                            <button class="btn btn-primary mt-auto">Thêm vào giỏ</button>
                        </div>
                    </div>
                </div>
            `).join('');
            
            console.log('✅ Products rendered successfully!');
        })
        .catch(error => {
            console.error('❌ Error loading products:', error);
            container.innerHTML = '<p class="text-danger">Error loading products</p>';
        });
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 DOM loaded, initializing simple version...');
    const flashContainer = document.querySelector('#flash-sale-products');
    console.log('🎯 Flash Sale container found:', flashContainer);
    
    initFlashSaleProducts();
    console.log('✅ Simple initialization completed');
});