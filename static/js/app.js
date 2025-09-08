// API Base URL
const API_BASE = '/api';

// Auth utilities
class Auth {
    static getToken() {
        return localStorage.getItem('accessToken');
    }
    
    static setToken(token) {
        localStorage.setItem('accessToken', token);
    }
    
    static removeToken() {
        localStorage.removeItem('accessToken');
        localStorage.removeItem('currentUser');
    }
    
    static getUser() {
        const userStr = localStorage.getItem('currentUser');
        return userStr ? JSON.parse(userStr) : null;
    }
    
    static setUser(user) {
        localStorage.setItem('currentUser', JSON.stringify(user));
    }
    
    static isLoggedIn() {
        return !!this.getToken();
    }
    
    static async getCurrentUser() {
        // First try to get user from localStorage
        const storedUser = this.getUser();
        if (storedUser) return storedUser;
        
        // Fallback to decoding JWT token
        const token = this.getToken();
        if (!token) return null;
        
        try {
            const payload = JSON.parse(atob(token.split('.')[1]));
            return payload;
        } catch (error) {
            console.error('Error decoding token:', error);
            return null;
        }
    }
}

// Image management utilities
class ImageManager {
    static async checkPersonalizedImage(productId) {
        if (!Auth.isLoggedIn()) return null;
        
        try {
            console.log(`Checking personalized image for product ${productId}`);
            const response = await fetch(`${API_BASE}/products/${productId}/personalized-image`, {
                headers: {
                    'Authorization': `Bearer ${Auth.getToken()}`
                }
            });
            
            if (response.ok) {
                const result = await response.json();
                console.log(`Check result for product ${productId}:`, result);
                return result;
            } else {
                console.log(`Failed to check personalized image for product ${productId}:`, response.status, response.statusText);
            }
        } catch (error) {
            console.error('Error checking personalized image:', error);
        }
        return null;
    }
    
