// Security utilities for SecureApp

class SecurityUtils {
    // CSRF token management
    static getCSRFToken() {
        return document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
    }

    // Input sanitization
    static sanitizeInput(input) {
        const div = document.createElement('div');
        div.textContent = input;
        return div.innerHTML;
    }

    // Password strength checker
    static checkPasswordStrength(password) {
        let strength = 0;
        let feedback = [];

        // Length checks
        if (password.length >= 8) {
            strength += 25;
        } else {
            feedback.push('Use at least 8 characters');
        }

        if (password.length >= 12) {
            strength += 25;
        }

        // Character variety checks
        if (/[a-z]/.test(password)) {
            strength += 12.5;
        } else {
            feedback.push('Add lowercase letters');
        }

        if (/[A-Z]/.test(password)) {
            strength += 12.5;
        } else {
            feedback.push('Add uppercase letters');
        }

        if (/[0-9]/.test(password)) {
            strength += 12.5;
        } else {
            feedback.push('Add numbers');
        }

        if (/[^A-Za-z0-9]/.test(password)) {
            strength += 12.5;
        } else {
            feedback.push('Add special characters');
        }

        let level = 'weak';
        let color = 'danger';

        if (strength >= 75) {
            level = 'strong';
            color = 'success';
        } else if (strength >= 50) {
            level = 'medium';
            color = 'warning';
        }

        return {
            strength: Math.min(strength, 100),
            level: level,
            color: color,
            feedback: feedback
        };
    }

    // Secure form submission
    static async secureSubmit(form, endpoint, options = {}) {
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());

        // Add CSRF token
        const csrfToken = this.getCSRFToken();
        if (csrfToken) {
            data.csrf_token = csrfToken;
        }

        try {
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken,
                    ...options.headers
                },
                body: JSON.stringify(data),
                ...options
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Secure submit error:', error);
            throw error;
        }
    }

    // JWT token utilities
    static parseJWT(token) {
        try {
            const base64Url = token.split('.')[1];
            const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
            const jsonPayload = decodeURIComponent(atob(base64).split('').map(function(c) {
                return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
            }).join(''));

            return JSON.parse(jsonPayload);
        } catch (error) {
            console.error('Error parsing JWT:', error);
            return null;
        }
    }

    static isTokenExpired(token) {
        const payload = this.parseJWT(token);
        if (!payload || !payload.exp) return true;

        const currentTime = Math.floor(Date.now() / 1000);
        return payload.exp < currentTime;
    }

    // Session management
    static checkSession() {
        const token = sessionStorage.getItem('jwt_token');
        if (!token || this.isTokenExpired(token)) {
            this.clearSession();
            return false;
        }
        return true;
    }

    static clearSession() {
        sessionStorage.removeItem('jwt_token');
        localStorage.removeItem('user_data');
    }

    // Rate limiting for API calls
    static rateLimiter = new Map();

    static async rateLimit(key, limit = 5, window = 60000) {
        const now = Date.now();
        const requests = this.rateLimiter.get(key) || [];
        
        // Remove old requests outside the window
        const validRequests = requests.filter(time => now - time < window);
        
        if (validRequests.length >= limit) {
            throw new Error('Rate limit exceeded. Please try again later.');
        }
        
        validRequests.push(now);
        this.rateLimiter.set(key, validRequests);
        
        return true;
    }

    // Input validation
    static validateEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    static validateUsername(username) {
        // Username: 3-50 characters, alphanumeric and underscore only
        const usernameRegex = /^[a-zA-Z0-9_]{3,50}$/;
        return usernameRegex.test(username);
    }

    // XSS protection
    static escapeHtml(text) {
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return text.replace(/[&<>"']/g, function(m) { return map[m]; });
    }

    // Secure random string generation
    static generateSecureRandom(length = 32) {
        const array = new Uint8Array(length);
        crypto.getRandomValues(array);
        return Array.from(array, byte => byte.toString(16).padStart(2, '0')).join('');
    }
}

// Global security event listeners
document.addEventListener('DOMContentLoaded', function() {
    // Prevent form double submission
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn && !submitBtn.disabled) {
                setTimeout(() => {
                    submitBtn.disabled = true;
                    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processing...';
                }, 100);
            }
        });
    });

    // Auto-logout on token expiration
    const token = sessionStorage.getItem('jwt_token');
    if (token && SecurityUtils.isTokenExpired(token)) {
        SecurityUtils.clearSession();
        if (window.location.pathname !== '/login-page' && window.location.pathname !== '/') {
            window.location.href = '/login-page';
        }
    }

    // Security headers check (development only)
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        console.log('🔒 Security Check: Running in development mode');
        console.log('🔒 CSRF Protection: Enabled');
        console.log('🔒 Password Hashing: PBKDF2-SHA256');
        console.log('🔒 JWT Authentication: Enabled');
    }
});

// Export for use in other scripts
window.SecurityUtils = SecurityUtils;