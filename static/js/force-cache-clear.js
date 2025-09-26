// Force Cache Clear Script
// This script will force clear all caches and reload the page

(function() {
    'use strict';
    
    console.log('Force Cache Clear Script loaded');
    
    // Clear all possible caches
    if ('caches' in window) {
        caches.keys().then(function(names) {
            for (let name of names) {
                caches.delete(name);
                console.log('Deleted cache:', name);
            }
        });
    }
    
    // Clear localStorage
    try {
        localStorage.clear();
        console.log('Cleared localStorage');
    } catch (e) {
        console.log('Could not clear localStorage:', e);
    }
    
    // Clear sessionStorage
    try {
        sessionStorage.clear();
        console.log('Cleared sessionStorage');
    } catch (e) {
        console.log('Could not clear sessionStorage:', e);
    }
    
    // Force reload with cache busting
    if (window.location.search.indexOf('force-clear') === -1) {
        console.log('Force clearing cache and reloading...');
        window.location.href = window.location.href + (window.location.search ? '&' : '?') + 'force-clear=' + Date.now();
    }
})();