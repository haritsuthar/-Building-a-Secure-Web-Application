"""
Utility functions for Building a Secure Web Application
Security helpers, validation functions, and common utilities
"""

import re
import secrets
import hashlib
from datetime import datetime, timezone
from functools import wraps
from flask import request, jsonify, current_app
import jwt


class SecurityUtils:
    """Security utility functions"""
    
    @staticmethod
    def generate_secure_token(length=32):
        """Generate a cryptographically secure random token"""
        return secrets.token_urlsafe(length)
    
    @staticmethod
    def hash_data(data, salt=None):
        """Hash data with optional salt using SHA-256"""
        if salt is None:
            salt = secrets.token_hex(16)
        
        combined = f"{data}{salt}".encode('utf-8')
        hashed = hashlib.sha256(combined).hexdigest()
        return f"{hashed}:{salt}"
    
    @staticmethod
    def verify_hash(data, hashed_data):
        """Verify hashed data"""
        try:
            hash_part, salt = hashed_data.split(':')
            return SecurityUtils.hash_data(data, salt) == hashed_data
        except ValueError:
            return False
    
    @staticmethod
    def sanitize_input(input_string):
        """Sanitize user input to prevent XSS"""
        if not isinstance(input_string, str):
            return input_string
        
        # Remove potentially dangerous characters
        sanitized = re.sub(r'[<>"\']', '', input_string)
        return sanitized.strip()
    
    @staticmethod
    def validate_email(email):
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_password_strength(password):
        """Check password strength and return score and feedback"""
        score = 0
        feedback = []
        
        if len(password) >= 8:
            score += 25
        else:
            feedback.append("Use at least 8 characters")
        
        if len(password) >= 12:
            score += 25
        
        if re.search(r'[a-z]', password):
            score += 12.5
        else:
            feedback.append("Add lowercase letters")
        
        if re.search(r'[A-Z]', password):
            score += 12.5
        else:
            feedback.append("Add uppercase letters")
        
        if re.search(r'\d', password):
            score += 12.5
        else:
            feedback.append("Add numbers")
        
        if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            score += 12.5
        else:
            feedback.append("Add special characters")
        
        strength_level = "weak"
        if score >= 75:
            strength_level = "strong"
        elif score >= 50:
            strength_level = "medium"
        
        return {
            'score': min(score, 100),
            'level': strength_level,
            'feedback': feedback
        }


class RateLimiter:
    """Simple in-memory rate limiter"""
    
    def __init__(self):
        self.requests = {}
    
    def is_allowed(self, key, limit=5, window=300):
        """Check if request is allowed based on rate limit"""
        now = datetime.now(timezone.utc).timestamp()
        
        if key not in self.requests:
            self.requests[key] = []
        
        # Remove old requests outside the window
        self.requests[key] = [
            req_time for req_time in self.requests[key] 
            if now - req_time < window
        ]
        
        # Check if limit exceeded
        if len(self.requests[key]) >= limit:
            return False
        
        # Add current request
        self.requests[key].append(now)
        return True


class JWTUtils:
    """JWT utility functions"""
    
    @staticmethod
    def create_token(payload, secret_key, expiration_hours=2):
        """Create a JWT token"""
        payload['exp'] = datetime.now(timezone.utc).timestamp() + (expiration_hours * 3600)
        return jwt.encode(payload, secret_key, algorithm='HS256')
    
    @staticmethod
    def decode_token(token, secret_key):
        """Decode and validate JWT token"""
        try:
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])
            return payload, None
        except jwt.ExpiredSignatureError:
            return None, "Token has expired"
        except jwt.InvalidTokenError:
            return None, "Invalid token"
    
    @staticmethod
    def extract_token_from_header(auth_header):
        """Extract token from Authorization header"""
        if not auth_header:
            return None
        
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return None
        
        return parts[1]


def rate_limit(limit=5, window=300):
    """Decorator for rate limiting endpoints"""
    limiter = RateLimiter()
    
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Use IP address as key
            key = request.remote_addr
            
            if not limiter.is_allowed(key, limit, window):
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'message': f'Maximum {limit} requests per {window} seconds'
                }), 429
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def log_security_event(event_type, details, user_id=None):
    """Log security events for monitoring"""
    timestamp = datetime.now(timezone.utc).isoformat()
    
    log_entry = {
        'timestamp': timestamp,
        'event_type': event_type,
        'details': details,
        'user_id': user_id,
        'ip_address': request.remote_addr if request else None,
        'user_agent': request.headers.get('User-Agent') if request else None
    }
    
    # In production, this would write to a proper logging system
    current_app.logger.info(f"SECURITY_EVENT: {log_entry}")
    
    return log_entry


def validate_input_length(value, min_length=1, max_length=255):
    """Validate input length"""
    if not isinstance(value, str):
        return False
    
    length = len(value.strip())
    return min_length <= length <= max_length


def escape_html(text):
    """Escape HTML characters to prevent XSS"""
    if not isinstance(text, str):
        return text
    
    escape_chars = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#x27;',
        '/': '&#x2F;'
    }
    
    for char, escaped in escape_chars.items():
        text = text.replace(char, escaped)
    
    return text