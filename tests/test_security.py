"""
Security-focused tests for Building a Secure Web Application
"""

import unittest
from utils import SecurityUtils, JWTUtils, RateLimiter
import secrets


class TestSecurityUtils(unittest.TestCase):
    """Test security utility functions"""
    
    def test_generate_secure_token(self):
        """Test secure token generation"""
        token1 = SecurityUtils.generate_secure_token()
        token2 = SecurityUtils.generate_secure_token()
        
        # Tokens should be different
        self.assertNotEqual(token1, token2)
        
        # Token should be URL-safe
        self.assertTrue(token1.replace('-', '').replace('_', '').isalnum())
    
    def test_password_strength_validation(self):
        """Test password strength validation"""
        # Weak password
        weak_result = SecurityUtils.validate_password_strength("123")
        self.assertEqual(weak_result['level'], 'weak')
        self.assertTrue(len(weak_result['feedback']) > 0)
        
        # Strong password
        strong_result = SecurityUtils.validate_password_strength("MySecure123!")
        self.assertEqual(strong_result['level'], 'strong')
        self.assertEqual(len(strong_result['feedback']), 0)
    
    def test_email_validation(self):
        """Test email validation"""
        # Valid emails
        self.assertTrue(SecurityUtils.validate_email("test@example.com"))
        self.assertTrue(SecurityUtils.validate_email("user.name@domain.co.uk"))
        
        # Invalid emails
        self.assertFalse(SecurityUtils.validate_email("invalid-email"))
        self.assertFalse(SecurityUtils.validate_email("@domain.com"))
        self.assertFalse(SecurityUtils.validate_email("user@"))
    
    def test_input_sanitization(self):
        """Test input sanitization"""
        # Test XSS prevention
        malicious_input = "<script>alert('xss')</script>"
        sanitized = SecurityUtils.sanitize_input(malicious_input)
        self.assertNotIn('<script>', sanitized)
        self.assertNotIn('</script>', sanitized)
        
        # Test normal input preservation
        normal_input = "Hello World 123"
        sanitized_normal = SecurityUtils.sanitize_input(normal_input)
        self.assertEqual(normal_input, sanitized_normal)


class TestJWTUtils(unittest.TestCase):
    """Test JWT utility functions"""
    
    def setUp(self):
        self.secret_key = secrets.token_hex(32)
        self.test_payload = {'user_id': 123, 'username': 'testuser'}
    
    def test_token_creation_and_decoding(self):
        """Test JWT token creation and decoding"""
        # Create token
        token = JWTUtils.create_token(self.test_payload.copy(), self.secret_key)
        self.assertIsInstance(token, str)
        
        # Decode token
        decoded_payload, error = JWTUtils.decode_token(token, self.secret_key)
        self.assertIsNone(error)
        self.assertEqual(decoded_payload['user_id'], 123)
        self.assertEqual(decoded_payload['username'], 'testuser')
    
    def test_invalid_token_handling(self):
        """Test handling of invalid tokens"""
        # Test with wrong secret
        token = JWTUtils.create_token(self.test_payload.copy(), self.secret_key)
        wrong_secret = secrets.token_hex(32)
        
        decoded_payload, error = JWTUtils.decode_token(token, wrong_secret)
        self.assertIsNone(decoded_payload)
        self.assertIsNotNone(error)
        self.assertIn("Invalid token", error)
    
    def test_token_header_extraction(self):
        """Test token extraction from Authorization header"""
        # Valid Bearer token
        valid_header = "Bearer abc123def456"
        token = JWTUtils.extract_token_from_header(valid_header)
        self.assertEqual(token, "abc123def456")
        
        # Invalid format
        invalid_header = "Basic abc123def456"
        token = JWTUtils.extract_token_from_header(invalid_header)
        self.assertIsNone(token)
        
        # No header
        token = JWTUtils.extract_token_from_header(None)
        self.assertIsNone(token)


class TestRateLimiter(unittest.TestCase):
    """Test rate limiting functionality"""
    
    def setUp(self):
        self.limiter = RateLimiter()
    
    def test_rate_limiting(self):
        """Test basic rate limiting functionality"""
        key = "test_user"
        limit = 3
        
        # First 3 requests should be allowed
        for i in range(limit):
            self.assertTrue(self.limiter.is_allowed(key, limit, 300))
        
        # 4th request should be denied
        self.assertFalse(self.limiter.is_allowed(key, limit, 300))
    
    def test_different_keys(self):
        """Test that different keys have separate limits"""
        limit = 2
        
        # Use up limit for key1
        self.assertTrue(self.limiter.is_allowed("key1", limit, 300))
        self.assertTrue(self.limiter.is_allowed("key1", limit, 300))
        self.assertFalse(self.limiter.is_allowed("key1", limit, 300))
        
        # key2 should still be allowed
        self.assertTrue(self.limiter.is_allowed("key2", limit, 300))
        self.assertTrue(self.limiter.is_allowed("key2", limit, 300))


if __name__ == '__main__':
    unittest.main()