    static async triggerImageGeneration(productId) {
        if (!Auth.isLoggedIn()) return null;
        
        try {
            const response = await fetch(`${API_BASE}/products/${productId}/generate-personalized-image`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${Auth.getToken()}`,
                    'Content-Type': 'application/json'
                }
            });
            
            if (response.ok) {
                return await response.json();
            }
        } catch (error) {
            console.error('Error triggering image generation:', error);
        }
        return null;
    }
    
    static setupImageHover(productImageElement, originalUrl, personalizedUrl) {
        if (!personalizedUrl) return;
        
        // Store URLs in dataset for reliable access
        productImageElement.dataset.originalUrl = originalUrl;
        productImageElement.dataset.personalizedUrl = personalizedUrl;
        
        // Remove existing event listeners to prevent duplicates
        const newElement = productImageElement.cloneNode(true);
        productImageElement.parentNode.replaceChild(newElement, productImageElement);
        
        newElement.addEventListener('mouseenter', () => {
            if (newElement.dataset.originalUrl) {
                newElement.src = newElement.dataset.originalUrl;
            }
        });
        
        newElement.addEventListener('mouseleave', () => {
            if (newElement.dataset.personalizedUrl) {
                newElement.src = newElement.dataset.personalizedUrl;
            }
        });
        
        return newElement;
    }
    
    static async setupPersonalizedImage(productId, productImageElement) {
        console.log(`Setting up personalized image for product ${productId}`);
        
        // Store the original URL before any changes
        if (!productImageElement.dataset.originalUrl) {
            productImageElement.dataset.originalUrl = productImageElement.src;
        }
        
        const imageInfo = await this.checkPersonalizedImage(productId);
        console.log(`Initial image info for product ${productId}:`, imageInfo);
        
        if (!imageInfo) {
            console.log(`No image info available for product ${productId}`);
            return;
        }
        
        const originalUrl = productImageElement.dataset.originalUrl;
        
        if (imageInfo.has_personalized_image) {
            // Use personalized image as main, show original on hover
            console.log(`Using existing personalized image for product ${productId}: ${imageInfo.personalized_image_url}`);
            const cacheBustedUrl = imageInfo.personalized_image_url + '?t=' + Date.now();
            
            // Mark as personalized to prevent reversion
            productImageElement.dataset.isPersonalized = 'true';
            productImageElement.dataset.personalizedUrl = imageInfo.personalized_image_url;
            
            productImageElement.src = cacheBustedUrl;
            const updatedElement = this.setupImageHover(productImageElement, originalUrl, imageInfo.personalized_image_url);
            
            // Add a visual indicator
            this.addPersonalizedIndicator(updatedElement || productImageElement);
        } else if (imageInfo.is_generating) {
            // Show generating indicator and poll for completion, but don't change image if already personalized
            console.log(`Image is generating for product ${productId}, starting to poll`);
            if (productImageElement.dataset.isPersonalized !== 'true') {
                this.addGeneratingIndicator(productImageElement);
            }
            this.pollForPersonalizedImage(productId, productImageElement, originalUrl);
        } else if (imageInfo.ready_for_personalization) {
            // No personalized image exists - trigger generation
            console.log(`Triggering personalized image generation for product ${productId}`);
            
            const generationResult = await this.triggerImageGeneration(productId);
            console.log(`Generation trigger result for product ${productId}:`, generationResult);
            
            if (generationResult && generationResult.status === 'generation_started') {
                // Show generating indicator and start polling, but don't change image if already personalized
                console.log(`Generation started for product ${productId}, adding indicator and starting poll`);
                if (productImageElement.dataset.isPersonalized !== 'true') {
                    this.addGeneratingIndicator(productImageElement);
                }
                this.pollForPersonalizedImage(productId, productImageElement, originalUrl);
            } else if (generationResult && generationResult.status === 'already_exists') {
                // Image was generated between checks
                console.log(`Image already exists for product ${productId}: ${generationResult.personalized_image_url}`);
                const cacheBustedUrl = generationResult.personalized_image_url + '?t=' + Date.now();
                
                // Mark as personalized
                productImageElement.dataset.isPersonalized = 'true';
                productImageElement.dataset.personalizedUrl = generationResult.personalized_image_url;
                
                productImageElement.src = cacheBustedUrl;
                const updatedElement = this.setupImageHover(productImageElement, originalUrl, generationResult.personalized_image_url);
                this.addPersonalizedIndicator(updatedElement || productImageElement);
            }
        }
    }
    
    static addPersonalizedIndicator(imageElement) {
        const container = imageElement.parentElement;
        if (container.querySelector('.personalized-indicator')) return;
        
        const indicator = document.createElement('div');
        indicator.className = 'personalized-indicator';
        indicator.innerHTML = '✨ Personalized';
        indicator.style.cssText = `
            position: absolute;
            top: 8px;
            right: 8px;
            background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
            color: white;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
            z-index: 10;
            pointer-events: none;
        `;
        
        container.style.position = 'relative';
        container.appendChild(indicator);
    }
    
    static addGeneratingIndicator(imageElement) {
        const container = imageElement.parentElement;
        if (container.querySelector('.generating-indicator')) return;
        
        const indicator = document.createElement('div');
        indicator.className = 'generating-indicator';
        indicator.innerHTML = '🎨 Generating...';
        indicator.style.cssText = `
            position: absolute;
            top: 8px;
            right: 8px;
            background: rgba(0, 0, 0, 0.8);
            color: white;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
            z-index: 10;
            pointer-events: none;
            animation: pulse 2s infinite;
        `;
        
        container.style.position = 'relative';
        container.appendChild(indicator);
    }
    
    static removeIndicators(imageElement) {
        const container = imageElement.parentElement;
        const indicators = container.querySelectorAll('.personalized-indicator, .generating-indicator');
        indicators.forEach(indicator => indicator.remove());
    }
    
    static async pollForPersonalizedImage(productId, imageElement, originalUrl) {
        const maxAttempts = 30; // Poll for up to 1 minute
        let attempts = 0;
        
        const poll = async () => {
            attempts++;
            console.log(`Polling attempt ${attempts} for product ${productId}`);
            
            const imageInfo = await this.checkPersonalizedImage(productId);
            console.log(`Poll result for product ${productId}:`, imageInfo);
            
            if (imageInfo && imageInfo.has_personalized_image) {
                // Image is ready!
                console.log(`Image ready for product ${productId}, updating src to: ${imageInfo.personalized_image_url}`);
                this.removeIndicators(imageElement);
                
                // Add cache busting parameter to force reload
                const cacheBustedUrl = imageInfo.personalized_image_url + '?t=' + Date.now();
                
                // Mark as personalized
                imageElement.dataset.isPersonalized = 'true';
                imageElement.dataset.personalizedUrl = imageInfo.personalized_image_url;
                
                imageElement.src = cacheBustedUrl;
                
                const updatedElement = this.setupImageHover(imageElement, originalUrl, imageInfo.personalized_image_url);
                this.addPersonalizedIndicator(updatedElement || imageElement);
                
                // Force image reload
                (updatedElement || imageElement).onload = () => {
                    console.log(`Image successfully loaded for product ${productId}`);
                };
                
                return;
            }
            
            if (attempts < maxAttempts && (imageInfo && (imageInfo.is_generating || imageInfo.ready_for_personalization))) {
                // Continue polling
                console.log(`Continue polling for product ${productId}, attempt ${attempts}/${maxAttempts}`);
                setTimeout(poll, 2000); // Poll every 2 seconds
            } else {
                // Stop polling and remove indicator
                console.log(`Stopped polling for product ${productId} after ${attempts} attempts`);
                this.removeIndicators(imageElement);
            }
        };
        
        setTimeout(poll, 1000); // Start polling after 1 second (reduced from 2)
    }
}

// API utilities
class API {
    static async request(endpoint, options = {}) {
        const url = `${API_BASE}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };
        
        // Add auth token if available
        const token = Auth.getToken();
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        
        try {
            const response = await fetch(url, config);
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.detail || 'API request failed');
            }
            
            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }
    
    static async get(endpoint) {
        return this.request(endpoint);
    }
    
    static async post(endpoint, data) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }
}

// UI utilities
class UI {
    static showAlert(message, type = 'error') {
        // Remove any existing alerts
        const existingAlerts = document.querySelectorAll('.alert');
        existingAlerts.forEach(alert => alert.remove());
        
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type}`;
        alertDiv.textContent = message;
        
        // Append to body for fixed positioning
        document.body.appendChild(alertDiv);
        
        // Remove after 5 seconds
        setTimeout(() => {
            alertDiv.remove();
        }, 5000);
    }
    
    static showLoading(element) {
        element.innerHTML = '<div class="loading"></div>';
        element.disabled = true;
    }
    
    static hideLoading(element, originalText) {
        element.innerHTML = originalText;
        element.disabled = false;
    }
}

// Password strength checker
async function checkPasswordStrength(password) {
    if (!password) return null;
    
    try {
        const response = await fetch(`${API_BASE}/auth/check-password`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `password=${encodeURIComponent(password)}`
        });
        
        return await response.json();
    } catch (error) {
        console.error('Error checking password strength:', error);
        return null;
    }
}

// Update navigation based on auth status
function updateNavigation() {
    const userActions = document.querySelector('.user-actions');
    if (!userActions) return;
    
    if (Auth.isLoggedIn()) {
        Auth.getCurrentUser().then(user => {
            if (user) {
                const avatarSrc = user.image ? user.image : '';
                const avatarHTML = user.image 
                    ? `<img src="${user.image}" alt="${user.name}" class="user-avatar-img" onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';">`
                    : '';
                const fallbackAvatar = `<div class="user-avatar-fallback">${user.name ? user.name.charAt(0).toUpperCase() : 'U'}</div>`;
                
                userActions.innerHTML = `
                    <div class="user-info">
                        <div class="user-avatar">
                            ${avatarHTML}
                            ${fallbackAvatar}
                        </div>
                        <span class="user-name">Welcome, ${user.name || 'User'}</span>
                        <button class="btn btn-logout" onclick="logout()">Logout</button>
                    </div>
                `;
            }
        });
    } else {
        userActions.innerHTML = `
            <a href="/login" class="btn">Login</a>
            <a href="/signup" class="btn btn-primary">Sign Up</a>
        `;
    }
}

// Logout function
function logout() {
    Auth.removeToken();
    updateNavigation();
    window.location.href = '/';
}

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
    updateNavigation();
});

// Product utilities
class ProductManager {
    static async loadProducts(gender = null, category = null) {
        try {
            let endpoint = '/products/';
            const params = new URLSearchParams();
            
            if (gender) params.append('gender', gender);
            if (category) params.append('category', category);
            
            if (params.toString()) {
                endpoint += '?' + params.toString();
            }
            
            return await API.get(endpoint);
        } catch (error) {
            console.error('Error loading products:', error);
            UI.showAlert('Failed to load products');
            return [];
        }
    }
    
    static async getProduct(id) {
        try {
            return await API.get(`/products/${id}`);
        } catch (error) {
            console.error('Error loading product:', error);
            UI.showAlert('Product not found');
            return null;
        }
    }
    
    static renderProductCard(product) {
        const cardId = `product-card-${product.id}`;
        return `
            <div class="product-card" onclick="viewProduct(${product.id})" id="${cardId}">
                <img src="${product.image}" 
                     alt="${product.name}" 
                     class="product-image" 
                     id="product-image-${product.id}"
                     onerror="this.src='/static/images/placeholder.jpg'">
                <div class="product-info">
                    <div class="product-category">${product.category}</div>
                    <div class="product-name">${product.name}</div>
                    <div class="product-price">$${product.price}</div>
                </div>
            </div>
        `;
    }
    
    static renderProductGrid(products, containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;
        
        if (products.length === 0) {
            container.innerHTML = '<p style="text-align: center; color: #666;">No products found.</p>';
            return;
        }
        
        const productHTML = products.map(product => this.renderProductCard(product)).join('');
        container.innerHTML = productHTML;
        
        // Setup personalized images for logged-in users
        if (Auth.isLoggedIn()) {
            products.forEach(product => {
                const imageElement = document.getElementById(`product-image-${product.id}`);
                if (imageElement) {
                    ImageManager.setupPersonalizedImage(product.id, imageElement);
                }
            });
        }
    }
}

// Navigate to product page
function viewProduct(productId) {
    window.location.href = `/product/${productId}`;
}

// Form validation utilities
class FormValidator {
    static validateEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }
    
    static validatePassword(password) {
        return password.length >= 8;
    }
    
    static validateRequired(value) {
        return value && value.trim().length > 0;
    }
}

// Hero Image Slider
let currentSlideIndex = 0;
const slides = document.querySelectorAll('.slide');
const dots = document.querySelectorAll('.dot');
const totalSlides = slides.length;

function showSlide(index) {
    // Hide all slides
    slides.forEach(slide => slide.classList.remove('active'));
    dots.forEach(dot => dot.classList.remove('active'));
    
    // Show current slide
    if (slides[index]) {
        slides[index].classList.add('active');
    }
    if (dots[index]) {
        dots[index].classList.add('active');
    }
}

function nextSlide() {
    currentSlideIndex = (currentSlideIndex + 1) % totalSlides;
    showSlide(currentSlideIndex);
}

function previousSlide() {
    currentSlideIndex = (currentSlideIndex - 1 + totalSlides) % totalSlides;
    showSlide(currentSlideIndex);
}

function currentSlide(index) {
    currentSlideIndex = index - 1; // Convert from 1-based to 0-based index
    showSlide(currentSlideIndex);
}

// Auto-slide functionality
function initializeSlider() {
    if (slides.length > 0) {
        // Start auto-sliding every 5 seconds
        setInterval(nextSlide, 5000);
        
        // Add keyboard navigation
        document.addEventListener('keydown', function(event) {
            if (event.key === 'ArrowLeft') {
                previousSlide();
            } else if (event.key === 'ArrowRight') {
                nextSlide();
            }
        });
    }
}

// Initialize slider when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeSlider();
});
